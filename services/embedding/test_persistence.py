#!/usr/bin/env python3
"""
Test script to verify ChromaDB persistence
"""

import os
from pathlib import Path
from vectordb.chroma_store import ChromaStore

def test_persistence():
    """Test if ChromaDB data persists between sessions."""
    
    print("🧪 Testing ChromaDB persistence...")
    
    # Check if chromadb directory exists
    chromadb_path = Path("./chromadb")
    if chromadb_path.exists():
        print("✅ ChromaDB directory exists")
        print(f"📁 Path: {chromadb_path.absolute()}")
        
        # List files in chromadb directory
        files = list(chromadb_path.rglob("*"))
        print(f"📄 Files in ChromaDB: {len(files)}")
        for file in files:
            print(f"  - {file.name}")
    else:
        print("❌ ChromaDB directory not found")
        return False
    
    # Test ChromaStore
    try:
        print("\n🔧 Testing ChromaStore...")
        chroma_store = ChromaStore()
        
        # Check collection
        collection = chroma_store.collection
        count = collection.count()
        print(f"📊 Items in collection: {count}")
        
        if count > 0:
            print("✅ Data found in collection")
            
            # Get a sample item
            sample = collection.get(limit=1)
            if sample['documents']:
                print(f"📝 Sample text: {sample['documents'][0][:100]}...")
        else:
            print("⚠️  No data in collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ChromaStore: {e}")
        return False

if __name__ == "__main__":
    success = test_persistence()
    if success:
        print("\n🎉 ChromaDB persistence test completed!")
    else:
        print("\n❌ ChromaDB persistence test failed!")
