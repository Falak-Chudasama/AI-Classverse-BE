from pydantic import BaseModel
from typing import Union, List, Optional
from datetime import datetime

class EmbedRequest(BaseModel):
    content: Union[str, List[str]]
    metadata: Optional[Union[dict, List[dict]]] = None

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    document_id: Optional[str] = None  # Filter by specific document

class DeleteRequest(BaseModel):
    ids: List[str]

class DocumentUploadResponse(BaseModel):
    document_id: str
    document_name: str
    chunks_created: int
    total_characters: int
    processing_time: float
    success: bool

class DocumentInfo(BaseModel):
    document_id: str
    document_name: str
    upload_date: datetime
    total_chunks: int
    total_characters: int
    file_type: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int

class ChunkInfo(BaseModel):
    chunk_id: str
    text: str
    chunk_index: int
    total_chunks: int
    document_id: str
    document_name: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None