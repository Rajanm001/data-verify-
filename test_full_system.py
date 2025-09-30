#!/usr/bin/env python3
"""
Full End-to-End GSA Compliance System Test
Tests the complete pipeline without requiring server
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.document_processor import DocumentProcessor
from src.rag_system import RAGSystem
from src.ai_service import EnterpriseAIService
from src.models import Document
from main import convert_to_json_serializable

async def test_full_gsa_system():
    """Test the complete GSA compliance analysis system"""
    
    print("🎯 Full End-to-End GSA Compliance Test")
    print("=" * 50)
    
    # Test document with comprehensive GSA data
    test_doc = Document(
        name="comprehensive_gsa.txt",
        text="""
        COMPREHENSIVE GSA SCHEDULE PROPOSAL
        
        Company Information:
        Company Name: ABC Technology Solutions
        UEI (Unique Entity Identifier): ABC123456789
        DUNS Number: 123456789
        SAM.gov Registration Status: Active
        Primary Contact: John Smith, CEO
        Email: john.smith@abctech.com
        Phone: (555) 123-4567
        
        NAICS Classification:
        Primary NAICS Code: 541511 (Computer Systems Design Services)
        Secondary NAICS: 541512 (Computer Systems Design - Custom)
        
        Past Performance History:
        1. Contract: W52P1J-21-D-0001
           Customer: U.S. Army Corps of Engineers
           Value: $2,500,000
           Period: March 2021 - March 2024
           Performance Rating: Exceptional
           
        2. Contract: HHSN316201200036W
           Customer: Department of Health and Human Services
           Value: $1,800,000
           Period: January 2020 - December 2023
           Performance Rating: Satisfactory
           
        3. Contract: GS-35F-0119Y
           Customer: General Services Administration
           Value: $500,000
           Period: June 2022 - June 2024
           Performance Rating: Outstanding
        
        Labor Categories and Pricing Structure:
        - Senior Systems Architect: $150/hour
        - Senior Software Developer: $125/hour
        - Project Manager: $110/hour
        - Systems Analyst: $95/hour
        - Junior Developer: $75/hour
        - Technical Writer: $65/hour
        
        Rate Basis: Hourly
        Pricing Period: 2024-2025
        All rates include fully loaded costs with overhead and profit.
        """,
        type_hint="gsa_proposal"
    )
    
    try:
        # Initialize all components
        print("Initializing system components...")
        processor = DocumentProcessor()
        rag_system = RAGSystem()
        ai_service = EnterpriseAIService()
        print("✓ All components initialized successfully")
        
        # Step 1: Document processing
        print("\nStep 1: Processing document and extracting data...")
        extraction_results = await processor.process_documents([test_doc])
        
        company_profile = extraction_results.get("company_profile", {})
        past_performance = extraction_results.get("past_performance", [])
        pricing = extraction_results.get("pricing", [])
        
        print(f"  ✓ Company profile fields: {len(company_profile)}")
        print(f"  ✓ Past performance contracts: {len(past_performance)}")
        print(f"  ✓ Pricing items: {len(pricing)}")
        
        # Display key extracted data
        print(f"    - UEI: {company_profile.get('uei', 'NOT FOUND')}")
        print(f"    - DUNS: {company_profile.get('duns', 'NOT FOUND')}")
        print(f"    - SAM Status: {company_profile.get('sam_status', 'NOT FOUND')}")
        print(f"    - NAICS: {company_profile.get('naics', 'NOT FOUND')}")
        
        # Step 2: GSA compliance analysis
        print("\nStep 2: Generating GSA compliance checklist...")
        checklist_items = await rag_system.generate_checklist(extraction_results)
        print(f"  ✓ GSA rules evaluated: {len(checklist_items)}")
        
        # Step 3: AI analysis generation  
        print("\nStep 3: Generating AI-powered analysis...")
        # Convert to serializable format first
        serializable_results = convert_to_json_serializable(extraction_results)
        # Cast to proper type for AI service
        analysis_dict = dict(serializable_results) if isinstance(serializable_results, dict) else {}
        ai_content, ai_metadata = await ai_service.generate_negotiation_brief(analysis_dict, checklist_items)
        print(f"  ✓ AI analysis generated: {len(ai_content)} characters")
        print(f"  ✓ Provider used: {ai_metadata.get('provider', 'unknown')}")
        
        # Step 4: Results evaluation
        print("\nStep 4: Evaluating compliance results...")
        passed_rules = sum(1 for item in checklist_items if item.required_ok)
        total_rules = len(checklist_items)
        compliance_rate = (passed_rules / total_rules * 100) if total_rules > 0 else 0
        
        print(f"  ✓ Rules passed: {passed_rules}/{total_rules}")
        print(f"  ✓ Compliance rate: {compliance_rate:.1f}%")
        
        # Display detailed results
        print("\n" + "=" * 50)
        print("📊 DETAILED COMPLIANCE RESULTS")
        print("=" * 50)
        
        for item in checklist_items:
            status = "✅ PASS" if item.required_ok else "❌ FAIL"
            print(f"{status} {item.rule_id}: {item.description}")
            
            if item.evidence and len(item.evidence) > 0:
                print(f"    Evidence: {item.evidence[0]}")
            
            if item.problems and len(item.problems) > 0:
                print(f"    Issues: {', '.join(item.problems)}")
        
        # Final assessment
        print("\n" + "=" * 50)
        success_threshold = 90.0
        is_success = compliance_rate >= success_threshold
        
        if is_success:
            print("🏆 FINAL RESULT: ✅ SUCCESS")
            print(f"📈 Compliance Rate: {compliance_rate:.1f}% (≥{success_threshold}%)")
            print("✅ Document meets GSA Schedule requirements!")
        else:
            print("🏆 FINAL RESULT: ❌ NEEDS IMPROVEMENT")  
            print(f"📈 Compliance Rate: {compliance_rate:.1f}% (<{success_threshold}%)")
            print("⚠️ Document requires additional work to meet GSA requirements")
        
        print("\n🎯 SYSTEM STATUS: All components working correctly!")
        return is_success
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting comprehensive GetGSA system test...")
    success = asyncio.run(test_full_gsa_system())
    print(f"\n🏁 Test Conclusion: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)