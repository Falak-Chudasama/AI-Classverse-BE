from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from utils.schema_ import (
    EmbedRequest, SearchRequest, DeleteRequest, 
    DocumentUploadResponse, DocumentListResponse, ChunkInfo
)
import chromadb
from chromadb.config import Settings
from vectordb.chroma_store import ChromaStore
from services.document_service import DocumentService
import time

app = FastAPI(title="AI Classroom Embedding Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with persistent storage
chroma_store = ChromaStore()
document_service = DocumentService(chroma_store)

# Use the same collection for consistency
collection = chroma_store.collection

@app.get("/")
def index():
    return {"status": "ChromaDB context engine is live."}

@app.get("/get-all")
def get_all_documents():
    try:
        # Use chroma_store collection for consistency
        results = chroma_store.collection.get()
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        ids = results.get("ids", [])

        formatted = [
            {"id": id_, "text": doc, "metadata": meta}
            for id_, doc, meta in zip(ids, documents, metadatas)
        ]

        return {"count": len(formatted), "data": formatted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed")
def embed_text(req: EmbedRequest):
    texts = req.content if isinstance(req.content, list) else [req.content]
    metadatas = (
        req.metadata if isinstance(req.metadata, list)
        else [req.metadata] * len(texts) if req.metadata else [{} for _ in texts]
    )
    
    # Use chroma_store for consistent embedding model
    ids = chroma_store.add_texts(texts, metadatas)
    return {"message": f"{len(ids)} item(s) embedded successfully.", "ids": ids, "success": True}

@app.post("/search")
def search_text(req: SearchRequest):
    try:
        # Use chroma_store for consistent embedding model
        results = chroma_store.search(req.query, req.k)
        
        # Handle results from chroma_store
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]
        
        # Filter by document_id if specified
        if req.document_id:
            filtered_results = []
            for i, (doc, meta, dist, chunk_id) in enumerate(zip(documents, metadatas, distances, ids)):
                if meta.get("document_id") == req.document_id:
                    filtered_results.append({
                        "id": chunk_id,
                        "text": doc, 
                        "metadata": meta, 
                        "distance": dist,
                        "document_id": meta.get("document_id"),
                        "document_name": meta.get("document_name"),
                        "chunk_index": meta.get("chunk_index")
                    })
            return {
                "results": filtered_results,
                "query": req.query,
                "total_results": len(filtered_results),
                "document_filter": req.document_id
            }
        else:
            return {
                "results": [
                    {
                        "id": chunk_id,
                        "text": doc, 
                        "metadata": meta, 
                        "distance": dist,
                        "document_id": meta.get("document_id") if meta else None,
                        "document_name": meta.get("document_name") if meta else None,
                        "chunk_index": meta.get("chunk_index") if meta else None
                    }
                    for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances)
                ],
                "query": req.query,
                "total_results": len(documents),
                "document_filter": req.document_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-all")
def delete_all_history():
    """Deletes and recreates the entire collection, clearing all data."""
    try:
        # Delete and recreate the chroma_store collection
        chroma_store.client.delete_collection("walnut-embeddings")
        chroma_store.collection = chroma_store.client.get_or_create_collection(
            name="walnut-embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        return {"status": "success", "message": "Collection 'walnut-embeddings' has been cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear collection: {str(e)}")

@app.delete("/delete-items")
def delete_items(req: DeleteRequest):
    """Deletes specific items from the collection by their IDs."""
    try:
        chroma_store.collection.delete(ids=req.ids)
        return {"status": "success", "message": f"Successfully deleted {len(req.ids)} item(s)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document Processing Endpoints

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document (PDF, DOCX, PPTX).
    The document will be chunked and stored in the vector database.
    """
    return await document_service.process_document(file)

@app.get("/documents", response_model=DocumentListResponse)
def get_documents():
    """Get list of all uploaded documents."""
    documents = document_service.get_document_list()
    return DocumentListResponse(
        documents=documents,
        total_count=len(documents)
    )

@app.get("/documents/{document_id}/chunks", response_model=List[ChunkInfo])
def get_document_chunks(document_id: str):
    """Get all chunks for a specific document."""
    return document_service.get_document_chunks(document_id)

@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    """Delete a document and all its chunks."""
    return document_service.delete_document(document_id)

@app.get("/documents/{document_id}/info")
def get_document_info(document_id: str):
    """Get information about a specific document."""
    if document_id not in document_service.documents_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    metadata = document_service.documents_metadata[document_id]
    return {
        "document_id": metadata["document_id"],
        "document_name": metadata["document_name"],
        "upload_date": metadata["upload_date"],
        "total_chunks": metadata["total_chunks"],
        "total_characters": metadata["total_characters"],
        "file_type": metadata["file_type"]
    }

@app.post("/chunk-document")
async def chunk_document(file: UploadFile = File(...)):
    """
    Upload a document and return its chunks without storing in database.
    This endpoint processes the file, extracts text, chunks it, and returns the chunks.
    """
    try:
        # Validate file format
        if not document_service.document_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {document_service.document_processor.supported_formats}"
            )
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Extract text with page information for PDFs
        extracted_text, page_info = document_service.document_processor.extract_text_with_page_info(file_content, file.filename)
        cleaned_text = document_service.document_processor.clean_text(extracted_text)
        
        if not cleaned_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in document")
        
        # Generate temporary document ID
        import uuid
        temp_document_id = str(uuid.uuid4())
        
        # Create chunks with page information
        chunks = document_service._create_chunks_with_page_info(
            text=cleaned_text,
            document_id=temp_document_id,
            document_name=file.filename,
            page_info=page_info
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid chunks created from document")
        
        # Convert chunks to response format
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append({
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "page_number": chunk.page_number,
                "chunk_length": len(chunk.text)
            })
        
        return {
            "success": True,
            "document_name": file.filename,
            "total_chunks": len(chunks),
            "total_characters": len(cleaned_text),
            "file_type": file.filename.split('.')[-1].lower(),
            "chunks": chunk_responses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")