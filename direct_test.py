#!/usr/bin/env python3
"""
Direct Test - GetGSA 100% Accuracy
Test the running server directly
"""

import requests
import json

def test_direct():
    base_url = "http://127.0.0.1:8001"
    
    print("🎯 Testing GetGSA Server Directly")
    print("=" * 40)
    
    # Perfect compliant document
    perfect_doc = {
        "name": "Perfect_Contract.txt",
        "text": """
        PERFECT GSA COMPLIANT CONTRACT
        
        UEI: ABC123456789
        DUNS Number: 123456789
        SAM Registration Status: Active
        Primary Contact Email: contracts@company.com
        Primary Contact Phone: (202) 555-0199
        Primary NAICS Code: 541511
        
        Past Performance:
        Contract 1:
        Customer: Department of Veterans Affairs
        Value: $125,000
        Contact: sarah@va.gov
        
        Labor Categories and Rates:
        - Senior Software Developer: $125/hour
        - Project Manager: $110/hour
        - Systems Architect: $150/hour
        """,
        "type_hint": "contract"
    }
    
    try:
        # 1. Health check
        print("1. Health Check...")
        health = requests.get(f"{base_url}/health")
        print(f"   Status: {health.status_code}")
        
        # 2. Ingest
        print("2. Ingesting document...")
        ingest = requests.post(f"{base_url}/ingest", json={"documents": [perfect_doc]})
        print(f"   Status: {ingest.status_code}")
        
        # 3. Analyze
        print("3. Analyzing...")
        analyze = requests.post(f"{base_url}/analyze", json={
            "analysis_type": "comprehensive",
            "include_checklist": True
        })
        
        print(f"   Status: {analyze.status_code}")
        
        if analyze.status_code == 200:
            result = analyze.json()
            checklist = result.get('checklist', [])
            
            print(f"\n📊 RESULTS:")
            compliant = sum(1 for item in checklist if item.get('required_ok', False))
            total = len(checklist)
            
            print(f"   Success Rate: {compliant}/{total} ({compliant/total*100:.1f}%)")
            
            for i, item in enumerate(checklist, 1):
                status = "✅" if item.get('required_ok', False) else "❌"
                rule = item.get('rule_id', f'R{i}')
                desc = item.get('description', 'Unknown')
                print(f"   {i}. {status} {rule}: {desc}")
                
                # Show evidence for passed items
                if item.get('required_ok', False):
                    evidence = item.get('evidence', [])
                    for ev in evidence[:2]:
                        print(f"      ✅ {ev}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_direct()