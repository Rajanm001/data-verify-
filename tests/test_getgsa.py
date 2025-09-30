"""
Test Suite for GetGSA System
Comprehensive tests covering all requirements
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import json

from src.models import Document, ChecklistItem
from src.document_processor import DocumentProcessor
from src.rag_system import RAGSystem
from src.pii_redactor import PIIRedactor
from src.ai_service import AIService
from src.storage import DocumentStorage

class TestDocumentProcessor:
    """Test document processing and classification"""
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    @pytest.mark.asyncio
    async def test_company_profile_extraction(self, processor):
        """Test extraction of company profile data"""
        doc = Document(
            name="Company Profile",
            text="""Company Profile (A):
Acme Robotics LLC
UEI: ABC123DEF456
DUNS: 123456789
NAICS: 541511, 541512
POC: Jane Smith, jane@acme.co, (415) 555-0100
Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
SAM.gov: registered""",
            type_hint="company_profile"
        )
        
        results = await processor.process_documents([doc])
        
        # Check extracted data
        profile = results["company_profile"]
        assert profile["uei"] == "ABC123DEF456"
        assert profile["duns"] == "123456789"
        assert profile["sam_status"] == "registered"
        assert 541511 in profile["naics"]
        assert 541512 in profile["naics"]
        assert profile["contact"]["email"] == "jane@acme.co"
        assert profile["contact"]["phone"] == "(415) 555-0100"
    
    @pytest.mark.asyncio
    async def test_past_performance_extraction(self, processor):
        """Test past performance data extraction"""
        doc = Document(
            name="Past Performance",
            text="""Past Performance (PP-2):
Customer: State of Fremont
Contract: Data migration & support
Value: $82,500
Period: 10/2022 - 02/2024
Contact: sarah.lee@fremont.gov""",
            type_hint="past_performance"
        )
        
        results = await processor.process_documents([doc])
        
        # Check extracted data
        pp = results["past_performance"][0]
        assert pp["customer"] == "State of Fremont"
        assert pp["value"] == 82500
        assert pp["contact_email"] == "sarah.lee@fremont.gov"
        assert pp["period"] == "10/2022 - 02/2024"
    
    @pytest.mark.asyncio
    async def test_pricing_extraction(self, processor):
        """Test pricing data extraction"""
        doc = Document(
            name="Pricing Sheet",
            text="""Pricing Sheet (text; simplified):
Labor Category, Rate, Unit
Senior Developer, 185, Hour
Project Manager, 165, Hour""",
            type_hint="pricing"
        )
        
        results = await processor.process_documents([doc])
        
        # Check extracted data
        pricing = results["pricing"]
        assert len(pricing) == 2
        assert pricing[0]["category"] == "Senior Developer"
        assert pricing[0]["rate"] == 185
        assert pricing[0]["unit"] == "Hour"

class TestRAGSystem:
    """Test RAG system and rule retrieval"""
    
    @pytest.fixture
    async def rag_system(self):
        rag = RAGSystem()
        await rag.initialize()
        return rag
    
    @pytest.mark.asyncio
    async def test_rule_retrieval(self, rag_system):
        """Test retrieval of relevant rules"""
        results = rag_system.retrieve_relevant_rules("UEI DUNS registration", top_k=2)
        
        assert len(results) >= 1
        rule_ids = [result[0] for result in results]
        assert "R1" in rule_ids  # Should retrieve identity & registry rule
    
    @pytest.mark.asyncio
    async def test_missing_uei_detection(self, rag_system):
        """Test 1: Missing UEI → missing_uei flagged (R1)"""
        analysis_results = {
            "company_profile": {
                "company_name": "Test Company",
                "duns": "123456789",
                "sam_status": "registered",
                "contact": {"email": "test@test.com", "phone": "(555) 555-5555"}
                # Missing UEI
            }
        }
        
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # Find R1 checklist item
        r1_item = next((item for item in checklist if item.rule_id == "R1"), None)
        assert r1_item is not None
        assert not r1_item.required_ok
        assert "missing_uei" in r1_item.problems
    
    @pytest.mark.asyncio
    async def test_past_performance_threshold(self, rag_system):
        """Test 2: Past performance threshold (PP-1 at $18,000) → past_performance_min_value_not_met (R3)"""
        analysis_results = {
            "past_performance": [
                {
                    "customer": "City of Palo Verde",
                    "value": 18000,  # Below $25,000 threshold
                    "period": "07/2023 - 03/2024",
                    "contact_email": "cio@pverde.gov"
                }
            ]
        }
        
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # Find R3 checklist item
        r3_item = next((item for item in checklist if item.rule_id == "R3"), None)
        assert r3_item is not None
        assert not r3_item.required_ok
        assert "past_performance_min_value_not_met" in r3_item.problems
    
    @pytest.mark.asyncio
    async def test_naics_sin_mapping(self, rag_system):
        """Test 3: Proper NAICS→SIN mapping with dedupe (R2)"""
        analysis_results = {
            "company_profile": {
                "naics": [541511, 541512]  # Both map to 54151S
            }
        }
        
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # Find R2 checklist item
        r2_item = next((item for item in checklist if item.rule_id == "R2"), None)
        assert r2_item is not None
        assert r2_item.required_ok  # These NAICS codes are valid
        assert len(r2_item.problems) == 0
    
    @pytest.mark.asyncio
    async def test_rag_sanity_removal(self, rag_system):
        """RAG sanity test: when R1 is removed from the index, checklist should fail to cite it"""
        # Remove R1 rule
        rag_system.remove_rule("R1")
        
        analysis_results = {
            "company_profile": {
                "company_name": "Test Company"
                # Missing UEI, DUNS, etc.
            }
        }
        
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # R1 should not be in checklist since rule was removed  
        r1_item = next((item for item in checklist if item.rule_id == "R1"), None)
        assert r1_item is None

class TestPIIRedactor:
    """Test PII redaction functionality"""
    
    @pytest.fixture
    def redactor(self):
        return PIIRedactor()
    
    def test_pii_redaction_masks_emails_and_phones(self, redactor):
        """Test 4: PII redaction masks emails/phones in stored docs (R5)"""
        original_text = """Contact: Jane Smith, jane@acme.co, (415) 555-0100
