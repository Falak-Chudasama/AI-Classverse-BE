#!/usr/bin/env python3
"""
Test script to verify document persistence
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_document_persistence():
    """Test if documents persist between server restarts."""
    
    print("🧪 Testing Document Persistence...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return False
    except:
        print("❌ Server is not running. Please start it first.")
        return False
    
    # Test 2: Check current documents
    print("\n📚 Checking current documents...")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Current documents: {data['total_count']}")
            for doc in data['documents']:
                print(f"  - {doc['document_name']} ({doc['file_type']}) - {doc['total_chunks']} chunks")
        else:
            print("❌ Error getting documents")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Check all items
    print("\n📄 Checking all items...")
    try:
        response = requests.get(f"{BASE_URL}/get-all")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Total items in database: {data['count']}")
        else:
            print("❌ Error getting all items")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Test search
    print("\n🔍 Testing search...")
    try:
        response = requests.post(f"{BASE_URL}/search", json={
            "query": "the",
            "k": 3
        })
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Search results: {data['total_results']}")
            if data['total_results'] > 0:
                print("✅ Search is working")
            else:
                print("⚠️  No search results found")
        else:
            print("❌ Error with search")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 Document persistence test completed!")
    print("💡 To test full persistence:")
    print("  1. Upload a document")
    print("  2. Stop the server (Ctrl+C)")
    print("  3. Start the server again")
    print("  4. Check if documents still exist")
    
    return True

if __name__ == "__main__":
    test_document_persistence()
