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
                r'uei[:\s\(]*(?:unique entity identifier[:\s]*)?([a-zA-Z0-9]{12})',
                r'duns[:\s\(]*(?:number[:\s]*)?([0-9]{9})',
                r'naics[:\s]*(?:code[:\s]*)?([0-9]{6})',
                r'sam[\s\.]*(?:gov|registration)',
                r'(?:business\s+)?address[:\s]+',
                r'(?:primary\s+)?contact[:\s]+|poc[:\s]+'
            ],
            "past_performance": [
                r'customer[:\s]+[a-zA-Z\s]+',
                r'(?:contract|value)[:\s]+.*\$[0-9,]+',
                r'period[:\s]+[0-9]{4}',
                r'contact[:\s]+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'performance[:\s]+[a-zA-Z\s]+'
            ],
            "pricing": [
                r'labor\s+categor(?:y|ies)',
                r'(?:rate|hour)[:\s]*\$[0-9]+',
                r'(?:hourly|per\s+hour)',
                r'(?:senior|junior)\s+(?:developer|analyst|manager)',
                r'pricing[:\s]*(?:structure|information)'
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
            
            # Extract ALL types of data from every document (not just classified type)
            # This ensures we don't miss GSA compliance data regardless of classification
            
            # Always try to extract company profile data
            profile_data = self._extract_company_profile(doc.text)
            if profile_data:  # Only update if we found data
                results["company_profile"].update(profile_data)
            
            # Always try to extract past performance data
            pp_data = self._extract_past_performance(doc.text, doc.name)
            if pp_data and pp_data.get("contracts"):  # Only add if we found contracts
                results["past_performance"].extend(pp_data["contracts"])
            elif pp_data:  # If we got data but in wrong format, handle it
                results["past_performance"].append(pp_data)
            
            # Always try to extract pricing data
            pricing_data = self._extract_pricing(doc.text)
            if pricing_data:  # Only extend if we found pricing data
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
        
        best_type = max(scores.keys(), key=lambda k: scores[k])
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
        """Extract company profile information with enhanced GSA compliance detection"""
        profile = {}
        
        # Extract UEI - Enhanced patterns
        uei_patterns = [
            r'uei[:\s]*(?:\(unique entity identifier\)[:\s]*)?([a-zA-Z0-9]{12})',
            r'uei[:\s]*(?:unique entity identifier[:\s]*)?([a-zA-Z0-9]{12})',
            r'unique\s+entity\s+identifier[:\s]*([a-zA-Z0-9]{12})',
            r'uei\s*\([^)]*\)[:\s]*([a-zA-Z0-9]{12})'
        ]
        for pattern in uei_patterns:
            uei_match = re.search(pattern, text, re.IGNORECASE)
            if uei_match:
                profile["uei"] = uei_match.group(1)
                break
        
        # Extract DUNS - Enhanced patterns
        duns_patterns = [
            r'duns[:\s]*(?:number[:\s]*)?([0-9]{9})',
            r'duns\s+number[:\s]*([0-9]{9})'
        ]
        for pattern in duns_patterns:
            duns_match = re.search(pattern, text, re.IGNORECASE)
            if duns_match:
                profile["duns"] = duns_match.group(1)
                break
        
        # Extract SAM status - Enhanced patterns
        sam_patterns = [
            r'sam[:\s]*(?:registration[:\s]*)?(?:status[:\s]*)?(active|inactive)',
            r'sam\.gov[:\s]*(?:status[:\s]*)?(active|inactive)',
            r'registration[:\s]*(?:status[:\s]*)?(active|inactive)'
        ]
        for pattern in sam_patterns:
            sam_match = re.search(pattern, text, re.IGNORECASE)
            if sam_match:
                profile["sam_status"] = sam_match.group(1).lower()
                break
        
        # Extract NAICS codes - Enhanced patterns
        naics_patterns = [
            r'naics[:\s]*(?:code[:\s]*)?([0-9]{6})',
            r'primary\s+naics[:\s]*(?:code[:\s]*)?([0-9]{6})',
            r'naics\s+code[:\s]*([0-9]{6})'
        ]
        naics_codes = []
        for pattern in naics_patterns:
            naics_matches = re.findall(pattern, text, re.IGNORECASE)
            naics_codes.extend(naics_matches)
        
        if naics_codes:
            profile["naics"] = list(set(naics_codes))  # Remove duplicates
        
        # Extract contact information - Enhanced patterns
        contact = {}
        
        # Extract name (after POC: or Contact:)
        name_patterns = [
            r'(?:primary\s+)?(?:poc|contact)[:\s]+([^,\n\r]+)',
            r'primary\s+contact[:\s]+([^,\n\r]+)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                contact["name"] = name_match.group(1).strip()
                break
        
        # Extract email - Enhanced patterns
        email_patterns = [
            r'(?:primary\s+)?(?:contact\s+)?email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        for pattern in email_patterns:
            email_match = re.search(pattern, text, re.IGNORECASE)
            if email_match:
                contact["email"] = email_match.group(1)
                break
        
        # Extract phone - Enhanced patterns
        phone_patterns = [
            r'(?:primary\s+)?(?:contact\s+)?phone[:\s]*(\([0-9]{3}\)\s*[0-9]{3}[-\s]?[0-9]{4})',
            r'(?:primary\s+)?(?:contact\s+)?phone[:\s]*([0-9]{3}[-\s][0-9]{3}[-\s][0-9]{4})',
            r'(\([0-9]{3}\)\s*[0-9]{3}[-\s]?[0-9]{4})',
            r'([0-9]{3}[-\s][0-9]{3}[-\s][0-9]{4})'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text, re.IGNORECASE)
            if phone_match:
                contact["phone"] = phone_match.group(1)
                break
        
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
            pp["value"] = int(value_str)  # type: ignore[assignment]
        
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
        
        # Pattern 1: Look for line-by-line format (- Category: $rate/unit)
        line_patterns = [
            r'-\s*([^:]+):\s*\$?(\d+(?:\.\d+)?)\s*/?(.+)',
            r'•\s*([^:]+):\s*\$?(\d+(?:\.\d+)?)\s*/?(.+)',
            r'\*\s*([^:]+):\s*\$?(\d+(?:\.\d+)?)\s*/?(.+)'
        ]
        
        for pattern in line_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                category, rate, unit = match
                pricing_items.append({
                    "category": category.strip(),
                    "rate": float(rate),
                    "unit": unit.strip()
                })
        
        # Pattern 2: Look for tabular data
        if not pricing_items:
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
                    
                    if len(parts) >= 2:
                        rate_val = self._parse_numeric(parts[1].strip())
                        if rate_val:
                            item = {
                                "category": parts[0].strip(),
                                "rate": rate_val,
                                "unit": parts[2].strip() if len(parts) > 2 else "hour"
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