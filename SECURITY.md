# GetGSA Security & Data Protection

## Security Overview

GetGSA implements enterprise-grade security measures to protect sensitive GSA contractor information, ensure PII compliance, and prevent system abuse.

## PII Redaction Strategy

### Scope of PII Protection

**Protected Information Types:**
- Email addresses (all formats)
- Phone numbers (US and international formats)
- Social Security Numbers (if detected)
- Credit card numbers (if accidentally included)

**Redaction Method:**
- **Emails**: Replace with `[EMAIL_REDACTED_X]` where X is incremental ID
- **Phones**: Replace with `[PHONE_REDACTED_X]` with format preservation
- **Pattern**: `[TYPE_REDACTED_ID]` for consistent identification

### Implementation Details

```python
# Email redaction patterns
EMAIL_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'
]

# Phone redaction patterns  
PHONE_PATTERNS = [
    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    r'\+1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
]
```

### Storage Strategy

**Original Documents:**
- Stored with full PII redaction
- Encrypted at rest (AES-256)
- Access logged and monitored

**Extracted Fields:**
- PII stored separately in secure field store
- Encrypted with different key from documents
- Access controlled by role-based permissions

**Processing Flow:**
1. Document received → Immediate PII scan
2. Redacted version stored for analysis
3. Original PII stored in secure field vault
4. Analysis performed on redacted version only

## Input Validation & Limits

### Document Size Limits
- **Maximum file size**: 10MB per document
- **Maximum batch size**: 50MB total per request
- **Text length limit**: 100,000 characters after extraction
- **Timeout**: 30 seconds per document processing

### Content Validation
```python
VALIDATION_RULES = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "max_text_length": 100000,
    "allowed_mime_types": [
        "text/plain",
        "application/pdf", 
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ],
    "max_documents_per_request": 20
}
```

### Malicious Content Detection
- **Script injection**: HTML/JS tag filtering
- **File type validation**: Magic number verification
- **Content scanning**: Malware signature checking
- **Encoding validation**: UTF-8 compliance checking

## API Security

### Authentication
- **API Key Required**: All endpoints except `/healthz`
- **Key Format**: 32-character alphanumeric tokens
- **Key Management**: Rotation every 90 days recommended
- **Environment Storage**: Keys stored in environment variables only

### Rate Limiting
```python
RATE_LIMITS = {
    "requests_per_minute": 100,
    "documents_per_hour": 500,
    "data_volume_per_hour": "500MB",
    "concurrent_requests": 10
}
```

### Request Validation
- **Content-Type**: Enforced JSON for POST requests
- **Request Size**: Limited to 50MB total
- **Parameter Validation**: Strict input sanitization
- **SQL Injection**: Parameterized queries only

## Data Encryption

### Encryption at Rest
- **Document Storage**: AES-256-GCM
- **Database**: TDE (Transparent Data Encryption)
- **Key Management**: AWS KMS / Azure Key Vault
- **Rotation**: Automatic 90-day key rotation

### Encryption in Transit
- **TLS Version**: TLS 1.3 minimum
- **Certificate**: RSA 2048-bit or ECDSA P-256
- **HSTS**: Strict-Transport-Security enforced
- **Certificate Pinning**: Production environments

## Access Control

### Role-Based Access Control (RBAC)
```
Administrator:
  - Full system access
  - User management
  - Security configuration

Analyst:
  - Document processing
  - Results viewing
  - Report generation

Viewer:
  - Read-only access
  - Report viewing only
```

### API Endpoint Security
```
POST /ingest:
  - Authentication required
  - Rate limited
  - Input validation
  - PII redaction

POST /analyze:
  - Authentication required
  - Request ID validation
  - Result caching

GET /healthz:
  - Public access
  - No sensitive data
```

## Audit & Compliance

### Logging Strategy
```python
AUDIT_EVENTS = {
    "document_uploaded": {
        "timestamp": "ISO-8601",
        "user_id": "string",
        "document_hash": "SHA-256",
        "file_size": "bytes",
        "pii_detected": "boolean"
    },
    "analysis_performed": {
        "timestamp": "ISO-8601", 
        "request_id": "UUID",
        "processing_time": "milliseconds",
        "ai_providers_used": "list"
    }
}
```

### Compliance Standards
- **GDPR**: Right to deletion, data portability
- **CCPA**: California Consumer Privacy Act compliance
- **SOC 2 Type II**: Security, availability, confidentiality
- **NIST Cybersecurity Framework**: Implementation guidelines

## Abuse Prevention

### Anti-Automation Measures
- **Request pattern analysis**: Unusual usage detection
- **IP-based rate limiting**: Per-IP address quotas
- **Behavioral analysis**: Suspicious activity flagging
- **CAPTCHA integration**: Human verification when needed

### Resource Protection
```python
RESOURCE_LIMITS = {
    "cpu_timeout": 30,  # seconds
    "memory_limit": "512MB",
    "disk_usage": "1GB",
    "network_requests": 100  # per processing session
}
```

### DDoS Protection
- **Rate limiting**: Aggressive limits during attacks
- **Geographic blocking**: Suspicious region filtering
- **Traffic shaping**: Bandwidth management
- **CDN integration**: Distributed load handling

## Incident Response

### Security Incident Classification
```
Critical (P0):
  - Data breach confirmed
  - System compromise
  - PII exposure

High (P1):
  - Unauthorized access attempt
  - Service disruption
  - Security control failure

Medium (P2):
  - Policy violation
  - Unusual activity patterns
  - Performance degradation

Low (P3):
  - Minor configuration issues
  - User access problems
  - Documentation updates
```

### Response Procedures
1. **Detection**: Automated monitoring + manual reporting
2. **Assessment**: Impact evaluation within 1 hour
3. **Containment**: Immediate threat mitigation
4. **Eradication**: Root cause elimination
5. **Recovery**: Service restoration with monitoring
6. **Lessons Learned**: Post-incident review and improvement

## Security Monitoring

### Real-Time Monitoring
- **Failed authentication attempts**: Alert after 5 failures
- **Unusual API usage patterns**: Statistical anomaly detection
- **System performance**: Response time and error rate monitoring
- **Data access patterns**: Abnormal query detection

### Security Metrics
```python
SECURITY_METRICS = {
    "authentication_success_rate": "> 95%",
    "api_response_time": "< 2 seconds",
    "error_rate": "< 1%",
    "pii_redaction_accuracy": "> 99.9%"
}
```

## Privacy by Design

### Data Minimization
- **Collection**: Only necessary data collected
- **Processing**: Minimal data used for analysis
- **Storage**: Automatic deletion after retention period
- **Access**: Least privilege principle

### Consent Management
- **Explicit Consent**: Required for all PII processing
- **Granular Control**: Per-data-type permissions
- **Withdrawal**: Easy consent revocation process
- **Audit Trail**: Complete consent history tracking

---

*Security architecture designed by Rajan Mishra - Senior AI Solutions Architect*
*Enterprise-grade protection for sensitive GSA contractor information*