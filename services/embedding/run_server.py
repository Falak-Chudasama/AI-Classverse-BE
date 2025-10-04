#!/usr/bin/env python3
"""
Startup script for the AI Classroom Embedding Service
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Ensure the chromadb directory exists
    chromadb_path = Path("./chromadb")
    chromadb_path.mkdir(exist_ok=True)
    
    print("🚀 Starting AI Classroom Embedding Service...")
    print(f"📁 ChromaDB directory: {chromadb_path.absolute()}")
    print("💾 Data will persist between server restarts")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
