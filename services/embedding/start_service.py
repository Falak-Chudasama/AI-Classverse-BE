#!/usr/bin/env python3
"""
Simple startup script for the embedding service
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import chromadb
        import sentence_transformers
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_service():
    """Start the embedding service"""
    print("🚀 Starting AI Classroom Embedding Service...")
    print("📁 ChromaDB directory: ./chromadb")
    print("💾 Data will persist between server restarts")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🧪 Test endpoints with: python test_endpoints.py")
    print("\n" + "=" * 60)
    
    try:
        # Run the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
    except Exception as e:
        print(f"❌ Error starting service: {e}")

def main():
    print("AI Classroom Embedding Service Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the services/embedding directory")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start the service
    start_service()

if __name__ == "__main__":
    main()
