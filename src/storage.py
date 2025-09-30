"""
Document Storage System
Handles storage of original and redacted documents
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional

class DocumentStorage:
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir if storage_dir is not None else "document_storage"
        self.documents_db = {}  # In-memory for demo, use proper DB in production
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    async def store_document(self, name: str, original_text: str, redacted_text: str, 
                           type_hint: Optional[str] = None, request_id: str = None) -> str:
        """
        Store document with both original (for processing) and redacted (for storage) versions
        Returns document ID
        """
        doc_id = str(uuid.uuid4())
        
        # Store metadata in memory (use database in production)
        self.documents_db[doc_id] = {
            "id": doc_id,
            "name": name,
            "type_hint": type_hint,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "original_length": len(original_text),
            "redacted_length": len(redacted_text)
        }
        
        # Store redacted version to file (this is what persists)
        redacted_file_path = os.path.join(self.storage_dir, f"{doc_id}_redacted.txt")
        with open(redacted_file_path, 'w', encoding='utf-8') as f:
            f.write(redacted_text)
        
        # Store original version temporarily in memory for processing
        # In production, this would be encrypted and have strict access controls
        self.documents_db[doc_id]["original_text"] = original_text
        self.documents_db[doc_id]["redacted_text"] = redacted_text
        
        return doc_id
    
    async def get_document(self, doc_id: str, redacted_only: bool = True) -> Optional[Dict]:
        """
        Retrieve document by ID
        If redacted_only=True, returns only redacted version
        """
        if doc_id not in self.documents_db:
            return None
        
        doc = self.documents_db[doc_id].copy()
        
        if redacted_only:
            # Remove original text from response for security
            doc.pop("original_text", None)
        
        return doc
    
    async def get_documents_by_request(self, request_id: str, redacted_only: bool = True) -> List[Dict]:
        """
        Get all documents for a request ID
        """
        documents = []
        
        for doc_id, doc_data in self.documents_db.items():
            if doc_data.get("request_id") == request_id:
                doc = doc_data.copy()
                if redacted_only:
                    doc.pop("original_text", None)
                documents.append(doc)
        
        return documents
    
    async def cleanup_old_documents(self, max_age_hours: int = 24):
        """
        Clean up old documents (for demo purposes)
        In production, implement proper retention policies
        """
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for doc_id, doc_data in self.documents_db.items():
            doc_timestamp = datetime.fromisoformat(doc_data["timestamp"]).timestamp()
            if doc_timestamp < cutoff_time:
                to_remove.append(doc_id)
        
        for doc_id in to_remove:
            # Remove from memory
            self.documents_db.pop(doc_id, None)
            
            # Remove redacted file
            redacted_file_path = os.path.join(self.storage_dir, f"{doc_id}_redacted.txt")
            if os.path.exists(redacted_file_path):
                os.remove(redacted_file_path)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_docs = len(self.documents_db)
        total_original_size = sum(doc.get("original_length", 0) for doc in self.documents_db.values())
        total_redacted_size = sum(doc.get("redacted_length", 0) for doc in self.documents_db.values())
        
        return {
            "total_documents": total_docs,
            "total_original_size": total_original_size,
            "total_redacted_size": total_redacted_size,
            "storage_reduction": total_original_size - total_redacted_size if total_original_size > 0 else 0,
            "storage_directory": self.storage_dir
        }