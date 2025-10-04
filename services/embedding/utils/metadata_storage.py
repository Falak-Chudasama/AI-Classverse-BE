#!/usr/bin/env python3
"""
File-based metadata storage for document persistence
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MetadataStorage:
    def __init__(self, storage_file="./metadata.json"):
        self.storage_file = Path(storage_file)
        self.metadata = {}
        self.load_metadata()
    
    def load_metadata(self):
        """Load metadata from file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    self.metadata = json.load(f)
                print(f"📚 Loaded {len(self.metadata)} documents from metadata file")
            else:
                print("📝 No existing metadata file found")
        except Exception as e:
            print(f"⚠️  Error loading metadata: {e}")
            self.metadata = {}
    
    def save_metadata(self):
        """Save metadata to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
            print(f"💾 Saved {len(self.metadata)} documents to metadata file")
        except Exception as e:
            print(f"⚠️  Error saving metadata: {e}")
    
    def add_document(self, document_id: str, document_name: str, total_chunks: int, total_characters: int, file_type: str):
        """Add document metadata."""
        self.metadata[document_id] = {
            "document_id": document_id,
            "document_name": document_name,
            "upload_date": datetime.now().isoformat(),
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "file_type": file_type
        }
        self.save_metadata()
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document metadata."""
        return self.metadata.get(document_id)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all document metadata."""
        return list(self.metadata.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document metadata."""
        if document_id in self.metadata:
            del self.metadata[document_id]
            self.save_metadata()
            return True
        return False
    
    def clear_all(self):
        """Clear all metadata."""
        self.metadata = {}
        self.save_metadata()
