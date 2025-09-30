#!/usr/bin/env python3
"""
Debug GetGSA Data Flow - Show what's being extracted
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.document_processor import DocumentProcessor
from src.models import Document

async def debug_extraction():
    """Debug what data is being extracted from documents"""
    
    print("🔧 GetGSA Data Extraction Debug")
    print("=" * 50)
    
    processor = DocumentProcessor()
    
    # Test document with perfect GSA compliance data
    test_doc = Document(
        name="Perfect_Test.txt",
        text="""
        PERFECT GSA COMPLIANT CONTRACT
        
        Contractor Information:
        UEI (Unique Entity Identifier): ABC123456789
        DUNS Number: 123456789
        SAM Registration Status: Active
        Primary Contact Email: contracts@company.com
        Primary Contact Phone: (202) 555-0199
        
        NAICS Information:
        Primary NAICS Code: 541511
        Secondary NAICS: 541512
        
        Past Performance:
        Contract 1:
        Customer: Department of Veterans Affairs
        Value: $125,000
        Period: 2023-2024
        Contact: sarah@va.gov
        
        Pricing Information:
        Labor Categories and Rates:
        - Senior Software Developer: $125/hour
        - Project Manager: $110/hour
        - Systems Architect: $150/hour
        Rate Basis: Hourly
        Units: Per Hour
        """,
        type_hint="contract"
    )
    
    print("📄 Processing test document...")
    results = await processor.process_documents([test_doc])
    
    print("\n🔍 EXTRACTION RESULTS:")
    print("=" * 30)
    
    print("\n📋 Company Profile:")
    company_profile = results.get("company_profile", {})
    print(f"   UEI: {company_profile.get('uei', 'NOT FOUND')}")
    print(f"   DUNS: {company_profile.get('duns', 'NOT FOUND')}")
    print(f"   SAM Status: {company_profile.get('sam_status', 'NOT FOUND')}")
    print(f"   NAICS: {company_profile.get('naics', 'NOT FOUND')}")
    
    contact = company_profile.get("contact", {})
    print(f"   Contact Email: {contact.get('email', 'NOT FOUND')}")
    print(f"   Contact Phone: {contact.get('phone', 'NOT FOUND')}")
    
    print("\n📈 Past Performance:")
    past_performance = results.get("past_performance", [])
    print(f"   Total Contracts: {len(past_performance)}")
    for i, pp in enumerate(past_performance, 1):
        print(f"   Contract {i}:")
        print(f"     Value: ${pp.get('value', 0):,}")
        print(f"     Customer: {pp.get('customer', 'Unknown')}")
    
    print("\n💰 Pricing:")
    pricing = results.get("pricing", [])
    print(f"   Pricing Items: {len(pricing)}")
    for i, item in enumerate(pricing, 1):
        print(f"   Item {i}:")
        print(f"     Category: {item.get('category', 'Unknown')}")
        print(f"     Rate: ${item.get('rate', 0)}")
        print(f"     Unit: {item.get('unit', 'Unknown')}")
    
    print("\n🎯 SUMMARY:")
    print(f"   Company Profile Keys: {list(company_profile.keys())}")
    print(f"   Past Performance Count: {len(past_performance)}")  
    print(f"   Pricing Items Count: {len(pricing)}")
    
    # Check what should pass GSA rules
    print("\n✅ GSA COMPLIANCE CHECK:")
    
    # R1 Check
    has_uei = company_profile.get('uei') and len(str(company_profile['uei'])) == 12
    has_duns = company_profile.get('duns') and len(str(company_profile['duns'])) == 9
    has_sam = company_profile.get('sam_status') in ['active', 'registered']
    has_email = contact.get('email')
    has_phone = contact.get('phone')
    
    r1_pass = has_uei and has_duns and has_sam and has_email and has_phone
    print(f"   R1 (Identity): {'✅ PASS' if r1_pass else '❌ FAIL'}")
    print(f"     UEI: {'✅' if has_uei else '❌'} {company_profile.get('uei', 'Missing')}")
    print(f"     DUNS: {'✅' if has_duns else '❌'} {company_profile.get('duns', 'Missing')}")
    print(f"     SAM: {'✅' if has_sam else '❌'} {company_profile.get('sam_status', 'Missing')}")
    print(f"     Email: {'✅' if has_email else '❌'} {contact.get('email', 'Missing')}")
    print(f"     Phone: {'✅' if has_phone else '❌'} {contact.get('phone', 'Missing')}")
    
    # R2 Check
    naics_codes = company_profile.get('naics', [])
    has_naics = bool(naics_codes)
    print(f"   R2 (NAICS): {'✅ PASS' if has_naics else '❌ FAIL'}")
    print(f"     NAICS Codes: {naics_codes}")
    
    # R3 Check
    valid_pp = [pp for pp in past_performance if pp.get('value', 0) >= 25000]
    has_pp = len(valid_pp) > 0
    print(f"   R3 (Past Performance): {'✅ PASS' if has_pp else '❌ FAIL'}")
    print(f"     Valid Contracts: {len(valid_pp)}")
    
    # R4 Check
    valid_pricing = [p for p in pricing if p.get('rate') and p.get('unit')]
    has_pricing = len(valid_pricing) > 0
    print(f"   R4 (Pricing): {'✅ PASS' if has_pricing else '❌ FAIL'}")
    print(f"     Valid Pricing Items: {len(valid_pricing)}")
    
    overall_pass = r1_pass and has_naics and has_pp and has_pricing
    print(f"\n🏆 OVERALL: {'✅ 100% COMPLIANT' if overall_pass else '❌ NON-COMPLIANT'}")
    
    return results

if __name__ == "__main__":
    asyncio.run(debug_extraction())