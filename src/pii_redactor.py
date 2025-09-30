"""
PII Redaction System
Redacts personally identifiable information (emails, phone numbers) from documents
"""

import re
from typing import Dict, List, Tuple

class PIIRedactor:
    def __init__(self):
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            re.IGNORECASE
        )
        
        # Phone number patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}'),  # (415) 555-0100
            re.compile(r'\(\d{3}\)\s*\d{3}\s*\d{4}'),  # (415) 555 0100
            re.compile(r'\d{3}-\d{3}-\d{4}'),  # 415-555-0100
            re.compile(r'\d{3}\.\d{3}\.\d{4}'),  # 415.555.0100
            re.compile(r'\d{10}'),  # 4155550100 (only if not part of longer number)
        ]
        
        # Redaction placeholders
        self.email_placeholder = "[EMAIL_REDACTED]"
        self.phone_placeholder = "[PHONE_REDACTED]"
    
    def redact_text(self, text: str) -> str:
        """
        Redact PII (emails and phone numbers) from text
        Returns the redacted text
        """
        redacted_text = text
        
        # Redact emails
        redacted_text = self.email_pattern.sub(self.email_placeholder, redacted_text)
        
        # Redact phone numbers
        for pattern in self.phone_patterns:
            redacted_text = pattern.sub(self.phone_placeholder, redacted_text)
        
        return redacted_text
    
    def find_pii_items(self, text: str) -> Dict[str, List[str]]:
        """
        Find all PII items in text without redacting
        Returns dict with 'emails' and 'phones' lists
        """
        pii_items = {
            "emails": [],
            "phones": []
        }
        
        # Find emails
        email_matches = self.email_pattern.findall(text)
        pii_items["emails"] = list(set(email_matches))  # Remove duplicates
        
        # Find phone numbers
        phone_matches = []
        for pattern in self.phone_patterns:
            matches = pattern.findall(text)
            phone_matches.extend(matches)
        
        pii_items["phones"] = list(set(phone_matches))  # Remove duplicates
        
        return pii_items
    
    def redact_with_mapping(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redact PII and return mapping of placeholders to original values
        Returns (redacted_text, mapping_dict)
        """
        redacted_text = text
        mapping = {}
        
        # Find and redact emails with unique placeholders
        email_matches = self.email_pattern.finditer(text)
        email_counter = 1
        for match in email_matches:
            original_email = match.group()
            placeholder = f"[EMAIL_{email_counter}]"
            mapping[placeholder] = original_email
            redacted_text = redacted_text.replace(original_email, placeholder, 1)
            email_counter += 1
        
        # Find and redact phone numbers with unique placeholders
        phone_counter = 1
        for pattern in self.phone_patterns:
            phone_matches = pattern.finditer(redacted_text)
            for match in phone_matches:
                original_phone = match.group()
                placeholder = f"[PHONE_{phone_counter}]"
                mapping[placeholder] = original_phone
                redacted_text = redacted_text.replace(original_phone, placeholder, 1)
                phone_counter += 1
        
        return redacted_text, mapping
    
    def is_text_clean(self, text: str) -> bool:
        """
        Check if text contains any PII
        Returns True if no PII found, False otherwise
        """
        pii_items = self.find_pii_items(text)
        return len(pii_items["emails"]) == 0 and len(pii_items["phones"]) == 0
    
    def get_redaction_stats(self, original_text: str, redacted_text: str) -> Dict[str, int]:
        """
        Get statistics about redaction
        """
        original_pii = self.find_pii_items(original_text)
        redacted_pii = self.find_pii_items(redacted_text)
        
        return {
            "emails_redacted": len(original_pii["emails"]) - len(redacted_pii["emails"]),
            "phones_redacted": len(original_pii["phones"]) - len(redacted_pii["phones"]),
            "total_redacted": (len(original_pii["emails"]) + len(original_pii["phones"])) - 
                             (len(redacted_pii["emails"]) + len(redacted_pii["phones"])),
            "character_difference": len(original_text) - len(redacted_text)
        }