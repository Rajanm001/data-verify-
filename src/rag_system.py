"""
RAG System for GSA Rules Pack
Implements vector storage and retrieval for policy snippets R1-R5
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

from src.models import ChecklistItem, Citation

class RAGSystem:
    def __init__(self):
        self.model = None
        self.rules_db = {}
        self.rule_embeddings = {}
        self.recent_citations = []
        
        # GSA Rules Pack (R1-R5)
        self.gsa_rules = {
            "R1": {
                "title": "Identity & Registry",
                "content": """Required: UEI (12 chars), DUNS (9 digits), and active SAM.gov registration.
Primary contact must have valid email and phone."""
            },
            "R2": {
                "title": "NAICS & SIN Mapping",
                "content": """NAICS to SIN mapping (subset for test):
541511 → 54151S
541512 → 54151S  
541611 → 541611
518210 → 518210C"""
            },
            "R3": {
                "title": "Past Performance",
                "content": """At least 1 past performance ≥ $25,000 within last 36 months.
Must include customer name, value, period, and contact email."""
            },
            "R4": {
                "title": "Pricing & Catalog",
                "content": """Provide labor categories and rates in a structured sheet.
If missing rate basis or units, flag "pricing_incomplete"."""
            },
            "R5": {
                "title": "Submission Hygiene",
                "content": """All personally identifiable info must be stored in redacted form; 
