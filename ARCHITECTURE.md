# GetGSA: AI + RAG System Architecture

## System Overview

GetGSA is an enterprise-grade AI-powered document processing system that combines advanced Retrieval-Augmented Generation (RAG) with multi-provider AI integration for GSA document analysis and compliance checking.

## Data Flow Architecture

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
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   AI Brief &    │
                    │   Email Gen     │
                    │   + UI Display  │
                    └─────────────────┘
```

## Component Architecture

### Core Components

1. **FastAPI Backend (`main.py`)**
   - RESTful API endpoints
   - Request/response handling
   - Error management
   - Health monitoring

2. **AI Service (`src/ai_service.py`)**
   - Multi-provider architecture (OpenAI GPT-4 + GROQ Llama3)
   - Intelligent fallback system
   - Prompt management and abstention handling
   - Performance caching

3. **RAG System (`src/rag_system.py`)**
   - Vector-based document retrieval
   - GSA Rules Pack (R1-R5) integration
   - Policy compliance checking
   - Citation tracking

4. **Document Processor (`src/document_processor.py`)**
   - Multi-format document ingestion
   - Field extraction and validation
   - Document classification
   - Structured data output

5. **PII Redactor (`src/pii_redactor.py`)**
   - Email and phone number detection
   - Secure redaction with preservation of structure
   - Compliance with data protection requirements

6. **Web Interface (`static/index.html`)**
   - Single-page application
   - Real-time processing dashboard
   - Interactive document upload
   - Results visualization

## AI Integration Points

### 1. Document Classification
- **Model**: OpenAI GPT-4 (primary) / GROQ Llama3 (fallback)
- **Purpose**: Classify documents as profile, past_performance, pricing, or unknown
- **Abstention**: Returns "unknown" with confidence scores when uncertain

### 2. RAG-Based Policy Checking
- **Vector Store**: SentenceTransformers all-MiniLM-L6-v2
- **Knowledge Base**: GSA Rules Pack (R1-R5)
- **Process**: 
  1. Query vectorization
  2. Similarity search against rule embeddings
  3. Rule citation and compliance validation

### 3. Brief and Email Generation
- **Model**: Multi-AI with template fallback
- **Inputs**: Extracted fields, compliance results, rule citations
- **Outputs**: Professional negotiation brief and client email

## Scalability Design (10 → 1,000 customers)

### Current Architecture Benefits
- **Stateless API**: Each request is independent
- **Async Processing**: Non-blocking I/O operations
- **Caching Layer**: Intelligent response caching
- **Modular Design**: Components can be scaled independently

### Scaling Strategy

#### Horizontal Scaling
```
Load Balancer
    │
    ├── API Instance 1 ────┐
    ├── API Instance 2 ────┤
    └── API Instance N ────┤
                           │
                           ▼
                    Shared Services
                    ├── Redis Cache
                    ├── Vector DB
                    └── Document Store
```

#### Queue-Based Processing
```
API Gateway → Message Queue → Worker Pool → Results Cache
     │             │              │             │
     └─── Sync ─────┘              └── Async ────┘
```

### Storage Strategy
- **Documents**: S3/MinIO for scalable file storage
- **Metadata**: PostgreSQL for structured data
- **Vectors**: Pinecone/Weaviate for vector search
- **Cache**: Redis for high-performance caching

## Extensibility: Adding "Pricing Pack v2"

### Current Plugin Architecture
```python
# Rule pack interface
class RulePack:
    def get_rules(self) -> List[Rule]
    def validate(self, document: Document) -> ValidationResult
```

### Adding New Rule Pack
1. **Create New Rule Pack**:
   ```python
   class PricingPackV2(RulePack):
       def get_rules(self):
           return [
               Rule("P2-1", "Advanced pricing validation"),
               Rule("P2-2", "Multi-tier rate structures"),
               # ... additional rules
           ]
   ```

2. **Register Rule Pack**:
   ```python
   rag_system.register_pack("pricing_v2", PricingPackV2())
   ```

3. **Version-aware Processing**:
   ```python
   def analyze_document(doc, rule_version="v1"):
       pack = rag_system.get_pack(f"pricing_{rule_version}")
       return pack.validate(doc)
   ```

### Backward Compatibility
- **Version Headers**: API accepts rule pack versions
- **Feature Flags**: Toggle new features per customer
- **Migration Tools**: Automatic upgrade paths

## Performance Characteristics

### Response Times (Target)
- **Document Ingestion**: < 2 seconds
- **Field Extraction**: < 1 second
- **RAG Analysis**: < 3 seconds  
- **Brief Generation**: < 5 seconds

### Throughput (Target)
- **Concurrent Users**: 100+
- **Documents/Hour**: 1,000+
- **API Requests/Second**: 50+

## Security Architecture

### Data Protection
- **PII Redaction**: Real-time email/phone masking
- **Encryption**: TLS 1.3 for data in transit
- **Access Control**: API key-based authentication
- **Audit Logging**: Complete request/response tracking

### Input Validation
- **Size Limits**: 10MB per document
- **Rate Limiting**: 100 requests/minute per API key
- **Content Filtering**: Malicious content detection

## Monitoring & Observability

### Health Checks
- **API Health**: `/healthz` endpoint
- **Component Status**: Individual service monitoring
- **Performance Metrics**: Response time tracking

### Logging Strategy
- **Structured Logging**: JSON format for analysis
- **Error Tracking**: Exception monitoring
- **Performance Profiling**: Slow query detection

---

*Architecture designed by Rajan Mishra - Senior AI Solutions Architect*
*Built for enterprise scale with professional reliability*