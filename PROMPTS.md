# GetGSA AI Prompts & Reasoning Strategy

## AI Integration Overview

GetGSA uses AI at three critical points:
1. **Document Classification** - Determining document types
2. **RAG-Based Policy Validation** - Compliance checking with citations
3. **Brief & Email Generation** - Professional communication drafting

## 1. Document Classification

### Primary Prompt (OpenAI GPT-4)
```
You are a GSA document classification expert. Analyze the following document text and classify it into one of these categories:

CATEGORIES:
- "profile": Company information, UEI, DUNS, NAICS codes, contact details
- "past_performance": Contract history, customer references, project details
- "pricing": Labor categories, rates, pricing structures
- "unknown": Cannot determine or mixed content

RULES:
1. Be conservative - if uncertain, return "unknown"
2. Look for key indicators:
   - Profile: UEI, DUNS, company name, SAM.gov
   - Past Performance: customer names, contract values, dates
   - Pricing: rates, labor categories, billing units
3. If document contains multiple types, classify by dominant content (>60%)
4. Return only the category name, nothing else

ABSTENTION: If confidence < 70%, return "unknown"

Document text:
{document_text}

Classification:
```

### Fallback Prompt (GROQ Llama3)
```
Classify this GSA document. Return ONLY one word: profile, past_performance, pricing, or unknown.

Key patterns:
- profile: UEI/DUNS numbers, company info
- past_performance: contracts, customers, values
- pricing: rates, labor categories
- unknown: unclear or mixed

Be conservative. If unsure, return "unknown".

Text: {document_text}

Answer:
```

### Abstention Policy
- **Confidence Threshold**: 70%
- **Mixed Content**: If document spans multiple categories with <60% dominance
- **Insufficient Data**: Less than 50 words or mostly structured data
- **Ambiguous Indicators**: Conflicting classification signals

## 2. RAG-Based Policy Validation

### Policy Retrieval Prompt
```
You are a GSA compliance expert. Based on the retrieved policy rules, validate the extracted document fields and identify any compliance issues.

RETRIEVED RULES:
{retrieved_rules}

EXTRACTED FIELDS:
{extracted_fields}

VALIDATION TASK:
1. Check each field against applicable rules
2. Identify missing required information
3. Flag any compliance violations
4. Cite specific rule IDs (R1, R2, R3, R4, R5) for each finding

RESPONSE FORMAT:
{
  "required_ok": boolean,
  "problems": [
    {
      "issue": "missing_uei",
      "rule_id": "R1",
      "description": "UEI is required but not found"
    }
  ]
}

Be thorough but only flag actual violations. Cite rules accurately.
```

### Rule Citation Strategy
- **Exact Match**: Direct rule violation citations
- **Semantic Match**: Related rule applications with confidence scores
- **Multiple Rules**: When validation requires multiple rule checks
- **No Hallucination**: Only cite rules actually retrieved from vector store

## 3. Brief & Email Generation

### Negotiation Brief Prompt
```
You are a GSA contract negotiation expert. Create a professional negotiation preparation brief based on the compliance analysis.

COMPLIANCE RESULTS:
{compliance_results}

RULE CITATIONS:
{rule_citations}

BRIEF REQUIREMENTS:
1. 2-3 paragraphs maximum
2. Highlight strengths and weaknesses
3. Specific negotiation leverage points
4. Cite GSA rules where relevant (R1-R5)
5. Focus on business impact and risk mitigation

TONE: Professional, analytical, actionable
FORMAT: Business memo style

Generate the brief:
```

### Client Email Prompt
```
Write a professional, polite email to a potential GSA contractor summarizing missing documentation and next steps.

MISSING ITEMS:
{missing_items}

COMPLIANCE ISSUES:
{compliance_issues}

EMAIL REQUIREMENTS:
1. Professional and helpful tone
2. Clear list of missing items
3. Specific next steps
4. Deadline for completion (suggest 10 business days)
5. Offer assistance if needed

FORMAT: Standard business email
LENGTH: Concise but complete

Draft the email:
```

## Abstention Handling

### When AI Should Abstain

1. **Low Confidence Scenarios**:
   - Classification confidence < 70%
   - Ambiguous document content
   - Insufficient context for validation

2. **Data Quality Issues**:
   - Corrupted or illegible text
   - Extremely short documents (< 50 words)
   - Non-English content without translation

3. **Complex Edge Cases**:
   - Mixed document types
   - Conflicting information
   - Novel document formats

### Abstention Response Format
```json
{
  "result": null,
  "abstention": true,
  "reason": "insufficient_context",
  "confidence": 0.45,
  "human_review_required": true,
  "suggestions": [
    "Request clearer document scan",
    "Provide document type hint",
    "Manual review recommended"
  ]
}
```

## Prompt Engineering Best Practices

### 1. Clarity & Specificity
- Clear task definition
- Specific output format requirements
- Concrete examples when helpful
- Unambiguous success criteria

### 2. Context Management
- Relevant context only (avoid information overload)
- Structured input formatting
- Clear parameter boundaries
- Consistent terminology

### 3. Error Prevention
- Conservative confidence thresholds
- Explicit abstention instructions
- Validation rules within prompts
- Fallback behavior specification

### 4. Consistency
- Standardized prompt templates
- Consistent response formats
- Uniform citation methods
- Predictable abstention behavior

## Model-Specific Optimizations

### OpenAI GPT-4
- **Strengths**: Complex reasoning, context understanding
- **Optimal Use**: Policy validation, brief generation
- **Token Management**: Efficient context use, clear delimiters

### GROQ Llama3
- **Strengths**: Fast inference, consistent formatting
- **Optimal Use**: Classification, structured output
- **Prompt Style**: Concise, direct instructions

### Template Fallback
- **Use Case**: When both AI providers fail
- **Method**: Rule-based classification and template responses
- **Quality**: Consistent but less sophisticated than AI

## Monitoring & Improvement

### Prompt Performance Metrics
- **Classification Accuracy**: Validation against manual labels
- **Abstention Rate**: Percentage of uncertain responses
- **Citation Accuracy**: Correct rule ID references
- **Response Quality**: Human evaluation scores

### Continuous Improvement
- **A/B Testing**: Compare prompt variations
- **Feedback Integration**: User correction incorporation
- **Model Updates**: Adaptation to new model versions
- **Domain Expansion**: New rule types and document formats

---

*Prompts engineered by Rajan Mishra - Senior AI Solutions Architect*
*Optimized for accuracy, reliability, and professional output quality*