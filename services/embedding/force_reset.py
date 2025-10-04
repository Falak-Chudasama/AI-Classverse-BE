#!/usr/bin/env python3
"""
Force reset ChromaDB to fix embedding dimension issues
"""

import os
import shutil
from pathlib import Path
import chromadb
from chromadb.config import Settings

def force_reset():
    """Force reset ChromaDB completely."""
    
    print("🔄 Force resetting ChromaDB...")
    
    # Step 1: Remove ChromaDB directory completely
    chromadb_path = Path("./chromadb")
    if chromadb_path.exists():
        print("Removing ChromaDB directory...")
        shutil.rmtree(chromadb_path)
        print("✅ ChromaDB directory removed")
    
    # Step 2: Remove any other ChromaDB files
    for file in Path(".").glob("*.sqlite3"):
        print(f"Removing {file}...")
        file.unlink()
    
    # Step 3: Create new directory
    chromadb_path.mkdir(exist_ok=True)
    print("✅ New ChromaDB directory created")
    
    # Step 4: Test with fresh ChromaDB
    print("Testing with fresh ChromaDB...")
    try:
        client = chromadb.Client(Settings())
        
        # Create a test collection with BGE model
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("BAAI/bge-base-en-v1.5", trust_remote_code=True)
        
        # Test embedding
        test_text = "This is a test"
        embedding = embedder.encode([test_text]).tolist()[0]
        print(f"✅ Embedding dimension: {len(embedding)}")
        
        # Create collection
        collection = client.get_or_create_collection("test-collection")
        
        # Add test embedding
        collection.add(
            ids=["test-1"],
            documents=[test_text],
            embeddings=[embedding]
        )
        
        print("✅ Test embedding added successfully")
        
        # Clean up test collection
        client.delete_collection("test-collection")
        print("✅ Test collection cleaned up")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    print("\n🎉 Force reset complete!")
    print("ChromaDB is now ready with correct dimensions.")
    return True

if __name__ == "__main__":
    success = force_reset()
    if success:
        print("\n✅ You can now start the server: python run_server.py")
    else:
        print("\n❌ Reset failed. Please check the error messages above.")
