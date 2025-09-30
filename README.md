# 🎯 GetGSA: Enterprise AI + RAG System
## Advanced GSA Document Processing & Compliance Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production--Ready-brightgreen.svg)]()

> **🏆 Built by Rajan Mishra** - Senior AI Solutions Architect | 6+ Years Enterprise AI Experience

A professional-grade AI system that revolutionizes GSA document processing through intelligent automation, advanced RAG technology, and multi-provider AI integration. Built to enterprise standards with comprehensive testing and security.

---

## 🚀 Quick Start

### One-Command Startup
```bash
# Windows - Double-click this file:
START_GETGSA.bat

# Or run the smart startup script:
python start_getgsa.py
```

### Manual Setup
```bash
# 1. Clone the repository
git clone https://github.com/Rajanm001/GetGSA-AI-RAG-System.git
cd GetGSA-AI-RAG-System

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API keys (optional - has fallback modes)
echo "OPENAI_API_KEY=your_key_here" > .env
echo "GROQ_API_KEY=your_key_here" >> .env
```

### Access Points
- 🌐 **Web Interface**: http://127.0.0.1:8001
- 📚 **API Documentation**: http://127.0.0.1:8001/docs
- ❤️ **Health Check**: http://127.0.0.1:8001/health

---

## ✨ Core Features

### 🤖 AI-Powered Processing
- **Multi-Provider AI**: OpenAI GPT-4 + GROQ Llama3 with intelligent fallback
- **Document Classification**: Automatic categorization of GSA documents
- **Smart Abstention**: AI knows when to defer to human review

### 🧠 Advanced RAG System
- **GSA Rules Pack**: Built-in knowledge of R1-R5 compliance rules
- **Vector Search**: Semantic similarity matching for policy validation
- **Citation Tracking**: Precise rule references in all outputs

### 🛡️ Enterprise Security
- **PII Redaction**: Automatic email/phone number masking
- **Secure Storage**: Encrypted document handling
- **Access Control**: API key-based authentication

### 📊 Professional Outputs
- **Negotiation Briefs**: AI-generated strategic analysis
- **Client Emails**: Professional communication drafts
- **Compliance Reports**: Detailed validation with citations

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   AI Service    │    │   RAG System    │
│   Ingestion     │───▶│  (Multi-AI)     │───▶│  (GSA Rules)    │
│   + PII Filter  │    │  Classification │    │   Compliance    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Secure        │    │   Field         │    │   Policy        │
│   Storage       │    │   Extraction    │    │   Validation    │
│   (Redacted)    │    │   + Validation  │    │   + Citations   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📋 API Endpoints

### Core Endpoints
- `POST /ingest` - Document ingestion with PII redaction
- `POST /analyze` - Comprehensive analysis with AI classification
- `GET /healthz` - System health monitoring

### Sample Request
```json
POST /ingest
{
  "documents": [
    {
      "name": "company_profile.txt",
      "type_hint": "profile",
      "text": "Acme Corp\nUEI: ABC123DEF456\nDUNS: 123456789..."
    }
  ]
}
```

### Sample Response
```json
{
  "parsed": {
    "uei": "ABC123DEF456",
    "duns": "123456789",
    "classification": "profile"
  },
  "checklist": {
    "required_ok": true,
    "problems": []
  },
  "brief": "Professional negotiation analysis...",
  "client_email": "Professional email draft...",
  "citations": [{"rule_id": "R1", "evidence": "..."}]
}
```

---

## 🧪 Testing & Validation
```bash
python -m pytest tests/ -v
```

### Comprehensive Test Suite
```bash
# Run all tests
python test_runner.py

# Sample test coverage:
✅ Missing UEI detection (R1 validation)
✅ Past performance thresholds (R3 validation)  
✅ NAICS SIN mapping (R2 validation)
✅ PII redaction (R5 compliance)
✅ RAG system integrity (Rule removal testing)
```

---

## 🎯 Requirements Compliance

### ✅ All 7 Core Requirements Implemented:

1. **✅ Document Ingestion & Classification** - Multi-format AI classification
2. **✅ Field Extraction & Validation** - Comprehensive data extraction  
3. **✅ RAG-Based Policy Checking** - GSA Rules Pack with citations
4. **✅ PII Redaction & Security** - Enterprise-grade data protection
5. **✅ AI Brief & Email Generation** - Professional communications
6. **✅ Single-Page UI & API** - Complete web interface + REST API
7. **✅ Comprehensive Test Harness** - Automated validation suite

---

## 👨‍💻 About the Developer

**Rajan Mishra** - Senior AI Solutions Architect
- 6+ years of enterprise AI development
- Expert in RAG systems and multi-AI architectures
- Specialized in production-ready AI solutions

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and scalability
- **[PROMPTS.md](PROMPTS.md)** - AI prompts and reasoning strategy  
- **[SECURITY.md](SECURITY.md)** - Security measures and compliance

---

*Built with precision, designed for scale, optimized for performance.* 🚀