Secondary: Bob Wilson bob.wilson@beta.com 312-555-0200"""
        
        redacted_text = redactor.redact_text(original_text)
        
        # Check that emails and phones are redacted
        assert "jane@acme.co" not in redacted_text
        assert "bob.wilson@beta.com" not in redacted_text
        assert "(415) 555-0100" not in redacted_text
        assert "312-555-0200" not in redacted_text
        
        # Check that redaction placeholders are present
        assert "[EMAIL_REDACTED]" in redacted_text
        assert "[PHONE_REDACTED]" in redacted_text
    
    def test_pii_detection(self, redactor):
        """Test PII detection without redaction"""
        text = "Contact jane@test.com or call (555) 123-4567"
        
        pii_items = redactor.find_pii_items(text)
        
        assert "jane@test.com" in pii_items["emails"]
        assert "(555) 123-4567" in pii_items["phones"]
    
    def test_no_pii_text_unchanged(self, redactor):
        """Test that text without PII remains unchanged"""
        text = "This is a clean document with no personal information."
        
        redacted_text = redactor.redact_text(text)
        
        assert text == redacted_text
        assert redactor.is_text_clean(text)

class TestAIService:
    """Test AI service functionality"""
    
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @pytest.mark.asyncio
    async def test_brief_generation_with_template(self, ai_service):
        """Test brief generation using template fallback"""
        analysis_results = {
            "company_profile": {"company_name": "Test Company"}
        }
        checklist = [
            ChecklistItem(
                rule_id="R1",
                description="Identity & Registry requirements",
                required_ok=False,
                problems=["missing_uei", "missing_duns"],
                evidence=["UEI not found", "DUNS not found"]
            )
        ]
        
        # Force template mode
        ai_service.use_openai = False
        
        brief = await ai_service.generate_negotiation_brief(analysis_results, checklist)
        
        assert "Test Company" in brief
        assert "missing_uei" in brief.lower() or "uei" in brief.lower()
        assert len(brief) > 100  # Should be substantial
    
    @pytest.mark.asyncio
    async def test_email_generation_with_template(self, ai_service):
        """Test client email generation using template fallback"""
        analysis_results = {
            "company_profile": {"company_name": "Test Company"}
        }
        checklist = [
            ChecklistItem(
                rule_id="R1",
                description="Identity & Registry requirements",
                required_ok=False,
                problems=["missing_uei"],
                evidence=["UEI not found"]
            )
        ]
        
        # Force template mode
        ai_service.use_openai = False
        
        email = await ai_service.generate_client_email(analysis_results, checklist)
        
        assert "Test Company" in email
        assert "missing" in email.lower()
        assert "Subject:" in email
        assert "GSA" in email

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete document processing pipeline"""
        # Initialize components
        processor = DocumentProcessor()
        rag_system = RAGSystem()
        await rag_system.initialize()
        ai_service = AIService()
        ai_service.use_openai = False  # Use template mode
        redactor = PIIRedactor()
        
        # Sample document
        doc = Document(
            name="Test Company Profile",
            text="""Test Company LLC
UEI: TEST12345678
DUNS: 987654321
NAICS: 541511
POC: Test User, test@example.com, (555) 555-5555
SAM.gov: registered""",
            type_hint="company_profile"
        )
        
        # Test PII redaction
        redacted_text = redactor.redact_text(doc.text)
        assert "test@example.com" not in redacted_text
        assert "(555) 555-5555" not in redacted_text
        
        # Process document
        analysis_results = await processor.process_documents([doc])
        
        # Generate checklist
        checklist = await rag_system.generate_checklist(analysis_results)
        
        # Generate brief and email
        brief = await ai_service.generate_negotiation_brief(analysis_results, checklist)
        email = await ai_service.generate_client_email(analysis_results, checklist)
        
        # Verify results
        assert analysis_results["company_profile"]["uei"] == "TEST12345678"
        assert len(checklist) > 0
        assert len(brief) > 50
        assert len(email) > 50
        assert "Subject:" in email

