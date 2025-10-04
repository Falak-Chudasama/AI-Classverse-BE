#!/usr/bin/env python3
"""
Script to reset ChromaDB with correct embedding dimensions
"""

import os
import shutil
from pathlib import Path
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def reset_chromadb():
    """Reset ChromaDB database to fix embedding dimension issues."""
    
    # Path to ChromaDB directory
    chromadb_path = Path("./chromadb")
    
    if chromadb_path.exists():
        print("Found existing ChromaDB directory...")
        print("Removing old ChromaDB data...")
        shutil.rmtree(chromadb_path)
        print("✅ ChromaDB directory removed")
    else:
        print("No existing ChromaDB directory found")
    
    # Create new directory
    chromadb_path.mkdir(exist_ok=True)
    print("✅ New ChromaDB directory created")
    
    # Test the embedding model
    print("Testing embedding model...")
    try:
        embedder = SentenceTransformer("BAAI/bge-base-en-v1.5", trust_remote_code=True)
        test_embedding = embedder.encode(["test"])
        print(f"✅ Embedding model works! Dimension: {len(test_embedding[0])}")
    except Exception as e:
        print(f"❌ Error with embedding model: {e}")
    
    print("\n🎉 ChromaDB reset complete!")
    print("You can now start the server with the correct embedding dimensions.")
    print("Run: python run_server.py")

if __name__ == "__main__":
    reset_chromadb()
