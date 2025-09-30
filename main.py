"""
GetGSA: AI + RAG System
Main FastAPI application with document ingestion, AI classification, and RAG-based analysis.
"""

import os
import uuid
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.models import IngestRequest, IngestResponse, AnalyzeResponse
from src.document_processor import DocumentProcessor
from src.rag_system import RAGSystem
from src.ai_service import EnterpriseAIService
from src.pii_redactor import PIIRedactor
from src.storage import DocumentStorage
import logging

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GetGSA: AI + RAG System",
    description="Smart GSA document processing with AI classification and RAG-based policy checking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enterprise-grade services
document_processor = DocumentProcessor()
rag_system = RAGSystem()
ai_service = EnterpriseAIService()  # 🚀 Enhanced AI with multi-provider support
pii_redactor = PIIRedactor()
document_storage = DocumentStorage()

# Enterprise configuration
ENTERPRISE_CONFIG = {
    "version": "2.0.0-enterprise",
    "features": ["multi-ai-providers", "advanced-caching", "performance-metrics", "health-monitoring"],
    "max_concurrent_requests": 50,
    "cache_enabled": True,
    "monitoring_enabled": True
}

# Global state for demo (in production, use proper database)
current_analysis_data = {}

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system with GSA Rules Pack"""
    await rag_system.initialize()
    print("✅ GetGSA system initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    return FileResponse("static/index.html")

@app.get("/healthz")
async def health_check():
    """Basic health check endpoint"""
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def enterprise_health_check():
    """🏥 Comprehensive enterprise health check with AI provider status"""
    try:
        ai_health = await ai_service.health_check()
        system_metrics = ai_service.get_performance_metrics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": ENTERPRISE_CONFIG["version"],
            "ai_providers": ai_health["providers"],
            "system_health": system_metrics["system_health"],
            "performance": {
                "avg_response_time": system_metrics["performance"]["average_response_time"],
                "success_rate": system_metrics["performance"]["overall_success_rate"],
                "cache_hit_rate": system_metrics["caching"]["cache_hit_rate"]
            },
            "features": ENTERPRISE_CONFIG["features"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/metrics")
async def get_performance_metrics():
    """📊 Enterprise performance metrics endpoint"""
    try:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": ai_service.get_performance_metrics(),
            "config": ENTERPRISE_CONFIG
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest and store documents with PII redaction
    """
    try:
        request_id = str(uuid.uuid4())
        doc_summaries = []
        
        for doc in request.documents:
            # Validate document size
            if len(doc.text) > 1048576:  # 1MB limit
                raise HTTPException(status_code=413, detail=f"Document {doc.name} too large")
            
            # Redact PII from the document
            redacted_text = pii_redactor.redact_text(doc.text)
            
            # Store the document
            doc_id = await document_storage.store_document(
                name=doc.name,
                original_text=doc.text,
                redacted_text=redacted_text,
                type_hint=doc.type_hint,
                request_id=request_id
            )
            
            doc_summaries.append({
                "doc_id": doc_id,
                "name": doc.name,
                "type_hint": doc.type_hint,
                "character_count": len(doc.text),
                "redacted_character_count": len(redacted_text),
                "pii_items_redacted": len(doc.text) - len(redacted_text)
            })
        
        # Store request metadata
        global current_analysis_data
        current_analysis_data[request_id] = {
            "documents": request.documents,
            "doc_summaries": doc_summaries,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return IngestResponse(
            doc_summaries=doc_summaries,
            request_id=request_id,
            message=f"Successfully ingested {len(request.documents)} documents"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_documents(request_id: Optional[str] = None):
    """
    Analyze the last ingested documents or specific request
    """
    try:
        # Get the most recent request if no ID provided
        if not request_id:
            if not current_analysis_data:
                raise HTTPException(status_code=400, detail="No documents to analyze")
            request_id = max(current_analysis_data.keys(), key=lambda k: current_analysis_data[k]["timestamp"])
        
        if request_id not in current_analysis_data:
            raise HTTPException(status_code=404, detail="Request ID not found")
        
        documents = current_analysis_data[request_id]["documents"]
        processing_start = time.time()
        
        # Process documents
        analysis_results = await document_processor.process_documents(documents)
        
        # Generate RAG-based checklist
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # Generate AI content with enterprise features (concurrent processing)
        brief_task = ai_service.generate_negotiation_brief(analysis_results, checklist)
        email_task = ai_service.generate_client_email(analysis_results, checklist)
        
        # Execute AI generation concurrently for better performance
        (brief, brief_meta), (client_email, email_meta) = await asyncio.gather(
            brief_task, email_task
        )
        
        # Get rule citations
        citations = rag_system.get_recent_citations()
        
        # Enhanced response with enterprise metadata
        response_data = {
            "parsed": analysis_results,
            "checklist": checklist,
            "brief": brief,
            "client_email": client_email,
            "citations": citations,
            "request_id": request_id,
            "enterprise_metadata": {
                "brief_generation": brief_meta,
                "email_generation": email_meta,
                "processing_time": time.time() - processing_start,
                "ai_providers_used": [brief_meta["provider"], email_meta["provider"]],
                "quality_scores": {
                    "brief": brief_meta.get("quality_score", 0),
                    "email": email_meta.get("quality_score", 0)
                }
            }
        }
        
        logger.info(f"🎆 Analysis complete for {request_id}: {len(checklist)} rules checked, AI: {brief_meta['provider']}/{email_meta['provider']}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)