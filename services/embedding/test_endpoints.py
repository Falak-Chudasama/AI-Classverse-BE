#!/usr/bin/env python3
"""
Test script to verify the embedding service endpoints work correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_embed():
    """Test the embed endpoint"""
    try:
        data = {
            "content": "This is a test document about artificial intelligence and machine learning.",
            "metadata": {
                "app": "Walnut",
                "type": "test"
            }
        }
        response = requests.post(f"{BASE_URL}/embed", json=data)
        print(f"Embed test: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Embed test failed: {e}")
        return False

def test_search():
    """Test the search endpoint"""
    try:
        data = {
            "query": "artificial intelligence",
            "k": 3
        }
        response = requests.post(f"{BASE_URL}/search", json=data)
        print(f"Search test: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Search test failed: {e}")
        return False

def test_get_all():
    """Test the get-all endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/get-all")
        print(f"Get all test: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Get all test failed: {e}")
        return False

def test_delete_all():
    """Test the delete-all endpoint"""
    try:
        response = requests.delete(f"{BASE_URL}/delete-all")
        print(f"Delete all test: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Delete all test failed: {e}")
        return False

def main():
    print("🧪 Testing Embedding Service Endpoints")
    print("=" * 50)
    
    # Test health
    print("\n1. Testing health endpoint...")
    health_ok = test_health()
    
    if not health_ok:
        print("❌ Service is not running. Please start the service first:")
        print("   cd services/embedding")
        print("   python run_server.py")
        return
    
    # Test embed
    print("\n2. Testing embed endpoint...")
    embed_ok = test_embed()
    
    # Wait a moment for embedding to complete
    time.sleep(1)
    
    # Test search
    print("\n3. Testing search endpoint...")
    search_ok = test_search()
    
    # Test get all
    print("\n4. Testing get-all endpoint...")
    get_all_ok = test_get_all()
    
    # Test delete all
    print("\n5. Testing delete-all endpoint...")
    delete_ok = test_delete_all()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Health: {'✅' if health_ok else '❌'}")
    print(f"   Embed:  {'✅' if embed_ok else '❌'}")
    print(f"   Search: {'✅' if search_ok else '❌'}")
    print(f"   Get All: {'✅' if get_all_ok else '❌'}")
    print(f"   Delete: {'✅' if delete_ok else '❌'}")
    
    all_passed = all([health_ok, embed_ok, search_ok, get_all_ok, delete_ok])
    print(f"\n🎯 Overall: {'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")
    
    if all_passed:
        print("\n🚀 The embedding service is working correctly!")
        print("   The Node.js server should now be able to connect to it.")
    else:
        print("\n⚠️  Some tests failed. Check the service logs for details.")

if __name__ == "__main__":
    main()
