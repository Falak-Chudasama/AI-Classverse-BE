# AI Classroom Embedding Service

A FastAPI-based microservice for document processing, text chunking, and vector similarity search using ChromaDB and SentenceTransformers.

## Features

- **Document Processing**: Support for PDF, DOCX, and PPTX files
- **Intelligent Chunking**: Text chunking with overlap for better search results
- **Vector Search**: Semantic search using ChromaDB and BGE embeddings
- **Document Management**: Upload, list, and delete documents
- **Metadata Tracking**: Comprehensive metadata for documents and chunks

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python run_server.py
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Document Processing

#### Upload Document
```
POST /upload-document
```
Upload and process a document (PDF, DOCX, PPTX). The document will be automatically chunked and stored in the vector database.

**Request**: Multipart form with file
**Response**: Document processing results with chunk information

#### List Documents
```
GET /documents
```
Get list of all uploaded documents with metadata.

#### Get Document Chunks
```
GET /documents/{document_id}/chunks
```
Get all chunks for a specific document.

#### Delete Document
```
DELETE /documents/{document_id}
```
Delete a document and all its chunks.

#### Get Document Info
```
GET /documents/{document_id}/info
```
Get detailed information about a specific document.

### Search and Embedding

#### Search Documents
```
POST /search
```
Search for similar content using semantic similarity.

**Request Body**:
```json
{
  "query": "search text",
  "k": 5,
  "document_id": "optional-document-filter"
}
```

#### Embed Text
```
POST /embed
```
Embed custom text content and store in the database.

#### Get All Documents
```
GET /get-all
```
Retrieve all documents from the collection.

#### Delete Items
```
DELETE /delete-items
```
Delete specific items by their IDs.

#### Clear Collection
```
DELETE /delete-all
```
Clear the entire collection.

## Configuration

### Chunking Parameters
- **Chunk Size**: 800 characters (configurable)
- **Overlap Size**: 100 characters (configurable)
- **Strategy**: Sentence-aware chunking with overlap

### Supported File Formats
- PDF (.pdf) - Using PyMuPDF for better text extraction
- Microsoft Word (.docx) - Using python-docx
- PowerPoint (.pptx) - Using python-pptx

### Document Processing Libraries
- **PDF**: PyMuPDF (fitz) - Superior text extraction with page information
- **DOCX**: python-docx - Native Microsoft Word support
- **PPTX**: python-pptx - Native PowerPoint support

### Embedding Model
- Model: `BAAI/bge-base-en-v1.5`
- Normalization: Enabled
- Trust Remote Code: Enabled

## Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Search for Content
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "k": 5
  }'
```

### Search within Specific Document
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural networks",
    "k": 3,
    "document_id": "document-uuid-here"
  }'
```

## Data Models

### Document Metadata
- `document_id`: Unique identifier
- `document_name`: Original filename
- `upload_date`: Upload timestamp
- `total_chunks`: Number of chunks created
- `total_characters`: Total text length
- `file_type`: File extension

### Chunk Metadata
- `chunk_id`: Unique chunk identifier
- `document_id`: Parent document ID
- `chunk_index`: Position in document
- `start_char`: Starting character position
- `end_char`: Ending character position
- `page_number`: Page number (for PDFs)

## Architecture

```
Document Upload → Text Extraction → Chunking → Embedding → Vector Storage
                                                      ↓
Search Query → Embedding → Vector Similarity → Ranked Results
```

## Development

### Project Structure
```
services/embedding/
├── app.py                 # Main FastAPI application
├── run_server.py          # Server startup script
├── requirements.txt       # Python dependencies
├── utils/
│   ├── document_processor.py  # File processing utilities
│   ├── text_chunker.py        # Text chunking logic
│   └── schema_.py             # Pydantic models
├── services/
│   └── document_service.py   # Document management service
├── vectordb/
│   └── chroma_store.py       # ChromaDB wrapper
└── models/
    └── embedder.py           # Embedding model
```

### Adding New File Formats

1. Add extraction logic to `utils/document_processor.py`
2. Update `supported_formats` list
3. Test with sample files

### Customizing Chunking

Modify parameters in `utils/text_chunker.py`:
- `chunk_size`: Maximum characters per chunk
- `overlap_size`: Overlap between chunks
- Chunking strategy (sentence-aware vs paragraph-based)

## Production Considerations

1. **CORS Configuration**: Update CORS settings for production
2. **File Size Limits**: Configure appropriate file size limits
3. **Database Persistence**: Ensure ChromaDB data directory is persistent
4. **Error Handling**: Implement comprehensive error handling
5. **Logging**: Add structured logging for monitoring
6. **Rate Limiting**: Implement rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **Empty Text Extraction**: Check file format support and file integrity
2. **Chunking Issues**: Verify text content and adjust chunking parameters
3. **Embedding Errors**: Ensure model download and internet connectivity
4. **Database Errors**: Check ChromaDB directory permissions

### Logs
Check server logs for detailed error messages and processing information.