only derived fields and hashes are stored by default."""
            }
        }
    
    async def initialize(self):
        """Initialize the sentence transformer model and create embeddings"""
        try:
            # Use a lightweight model for demo
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create embeddings for each rule
            for rule_id, rule_data in self.gsa_rules.items():
                text = f"{rule_data['title']}: {rule_data['content']}"
                embedding = self.model.encode([text])[0]
                
                self.rules_db[rule_id] = {
                    "title": rule_data["title"],
                    "content": rule_data["content"],
                    "full_text": text,
                    "embedding": embedding
                }
                
        except Exception as e:
            print(f"Warning: Could not initialize sentence transformer: {e}")
            # Fallback to keyword-based retrieval
            self.model = None
            for rule_id, rule_data in self.gsa_rules.items():
                self.rules_db[rule_id] = {
                    "title": rule_data["title"],
                    "content": rule_data["content"],
                    "full_text": f"{rule_data['title']}: {rule_data['content']}"
                }
    
    def retrieve_relevant_rules(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """
        Retrieve relevant rules for a given query
        Returns: List of (rule_id, content, relevance_score)
        """
        if not self.model:
            # Fallback to keyword matching
            return self._keyword_based_retrieval(query, top_k)
        
        try:
            query_embedding = self.model.encode([query])[0]
            similarities = []
            
            for rule_id, rule_data in self.rules_db.items():
                similarity = cosine_similarity(
                    [query_embedding], 
                    [rule_data["embedding"]]
                )[0][0]
                similarities.append((rule_id, rule_data["full_text"], float(similarity)))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[2], reverse=True)
            return similarities[:top_k]
            
        except Exception:
            return self._keyword_based_retrieval(query, top_k)
    
    def _keyword_based_retrieval(self, query: str, top_k: int) -> List[Tuple[str, str, float]]:
        """Fallback keyword-based retrieval"""
        query_lower = query.lower()
        results = []
        
        keyword_rules = {
            "uei": "R1", "duns": "R1", "sam": "R1", "contact": "R1", "email": "R1", "phone": "R1",
            "naics": "R2", "sin": "R2", "mapping": "R2",
            "performance": "R3", "past": "R3", "customer": "R3", "value": "R3", "25000": "R3",
            "pricing": "R4", "labor": "R4", "rate": "R4", "catalog": "R4",
            "pii": "R5", "redact": "R5", "personal": "R5", "identifiable": "R5"
        }
        
        rule_scores = {}
        for keyword, rule_id in keyword_rules.items():
            if keyword in query_lower:
                rule_scores[rule_id] = rule_scores.get(rule_id, 0) + 1
        
        # Convert to results format
        for rule_id, score in sorted(rule_scores.items(), key=lambda x: x[1], reverse=True):
            if rule_id in self.rules_db:
                results.append((rule_id, self.rules_db[rule_id]["full_text"], score / 10.0))
        
        # Add remaining rules with low score if needed
        remaining_rules = set(self.rules_db.keys()) - set(rule_scores.keys())
        for rule_id in list(remaining_rules)[:top_k - len(results)]:
            results.append((rule_id, self.rules_db[rule_id]["full_text"], 0.1))
        
        return results[:top_k]
    
    async def generate_checklist(self, analysis_results: Dict[str, Any]) -> List[ChecklistItem]:
        """
        Generate policy-aware checklist using RAG retrieval
        """
        checklist_items = []
        self.recent_citations = []
        
        # R1: Identity & Registry checks (only if rule exists)
        if "R1" in self.rules_db:
            r1_rules = self.retrieve_relevant_rules("UEI DUNS SAM registration contact email phone", 1)
            if r1_rules and r1_rules[0][0] == "R1":
                rule_id, content, score = r1_rules[0]
                self.recent_citations.append(Citation(rule_id=rule_id, chunk=content, relevance_score=score))
                
                problems = []
                evidence = []
            
            # Check UEI
            uei = analysis_results.get("company_profile", {}).get("uei")
            if not uei or len(uei) != 12:
                problems.append("missing_uei")
                evidence.append("UEI not found or invalid format (requires 12 characters)")
            
            # Check DUNS
            duns = analysis_results.get("company_profile", {}).get("duns")
            if not duns or not re.match(r'^\d{9}$', str(duns)):
                problems.append("missing_duns")
                evidence.append("DUNS not found or invalid format (requires 9 digits)")
            
            # Check SAM registration
            sam_status = analysis_results.get("company_profile", {}).get("sam_status")
            if sam_status != "registered":
                problems.append("sam_not_active")
                evidence.append(f"SAM.gov status: {sam_status or 'unknown'}")
            
            # Check contact info
            contact = analysis_results.get("company_profile", {}).get("contact", {})
            if not contact.get("email"):
                problems.append("missing_contact_email")
                evidence.append("Primary contact email not found")
            if not contact.get("phone"):
                problems.append("missing_contact_phone")
                evidence.append("Primary contact phone not found")
            
            checklist_items.append(ChecklistItem(
                rule_id="R1",
                description="Identity & Registry requirements",
                required_ok=len(problems) == 0,
                problems=problems,
                evidence=evidence
            ))
        
        # R2: NAICS & SIN Mapping (only if rule exists)
        if "R2" in self.rules_db:
            r2_rules = self.retrieve_relevant_rules("NAICS SIN mapping", 1)
            if r2_rules and r2_rules[0][0] == "R2":
                rule_id, content, score = r2_rules[0]
                self.recent_citations.append(Citation(rule_id=rule_id, chunk=content, relevance_score=score))
                
                problems = []
                evidence = []
            
            naics_codes = analysis_results.get("company_profile", {}).get("naics", [])
            if not naics_codes:
                problems.append("missing_naics")
                evidence.append("No NAICS codes found")
            else:
                # Check mapping based on R2 rules
                valid_mappings = {"541511": "54151S", "541512": "54151S", "541611": "541611", "518210": "518210C"}
                for naics in naics_codes:
                    if str(naics) not in valid_mappings:
                        problems.append("invalid_naics_mapping")
                        evidence.append(f"NAICS {naics} not in approved SIN mapping")
            
            checklist_items.append(ChecklistItem(
                rule_id="R2",
                description="NAICS & SIN Mapping verification",
                required_ok=len(problems) == 0,
                problems=problems,
                evidence=evidence
            ))
        
        # R3: Past Performance (only if rule exists)
        if "R3" in self.rules_db:
            r3_rules = self.retrieve_relevant_rules("past performance $25000 36 months customer", 1)
            if r3_rules and r3_rules[0][0] == "R3":
                rule_id, content, score = r3_rules[0]
                self.recent_citations.append(Citation(rule_id=rule_id, chunk=content, relevance_score=score))
                
                problems = []
                evidence = []
            
            past_performances = analysis_results.get("past_performance", [])
            valid_performances = []
            
            for pp in past_performances:
                value = pp.get("value", 0)
                if isinstance(value, str):
                    # Extract numeric value
                    value = float(re.sub(r'[^\d.]', '', value) or 0)
                
                if value >= 25000:
                    valid_performances.append(pp)
                    evidence.append(f"Valid performance: {pp.get('customer', 'Unknown')} - ${value:,}")
            
            if not valid_performances:
                problems.append("past_performance_min_value_not_met")
                evidence.append("No past performance contracts ≥ $25,000 found")
            
            # Check required fields in valid performances
            for pp in valid_performances:
                if not pp.get("customer"):
                    problems.append("missing_pp_customer")
                if not pp.get("contact_email"):
                    problems.append("missing_pp_contact")
                if not pp.get("period"):
                    problems.append("missing_pp_period")
            
            checklist_items.append(ChecklistItem(
                rule_id="R3",
                description="Past Performance requirements",
                required_ok=len(problems) == 0,
                problems=problems,
                evidence=evidence
            ))
        
        # R4: Pricing & Catalog (only if rule exists)
        if "R4" in self.rules_db:
            r4_rules = self.retrieve_relevant_rules("pricing labor categories rates structured", 1)
            if r4_rules and r4_rules[0][0] == "R4":
                rule_id, content, score = r4_rules[0]
                self.recent_citations.append(Citation(rule_id=rule_id, chunk=content, relevance_score=score))
                
                problems = []
                evidence = []
            
            pricing_data = analysis_results.get("pricing", [])
            if not pricing_data:
                problems.append("pricing_incomplete")
                evidence.append("No pricing information found")
            else:
                for item in pricing_data:
                    if not item.get("rate") or not item.get("unit"):
                        problems.append("pricing_incomplete")
                        evidence.append(f"Missing rate basis or units for {item.get('category', 'Unknown category')}")
            
            checklist_items.append(ChecklistItem(
                rule_id="R4",
                description="Pricing & Catalog requirements",
                required_ok=len(problems) == 0,
                problems=problems,
                evidence=evidence
            ))
        
        return checklist_items
    
    def get_recent_citations(self) -> List[Citation]:
        """Get citations from the most recent checklist generation"""
        return self.recent_citations
    
    def remove_rule(self, rule_id: str):
        """Remove a rule from the database (for testing)"""
        if rule_id in self.rules_db:
            del self.rules_db[rule_id]