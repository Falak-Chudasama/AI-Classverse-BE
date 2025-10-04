import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_index: int
    total_chunks: int
    document_id: str
    document_name: str
    start_char: int
    end_char: int
    page_number: int = None

class TextChunker:
    def __init__(self, chunk_size: int = 800, overlap_size: int = 100):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            overlap_size: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Split on sentence endings, keeping the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str, document_id: str, document_name: str, page_number: int = None) -> List[TextChunk]:
        """
        Create overlapping chunks from text.
        
        Args:
            text: The text to chunk
            document_id: Unique identifier for the document
            document_name: Name of the document
            page_number: Page number (for PDFs)
        
        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []
        
        # Split into sentences first
        sentences = self.split_into_sentences(text)
        if not sentences:
            return []
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk = TextChunk(
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    total_chunks=0,  # Will be updated later
                    document_id=document_id,
                    document_name=document_name,
                    start_char=current_start,
                    end_char=current_start + len(current_chunk),
                    page_number=page_number
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_start = current_start + len(current_chunk) - len(overlap_text) - len(sentence) - 1
                chunk_index += 1
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                    current_start = 0
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunk = TextChunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                total_chunks=0,  # Will be updated
                document_id=document_id,
                document_name=document_name,
                start_char=current_start,
                end_char=current_start + len(current_chunk),
                page_number=page_number
            )
            chunks.append(chunk)
        
        # Update total_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total_chunks
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap."""
        if len(text) <= self.overlap_size:
            return text
        
        # Find the last sentence that fits in overlap size
        sentences = self.split_into_sentences(text)
        overlap_text = ""
        
        for sentence in reversed(sentences):
            if len(overlap_text + sentence) <= self.overlap_size:
                overlap_text = sentence + " " + overlap_text if overlap_text else sentence
            else:
                break
        
        return overlap_text.strip()
    
    def chunk_by_paragraphs(self, text: str, document_id: str, document_name: str) -> List[TextChunk]:
        """
        Alternative chunking method that respects paragraph boundaries.
        Useful for documents with clear paragraph structure.
        """
        paragraphs = text.split('\n\n')
        chunks = []
        chunk_index = 0
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # If paragraph is too long, split it
            if len(para) > self.chunk_size:
                para_chunks = self.create_chunks(para, document_id, document_name)
                for chunk in para_chunks:
                    chunk.chunk_index = chunk_index
                    chunks.append(chunk)
                    chunk_index += 1
            else:
                chunk = TextChunk(
                    text=para.strip(),
                    chunk_index=chunk_index,
                    total_chunks=0,
                    document_id=document_id,
                    document_name=document_name,
                    start_char=0,
                    end_char=len(para)
                )
                chunks.append(chunk)
                chunk_index += 1
        
        # Update total_chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total_chunks
        
        return chunks
