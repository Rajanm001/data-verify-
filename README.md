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

### Access Points (After Local Setup)
- 🌐 **Web Interface**: `http://127.0.0.1:8001` (runs locally after setup)
- 📚 **API Documentation**: `http://127.0.0.1:8001/docs` (interactive API docs)
- ❤️ **Health Check**: `http://127.0.0.1:8001/health` (system status)

---

## 🖥️ Live Demo & Screenshots

### System Interface Preview
```
🎯 GetGSA System Dashboard
┌─────────────────────────────────────────────────────────────┐
│ 📁 Upload Documents    🔍 Analyze    📊 Results           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 Document Upload Area                                   │
│     • Drag & drop PDF/DOCX/TXT files                      │
│     • Or click to select files                            │
│                                                             │
│  🤖 AI Processing Status                                   │
│     ✅ Classification Complete                             │
│     ✅ Field Extraction Complete                          │
│     ✅ RAG Analysis Complete                              │
│     ✅ PII Redaction Applied                              │
│                                                             │
│  📊 Results Dashboard                                      │
│     • Extracted Fields (UEI, DUNS, NAICS)                │
│     • Compliance Checklist with Rule Citations           │
│     • AI-Generated Negotiation Brief                     │
│     • Professional Client Email Draft                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Quick Start Commands
```bash
# Clone and run locally
git clone https://github.com/Rajanm001/data-verify-.git
cd data-verify-
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python start_getgsa.py
```

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

## � API Documentation

### REST API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest` | POST | Upload and process documents with PII redaction |
| `/analyze` | POST | Run comprehensive AI analysis and compliance check |
| `/healthz` | GET | System health and status monitoring |

### Example API Usage

#### Document Upload
```bash
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "name": "company_profile.txt",
      "type_hint": "profile", 
      "text": "Acme Corp\nUEI: ABC123DEF456\nDUNS: 123456789\nNAICS: 541511"
    }]
  }'
```

#### Analysis Response
```json
{
  "request_id": "uuid-12345",
  "parsed": {
    "uei": "ABC123DEF456",
    "duns": "123456789", 
    "classification": "profile",
    "naics_codes": ["541511"]
  },
  "checklist": {
    "required_ok": true,
    "problems": [],
    "compliance_score": 95
  },
  "brief": "Strong compliance profile with all required fields...",
  "client_email": "Thank you for your submission. All required...",
  "citations": [
    {"rule_id": "R1", "evidence": "UEI and DUNS validation passed"}
  ]
}
```

**📚 Interactive API Docs**: Available at `/docs` when running locally

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