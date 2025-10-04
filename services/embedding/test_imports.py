#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

try:
    print("Testing imports...")
    
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    print("✅ FastAPI imports successful")
    
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ CORS middleware import successful")
    
    from typing import List
    print("✅ List import successful")
    
    from utils.schema_ import (
        EmbedRequest, SearchRequest, DeleteRequest, 
        DocumentUploadResponse, DocumentListResponse, ChunkInfo
    )
    print("✅ Schema imports successful")
    
    import chromadb
    print("✅ ChromaDB import successful")
    
    from chromadb.config import Settings
    print("✅ ChromaDB Settings import successful")
    
    from vectordb.chroma_store import ChromaStore
    print("✅ ChromaStore import successful")
    
    from services.document_service import DocumentService
    print("✅ DocumentService import successful")
    
    print("\n🎉 All imports successful! The server should work now.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your dependencies and virtual environment.")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
