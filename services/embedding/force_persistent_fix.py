#!/usr/bin/env python3
"""
Force fix for ChromaDB persistence - ensures everything is saved
"""

import os
import shutil
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

def force_persistent_fix():
    """Force fix ChromaDB to ensure true persistence."""
    
    print("🔧 Force fixing ChromaDB persistence...")
    
    # Step 1: Remove all existing ChromaDB data
    chromadb_path = Path("./chromadb")
    if chromadb_path.exists():
        print("🗑️  Removing existing ChromaDB data...")
        shutil.rmtree(chromadb_path)
        print("✅ ChromaDB data removed")
    
    # Step 2: Create new directory
    chromadb_path.mkdir(exist_ok=True)
    print("✅ New ChromaDB directory created")
    
    # Step 3: Test persistent client
    print("🧪 Testing persistent client...")
    try:
        # Create persistent client
        client = chromadb.PersistentClient(path="./chromadb")
        
        # Test embedding model
        embedder = SentenceTransformer("BAAI/bge-base-en-v1.5", trust_remote_code=True)
        test_embedding = embedder.encode(["test"]).tolist()[0]
        print(f"✅ Embedding dimension: {len(test_embedding)}")
        
        # Create collection
        collection = client.get_or_create_collection(
            name="walnut-embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add test data
        collection.add(
            ids=["test-1"],
            documents=["This is a test document"],
            embeddings=[test_embedding]
        )
        
        print("✅ Test data added")
        
        # Verify data exists
        results = collection.get()
        print(f"✅ Data verified: {len(results['documents'])} items")
        
        # Close and reopen to test persistence
        del collection
        del client
        
        # Reopen and check
        client2 = chromadb.PersistentClient(path="./chromadb")
        collection2 = client2.get_collection("walnut-embeddings")
        results2 = collection2.get()
        
        if len(results2['documents']) > 0:
            print("✅ Data persists after reopen!")
        else:
            print("❌ Data lost after reopen")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    print("\n🎉 ChromaDB persistence fix completed!")
    print("💾 Data will now persist between server restarts")
    return True

if __name__ == "__main__":
    success = force_persistent_fix()
    if success:
        print("\n✅ You can now start the server: python run_server.py")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")