class TestStorage:
    """Test document storage functionality"""
    
    @pytest.fixture
    def storage(self):
        return DocumentStorage(storage_dir="test_storage")
    
    @pytest.mark.asyncio
    async def test_document_storage(self, storage):
        """Test document storage and retrieval"""
        original_text = "Test document with email@test.com"
        redacted_text = "Test document with [EMAIL_REDACTED]"
        
        doc_id = await storage.store_document(
            name="Test Doc",
            original_text=original_text,
            redacted_text=redacted_text,
            request_id="test-123"
        )
        
        # Retrieve document (redacted only)
        doc = await storage.get_document(doc_id, redacted_only=True)
        
        assert doc is not None
        assert doc["name"] == "Test Doc"
        assert doc["request_id"] == "test-123"
        assert "original_text" not in doc  # Should be redacted
        
        # Get storage stats
        stats = storage.get_storage_stats()
        assert stats["total_documents"] >= 1

# Test runner function
async def run_all_tests():
    """Run all tests manually"""
    print("🧪 Running GetGSA Test Suite...")
    
    # Test 1: Missing UEI detection
    print("\n📋 Test 1: Missing UEI detection")
    rag = RAGSystem()
    await rag.initialize()
    
    analysis_results = {"company_profile": {"duns": "123456789"}}  # Missing UEI
    checklist = await rag.generate_checklist(analysis_results)
    r1_item = next((item for item in checklist if item.rule_id == "R1"), None)
    
    if r1_item and "missing_uei" in r1_item.problems:
        print("✅ PASS: Missing UEI correctly flagged")
    else:
        print("❌ FAIL: Missing UEI not detected")
    
    # Test 2: Past performance threshold
    print("\n📋 Test 2: Past performance threshold")
    analysis_results = {
        "past_performance": [{"customer": "Test", "value": 18000, "contact_email": "test@test.com"}]
    }
    checklist = await rag.generate_checklist(analysis_results)
    r3_item = next((item for item in checklist if item.rule_id == "R3"), None)
    
    if r3_item and "past_performance_min_value_not_met" in r3_item.problems:
        print("✅ PASS: Past performance threshold correctly flagged")
    else:
        print("❌ FAIL: Past performance threshold not detected")
    
    # Test 3: NAICS mapping
    print("\n📋 Test 3: NAICS SIN mapping")
    analysis_results = {"company_profile": {"naics": [541511, 541512]}}
    checklist = await rag.generate_checklist(analysis_results)
    r2_item = next((item for item in checklist if item.rule_id == "R2"), None)
    
    if r2_item and r2_item.required_ok:
        print("✅ PASS: Valid NAICS codes correctly approved")
    else:
        print("❌ FAIL: Valid NAICS codes incorrectly flagged")
    
    # Test 4: PII redaction
    print("\n📋 Test 4: PII redaction")
    redactor = PIIRedactor()
    original = "Contact jane@test.com or (555) 123-4567"
    redacted = redactor.redact_text(original)
    
    if "jane@test.com" not in redacted and "(555) 123-4567" not in redacted:
        print("✅ PASS: PII correctly redacted")
    else:
        print("❌ FAIL: PII not properly redacted")
    
    # Test 5: RAG sanity test
    print("\n📋 Test 5: RAG sanity test (rule removal)")
    rag_test = RAGSystem()
    await rag_test.initialize()
    rag_test.remove_rule("R1")
    
    analysis_results = {"company_profile": {"company_name": "Test"}}
    checklist = await rag_test.generate_checklist(analysis_results)
    r1_item = next((item for item in checklist if item.rule_id == "R1"), None)
    
    if r1_item is None:
        print("✅ PASS: Removed rule not cited in checklist")
    else:
        print("❌ FAIL: Removed rule still appearing in checklist")
    
    print("\n🎉 Test suite complete!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())