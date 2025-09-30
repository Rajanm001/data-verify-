"""
Pydantic models for request/response schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator

class Document(BaseModel):
    name: str
    text: str
    type_hint: Optional[str] = None
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Document text cannot be empty')
        return v

class IngestRequest(BaseModel):
    documents: List[Document]
    
    @validator('documents')
    def documents_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('At least one document is required')
        if len(v) > 10:  # MAX_DOCUMENTS_PER_REQUEST
            raise ValueError('Too many documents (max 10)')
        return v

class DocumentSummary(BaseModel):
    doc_id: str
    name: str
    type_hint: Optional[str]
    character_count: int
    redacted_character_count: int
    pii_items_redacted: int

class IngestResponse(BaseModel):
    doc_summaries: List[DocumentSummary]
    request_id: str
    message: str

class ExtractedField(BaseModel):
    field_name: str
    value: Any
    confidence: float
    source_document: str

class ClassificationResult(BaseModel):
    document_name: str
    predicted_type: str
    confidence: float
    abstained: bool = False
    reason: Optional[str] = None

class ChecklistItem(BaseModel):
    rule_id: str
    description: str
    required_ok: bool
    problems: List[str] = []
    evidence: List[str] = []

class Citation(BaseModel):
    rule_id: str
    chunk: str
    relevance_score: float

class AnalyzeResponse(BaseModel):
    parsed: Dict[str, Any]
    checklist: List[Dict[str, Any]]  # Serialized ChecklistItem objects
    brief: str
    client_email: str
    citations: List[Dict[str, Any]]  # Serialized Citation objects
    request_id: str
    documents_analyzed: int
    compliance_status: str
    enterprise_metadata: Optional[Dict[str, Any]] = None