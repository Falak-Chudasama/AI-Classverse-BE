#!/usr/bin/env python3
"""
Test script for the AI Classroom Embedding Service
"""

import requests
import json
import time
from pathlib import Path

# Service URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_document_list():
    """Test getting document list."""
    print("\nTesting document list...")
    response = requests.get(f"{BASE_URL}/documents")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total documents: {data['total_count']}")
        for doc in data['documents']:
            print(f"- {doc['document_name']} ({doc['file_type']}) - {doc['total_chunks']} chunks")
    return response.status_code == 200

def test_search(query: str, k: int = 3):
    """Test search functionality."""
    print(f"\nTesting search for: '{query}'")
    payload = {
        "query": query,
        "k": k
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} results")
        for i, result in enumerate(data['results'][:3]):
            print(f"{i+1}. {result['text'][:100]}...")
            print(f"   Document: {result.get('document_name', 'N/A')}")
            print(f"   Distance: {result['distance']:.4f}")
    return response.status_code == 200

def test_embed_text():
    """Test embedding custom text."""
    print("\nTesting text embedding...")
    payload = {
        "content": "This is a test document about artificial intelligence and machine learning.",
        "metadata": {"source": "test", "type": "sample"}
    }
    response = requests.post(f"{BASE_URL}/embed", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Embedded successfully: {data['message']}")
    return response.status_code == 200

def main():
    """Run all tests."""
    print("AI Classroom Embedding Service Test Suite")
    print("Using PyMuPDF, python-docx, and python-pptx")
    print("=" * 50)
    
    # Wait for service to start
    print("Waiting for service to start...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_check),
        ("Document List", test_document_list),
        ("Text Embedding", test_embed_text),
        ("Search Test 1", lambda: test_search("artificial intelligence")),
        ("Search Test 2", lambda: test_search("machine learning algorithms")),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the service logs.")

if __name__ == "__main__":
    main()
