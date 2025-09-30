"""
Document Processor with AI-powered classification and field extraction
"""

import re
from typing import List, Dict, Any, Optional
import json

from src.models import Document, ClassificationResult, ExtractedField

class DocumentProcessor:
    def __init__(self):
        self.classification_patterns = {
            "company_profile": [
                r'uei[:\s]+([a-zA-Z0-9]{12})',
                r'duns[:\s]+(\d{9})',
                r'naics[:\s]+',
                r'sam\.gov',
                r'address[:\s]+',
                r'poc[:\s]+|primary contact'
            ],
            "past_performance": [
                r'customer[:\s]+',
                r'contract[:\s]+',
                r'value[:\s]+\$',
                r'period[:\s]+',
                r'contact[:\s]+.*@'
            ],
            "pricing": [
                r'labor category',
                r'rate[:\s]+',
                r'hour|hourly',
                r'senior developer|project manager|analyst'
            ]
        }
    
    async def process_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Process documents with AI-powered classification and field extraction
        """
        results = {
            "classifications": [],
            "company_profile": {},
            "past_performance": [],
            "pricing": [],
            "extracted_fields": []
        }
        
        for doc in documents:
            # Classify document
            classification = await self._classify_document(doc)
            results["classifications"].append(classification)
            
            # Extract fields based on classification
            if not classification.abstained:
                if classification.predicted_type == "company_profile":
                    profile_data = self._extract_company_profile(doc.text)
                    results["company_profile"].update(profile_data)
                    
                elif classification.predicted_type == "past_performance":
                    pp_data = self._extract_past_performance(doc.text, doc.name)
                    results["past_performance"].append(pp_data)
                    
                elif classification.predicted_type == "pricing":
                    pricing_data = self._extract_pricing(doc.text)
                    results["pricing"].extend(pricing_data)
        
        return results
    
    async def _classify_document(self, document: Document) -> ClassificationResult:
        """
        Classify document type using pattern matching with confidence scoring
        """
        text_lower = document.text.lower()
        scores = {}
        
        # Score each document type based on pattern matches
        for doc_type, patterns in self.classification_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
                    score += 1
            
            # Normalize score
            if len(patterns) > 0:
                scores[doc_type] = matches / len(patterns)
            else:
                scores[doc_type] = 0
        
        # Determine best classification
        if not scores or max(scores.values()) == 0:
            return ClassificationResult(
                document_name=document.name,
                predicted_type="unknown",
                confidence=0.0,
                abstained=True,
                reason="No clear patterns detected - requires human review"
            )
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # Use type hint if provided and confidence is low
        if document.type_hint and confidence < 0.5:
            if document.type_hint in self.classification_patterns:
                return ClassificationResult(
                    document_name=document.name,
                    predicted_type=document.type_hint,
                    confidence=0.6,  # Moderate confidence from hint
                    abstained=False,
                    reason="Classification based on provided type hint"
                )
        
        # Abstain if confidence is too low
        if confidence < 0.3:
            return ClassificationResult(
                document_name=document.name,
                predicted_type="unknown",
                confidence=confidence,
                abstained=True,
                reason=f"Low confidence ({confidence:.2f}) - requires human review"
            )
        
        return ClassificationResult(
            document_name=document.name,
            predicted_type=best_type,
            confidence=confidence,
            abstained=False
        )
    
    def _extract_company_profile(self, text: str) -> Dict[str, Any]:
        """Extract company profile information"""
        profile = {}
        
        # Extract UEI
        uei_match = re.search(r'uei[:\s]+([a-zA-Z0-9]{12})', text, re.IGNORECASE)
        if uei_match:
            profile["uei"] = uei_match.group(1)
        
        # Extract DUNS
        duns_match = re.search(r'duns[:\s]+(\d{9})', text, re.IGNORECASE)
        if duns_match:
            profile["duns"] = duns_match.group(1)
        
        # Extract SAM status
        if re.search(r'sam\.gov[:\s]+registered', text, re.IGNORECASE):
            profile["sam_status"] = "registered"
        elif re.search(r'sam\.gov', text, re.IGNORECASE):
            profile["sam_status"] = "unknown"
        
        # Extract NAICS codes
        naics_matches = re.findall(r'\b(\d{6})\b', text)
        if naics_matches:
            profile["naics"] = [int(code) for code in naics_matches if code.startswith(('5', '4'))]
        
        # Extract contact information
        contact = {}
        
        # Extract name (after POC: or Contact:)
        name_match = re.search(r'(?:poc|primary contact|contact)[:\s]+([^,\n]+)', text, re.IGNORECASE)
        if name_match:
            contact["name"] = name_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            contact["email"] = email_match.group(1)
        
        # Extract phone
        phone_match = re.search(r'(\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\(\d{3}\)\s*\d{3}\s*\d{4})', text)
        if phone_match:
            contact["phone"] = phone_match.group(1)
        
        if contact:
            profile["contact"] = contact
        
        # Extract company name
        lines = text.split('\n')
        if lines:
            # Usually company name is on the first line
            first_line = lines[0].strip()
            if first_line and not re.match(r'^\s*(company|profile)', first_line, re.IGNORECASE):
                profile["company_name"] = first_line
        
        return profile
    
    def _extract_past_performance(self, text: str, doc_name: str) -> Dict[str, Any]:
        """Extract past performance information"""
        pp = {"source_document": doc_name}
        
        # Extract customer
        customer_match = re.search(r'customer[:\s]+([^\n]+)', text, re.IGNORECASE)
        if customer_match:
            pp["customer"] = customer_match.group(1).strip()
        
        # Extract contract description
        contract_match = re.search(r'contract[:\s]+([^\n]+)', text, re.IGNORECASE)
        if contract_match:
            pp["contract"] = contract_match.group(1).strip()
        
        # Extract value
        value_match = re.search(r'value[:\s]+\$([0-9,]+)', text, re.IGNORECASE)
        if value_match:
            value_str = value_match.group(1).replace(',', '')
            pp["value"] = int(value_str)
        
        # Extract period
        period_match = re.search(r'period[:\s]+([^\n]+)', text, re.IGNORECASE)
        if period_match:
            pp["period"] = period_match.group(1).strip()
        
        # Extract contact email
        contact_match = re.search(r'contact[:\s]+[^,]*,?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
        if contact_match:
            pp["contact_email"] = contact_match.group(1)
        
        return pp
    
    def _extract_pricing(self, text: str) -> List[Dict[str, Any]]:
        """Extract pricing information"""
        pricing_items = []
        
        # Look for tabular data
        lines = text.split('\n')
        
        # Find header line
        header_line = None
        data_start = 0
        
        for i, line in enumerate(lines):
            if 'labor category' in line.lower() or 'rate' in line.lower():
                header_line = line
                data_start = i + 1
                break
        
        if header_line:
            # Parse data lines
            for line in lines[data_start:]:
                line = line.strip()
                if not line:
                    continue
                
                # Split by comma or multiple spaces
                parts = re.split(r',|\s{2,}', line)
                
                if len(parts) >= 3:
                    item = {
                        "category": parts[0].strip(),
                        "rate": self._parse_numeric(parts[1].strip()),
                        "unit": parts[2].strip()
                    }
                    pricing_items.append(item)
        
        return pricing_items
    
    def _parse_numeric(self, value: str) -> Optional[float]:
        """Parse numeric value from string"""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', value)
            return float(cleaned) if cleaned else None
        except ValueError:
            return None