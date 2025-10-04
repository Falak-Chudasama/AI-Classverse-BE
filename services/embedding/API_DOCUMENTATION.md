# Embedding Service API Documentation

This document describes the REST API endpoints for the AI Classroom Embedding Service.

## Base URL
```
http://localhost:8000
```

## Health Check

### GET /
Check if the service is running.

**Response:**
```json
{
  "status": "ChromaDB context engine is live."
}
```

## Core RAG Endpoints

### POST /embed
Embed text content into the vector database.

**Request Body:**
```json
{
  "content": "Text to embed",
  "metadata": {
    "app": "Walnut",
    "type": "document"
  }
}
```

**Response:**
```json
{
  "message": "1 item(s) embedded successfully.",
  "ids": ["uuid-here"],
  "success": true
}
```

### POST /search
Search for similar content using semantic similarity.

**Request Body:**
```json
{
  "query": "search text",
  "k": 5,
  "document_id": "optional-document-filter"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "chunk-id",
      "text": "matching text",
      "metadata": {...},
      "distance": 0.123,
      "document_id": "doc-id",
      "document_name": "document.pdf",
      "chunk_index": 0
    }
  ],
  "query": "search text",
  "total_results": 1,
  "document_filter": null
}
```

### DELETE /delete-all
Clear the entire vector database.

**Response:**
```json
{
  "status": "success",
  "message": "Collection 'walnut-embeddings' has been cleared."
}
```

### GET /get-all
Get all documents from the vector database.

**Response:**
```json
{
  "count": 10,
  "data": [
    {
      "id": "chunk-id",
      "text": "document text",
      "metadata": {...}
    }
  ]
}
```

## Document Processing Endpoints

### POST /upload-document
Upload and process a document (PDF, DOCX, PPTX).

**Request:** Multipart form with file
**Response:**
```json
{
  "document_id": "uuid",
  "document_name": "document.pdf",
  "chunks_created": 5,
  "total_characters": 1000,
  "processing_time": 2.5,
  "success": true
}
```

### GET /documents
Get list of all uploaded documents.

**Response:**
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "document_name": "document.pdf",
      "upload_date": "2024-01-01T00:00:00",
      "total_chunks": 5,
      "total_characters": 1000,
      "file_type": "pdf"
    }
  ],
  "total_count": 1
}
```

### GET /documents/{document_id}/chunks
Get all chunks for a specific document.

**Response:**
```json
[
  {
    "chunk_id": "chunk-uuid",
    "text": "chunk text",
    "chunk_index": 0,
    "total_chunks": 5,
    "document_id": "doc-uuid",
    "document_name": "document.pdf",
    "start_char": 0,
    "end_char": 200,
    "page_number": 1
  }
]
```

### DELETE /documents/{document_id}
Delete a document and all its chunks.

**Response:**
```json
{
  "status": "success",
  "message": "Document 'uuid' and all its chunks deleted successfully",
  "chunks_deleted": 5
}
```

### GET /documents/{document_id}/info
Get information about a specific document.

**Response:**
```json
{
  "document_id": "uuid",
  "document_name": "document.pdf",
  "upload_date": "2024-01-01T00:00:00",
  "total_chunks": 5,
  "total_characters": 1000,
  "file_type": "pdf"
}
```

### POST /chunk-document
Process a document and return its chunks without storing.

**Request:** Multipart form with file
**Response:**
```json
{
  "success": true,
  "document_name": "document.pdf",
  "total_chunks": 5,
  "total_characters": 1000,
  "file_type": "pdf",
  "chunks": [
    {
      "chunk_index": 0,
      "text": "chunk text",
      "start_char": 0,
      "end_char": 200,
      "page_number": 1,
      "chunk_length": 200
    }
  ]
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error description"
}
```

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors)
- `404` - Not Found (document not found)
- `500` - Internal Server Error

## Usage Examples

### cURL Examples

#### 1. Health Check
```bash
curl -X GET http://localhost:8000/
```

#### 2. Embed Text
```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test document about AI.",
    "metadata": {"app": "Walnut"}
  }'
```

#### 3. Search Content
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "k": 5
  }'
```

#### 4. Upload Document
```bash
curl -X POST http://localhost:8000/upload-document \
  -F "file=@document.pdf"
```

#### 5. Get All Documents
```bash
curl -X GET http://localhost:8000/get-all
```

#### 6. Clear All Data
```bash
curl -X DELETE http://localhost:8000/delete-all
```

## Configuration

### Environment Variables
- `CHROMA_DB_PATH` - Path to ChromaDB storage (default: ./chromadb)
- `EMBEDDING_MODEL` - Sentence transformer model (default: BAAI/bge-base-en-v1.5)

### Supported File Formats
- PDF (.pdf) - Using PyMuPDF
- Microsoft Word (.docx) - Using python-docx
- PowerPoint (.pptx) - Using python-pptx

### Chunking Parameters
- **Chunk Size**: 800 characters (configurable)
- **Overlap Size**: 100 characters (configurable)
- **Strategy**: Sentence-aware chunking with overlap

## Development

### Starting the Service
```bash
# Method 1: Using the startup script
python start_service.py

# Method 2: Direct uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Using run_server.py
python run_server.py
```

### Testing Endpoints
```bash
python test_endpoints.py
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Integration with Node.js Server

The Node.js server expects these endpoints to be available:
- `POST /embed` - For storing conversation summaries
- `POST /search` - For retrieving relevant context
- `DELETE /delete-all` - For clearing conversation history

The service is designed to work seamlessly with the AI-Classverse backend for RAG (Retrieval Augmented Generation) functionality.
