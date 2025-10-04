import uuid
import time
from datetime import datetime
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException

from utils.document_processor import DocumentProcessor
from utils.text_chunker import TextChunker, TextChunk
from utils.schema_ import DocumentUploadResponse, DocumentInfo, ChunkInfo
from utils.metadata_storage import MetadataStorage
from vectordb.chroma_store import ChromaStore

class DocumentService:
    def __init__(self, chroma_store: ChromaStore):
        self.chroma_store = chroma_store
        self.document_processor = DocumentProcessor()
        self.text_chunker = TextChunker(chunk_size=800, overlap_size=100)
        self.metadata_storage = MetadataStorage()  # File-based metadata storage
        self.documents_metadata = {}  # In-memory cache for document metadata
        self._load_documents_metadata()  # Load existing metadata from file
    
    def _load_documents_metadata(self):
        """Load document metadata from file storage."""
        try:
            # Load from file-based storage
            all_docs = self.metadata_storage.get_all_documents()
            for doc in all_docs:
                self.documents_metadata[doc["document_id"]] = doc
            
            print(f"📚 Loaded {len(self.documents_metadata)} documents from metadata file")
            
        except Exception as e:
            print(f"⚠️  Error loading document metadata: {e}")
    
    def _store_document_metadata(self, document_id: str, document_name: str, upload_date: datetime, total_chunks: int, total_characters: int, file_type: str):
        """Store document metadata in ChromaDB for persistence."""
        try:
            # Create a special metadata entry for the document
            metadata_entry = {
                "document_id": document_id,
                "document_name": document_name,
                "upload_date": upload_date.isoformat(),
                "total_chunks": total_chunks,
                "total_characters": total_characters,
                "file_type": file_type,
                "type": "document_metadata"  # Special type to identify metadata entries
            }
            
            # Store as a special entry in ChromaDB
            self.chroma_store.collection.add(
                ids=[f"doc_meta_{document_id}"],
                documents=[f"Document metadata for {document_name}"],
                metadatas=[metadata_entry]
            )
            
        except Exception as e:
            print(f"⚠️  Error storing document metadata: {e}")
    
    async def process_document(self, file: UploadFile) -> DocumentUploadResponse:
        """
        Process uploaded document: extract text, chunk, and store in vector database.
        """
        start_time = time.time()
        
        try:
            # Validate file format
            if not self.document_processor.is_supported_format(file.filename):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format. Supported formats: {self.document_processor.supported_formats}"
                )
            
            # Read file content
            file_content = await file.read()
            if len(file_content) == 0:
                raise HTTPException(status_code=400, detail="Empty file")
            
            # Extract text with page information for PDFs
            extracted_text, page_info = self.document_processor.extract_text_with_page_info(file_content, file.filename)
            cleaned_text = self.document_processor.clean_text(extracted_text)
            
            if not cleaned_text.strip():
                raise HTTPException(status_code=400, detail="No text content found in document")
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Create chunks with page information
            chunks = self._create_chunks_with_page_info(
                text=cleaned_text,
                document_id=document_id,
                document_name=file.filename,
                page_info=page_info
            )
            
            if not chunks:
                raise HTTPException(status_code=400, detail="No valid chunks created from document")
            
            # Prepare chunks for storage
            chunk_texts = []
            chunk_metadatas = []
            chunk_ids = []
            
            for chunk in chunks:
                chunk_id = f"{document_id}_chunk_{chunk.chunk_index}"
                chunk_texts.append(chunk.text)
                chunk_metadatas.append({
                    "document_id": document_id,
                    "document_name": file.filename,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "page_number": chunk.page_number,
                    "file_type": file.filename.split('.')[-1].lower(),
                    "upload_date": datetime.now().isoformat()
                })
                chunk_ids.append(chunk_id)
            
            # Store in vector database
            self.chroma_store.add_texts(
                texts=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            # Store document metadata
            upload_date = datetime.now()
            self.documents_metadata[document_id] = {
                "document_id": document_id,
                "document_name": file.filename,
                "upload_date": upload_date,
                "total_chunks": len(chunks),
                "total_characters": len(cleaned_text),
                "file_type": file.filename.split('.')[-1].lower()
            }
            
            # Store document metadata in file storage for persistence
            self.metadata_storage.add_document(
                document_id, 
                file.filename, 
                len(chunks), 
                len(cleaned_text), 
                file.filename.split('.')[-1].lower()
            )
            
            processing_time = time.time() - start_time
            
            return DocumentUploadResponse(
                document_id=document_id,
                document_name=file.filename,
                chunks_created=len(chunks),
                total_characters=len(cleaned_text),
                processing_time=processing_time,
                success=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    def _create_chunks_with_page_info(self, text: str, document_id: str, document_name: str, page_info: list) -> List[TextChunk]:
        """Create chunks with page information for better metadata."""
        chunks = self.text_chunker.create_chunks(
            text=text,
            document_id=document_id,
            document_name=document_name
        )
        
        # Add page number information for PDFs
        if page_info:
            for chunk in chunks:
                # Find which page this chunk belongs to
                chunk_midpoint = (chunk.start_char + chunk.end_char) // 2
                for page in page_info:
                    if page['start_char'] <= chunk_midpoint <= page['end_char']:
                        chunk.page_number = page['page_number']
                        break
        
        return chunks
    
    def get_document_list(self) -> List[DocumentInfo]:
        """Get list of all uploaded documents."""
        documents = []
        for doc_id, metadata in self.documents_metadata.items():
            documents.append(DocumentInfo(
                document_id=metadata["document_id"],
                document_name=metadata["document_name"],
                upload_date=metadata["upload_date"],
                total_chunks=metadata["total_chunks"],
                total_characters=metadata["total_characters"],
                file_type=metadata["file_type"]
            ))
        return documents
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document and all its chunks."""
        if document_id not in self.documents_metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get all chunk IDs for this document
        chunk_ids = []
        for i in range(self.documents_metadata[document_id]["total_chunks"]):
            chunk_ids.append(f"{document_id}_chunk_{i}")
        
        # Add metadata ID to deletion list
        chunk_ids.append(f"doc_meta_{document_id}")
        
        # Delete chunks and metadata from vector database
        try:
            self.chroma_store.collection.delete(ids=chunk_ids)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting chunks: {str(e)}")
        
        # Remove document metadata from memory and file storage
        del self.documents_metadata[document_id]
        self.metadata_storage.delete_document(document_id)
        
        return {
            "status": "success",
            "message": f"Document '{document_id}' and all its chunks deleted successfully",
            "chunks_deleted": len(chunk_ids)
        }
    
    def get_document_chunks(self, document_id: str) -> List[ChunkInfo]:
        """Get all chunks for a specific document."""
        if document_id not in self.documents_metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Query vector database for chunks of this document
        try:
            results = self.chroma_store.collection.get(
                where={"document_id": document_id}
            )
            
            chunks = []
            for i, (chunk_id, text, metadata) in enumerate(zip(
                results["ids"], 
                results["documents"], 
                results["metadatas"]
            )):
                chunks.append(ChunkInfo(
                    chunk_id=chunk_id,
                    text=text,
                    chunk_index=metadata.get("chunk_index", i),
                    total_chunks=metadata.get("total_chunks", 0),
                    document_id=metadata.get("document_id", document_id),
                    document_name=metadata.get("document_name", ""),
                    start_char=metadata.get("start_char", 0),
                    end_char=metadata.get("end_char", len(text)),
                    page_number=metadata.get("page_number")
                ))
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x.chunk_index)
            return chunks
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving document chunks: {str(e)}")
