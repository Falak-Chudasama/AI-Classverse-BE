#!/usr/bin/env python3
"""
Simple server runner without uvicorn dependency
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    import uvicorn
    
    if __name__ == "__main__":
        # Ensure the chromadb directory exists
        chromadb_path = Path("./chromadb")
        chromadb_path.mkdir(exist_ok=True)
        
        print("Starting AI Classroom Embedding Service...")
        print("Server will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
except ImportError as e:
    print(f"Import error: {e}")
    print("\nTrying alternative method...")
    
    # Alternative: Try to run with built-in server
    try:
        from app import app
        print("FastAPI app loaded successfully!")
        print("You can now run: python -m uvicorn app:app --host 0.0.0.0 --port 8000")
    except Exception as ex:
        print(f"Error loading app: {ex}")
        print("\nPlease install uvicorn:")
        print("pip install uvicorn[standard]")
