#!/usr/bin/env python3
"""
API Test and Fix - Check OpenAI and GROQ APIs
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_and_analysis():
    """Test APIs and complete analysis workflow"""
    
    print("🔧 GetGSA API Test and Fix")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test document
    test_contract = {
        "name": "Test_Contract.txt",
        "text": """
        GOVERNMENT SOFTWARE CONTRACT
        
        Contractor: TechSolutions Inc
        UEI: TEST123456789
        DUNS: 123456789
        SAM Registration: Active
        NAICS: 541511
        
        Project: Data Management System
        Value: $100,000
        Duration: 4 months
        
        Contact: manager@techsolutions.com
        Phone: (555) 123-4567
        
        Requirements:
        - Cloud infrastructure
        - Security compliance
        - Data analytics
        - User training
        
        This contract follows GSA requirements.
        """,
        "type_hint": "contract"
    }
    
    try:
        # Step 1: Test server health
        print("\n1. 🏥 Testing server health...")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Server healthy")
        else:
            print(f"   ❌ Server health failed: {response.status_code}")
            return False
        
        # Step 2: Test document ingestion
        print("\n2. 📤 Testing document ingestion...")
        
        ingest_data = {"documents": [test_contract]}
        response = requests.post(f"{base_url}/ingest", json=ingest_data, timeout=30)
        
        if response.status_code == 200:
            print("   ✅ Document ingested successfully")
            result = response.json()
            print(f"   📄 Result: {result.get('message', 'Processed')}")
        else:
            print(f"   ❌ Ingestion failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            return False
        
        # Step 3: Test AI analysis
        print("\n3. 🤖 Testing AI analysis...")
        print("   ⏳ Running analysis (may take 60+ seconds)...")
        
        analysis_data = {
            "analysis_type": "comprehensive",
            "include_checklist": True,
            "generate_brief": True,
            "generate_email": True
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=analysis_data, timeout=120)
        analysis_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Analysis completed in {analysis_time:.1f}s")
            
            result = response.json()
            
            print("\n" + "="*50)
            print("🎯 COMPLETE ANALYSIS RESULTS")
            print("="*50)
            
            # Show basic info
            print(f"📊 Documents: {result.get('documents_analyzed', 0)}")
            print(f"📋 Status: {result.get('compliance_status', 'Unknown')}")
            
            # Show checklist
            checklist = result.get('checklist', [])
            print(f"\n✅ COMPLIANCE CHECKLIST ({len(checklist)} items):")
            for i, item in enumerate(checklist[:3], 1):  # Show first 3
                status = "✅" if item.get('required_ok', False) else "❌"
                rule_id = item.get('rule_id', f'R{i}')
                desc = item.get('description', 'No description')[:50]
                print(f"   {i}. {status} {rule_id}: {desc}...")
            
            # Show AI content
            brief = result.get('brief', '')
            if brief:
                print(f"\n📋 AI BRIEF (first 200 chars):")
                print(f"   {brief[:200]}...")
            
            email = result.get('client_email', '')
            if email:
                print(f"\n📧 AI EMAIL (first 200 chars):")
                print(f"   {email[:200]}...")
            
            # Show performance
            metadata = result.get('enterprise_metadata', {})
            if metadata:
                providers = metadata.get('ai_providers_used', [])
                processing_time = metadata.get('processing_time', 0)
                print(f"\n⚡ PERFORMANCE:")
                print(f"   🤖 AI Providers: {', '.join(providers)}")
                print(f"   🕒 Processing: {processing_time:.2f}s")
            
            print("\n🎉 SUCCESS: COMPLETE AI ANALYSIS WORKING!")
            return True
            
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            
            if "openai" in response.text.lower():
                print("\n🔄 OpenAI API issue detected - system should auto-fallback to GROQ")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - server not responding")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout - analysis taking too long")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

def check_api_keys():
    """Check API key configuration"""
    print("\n🔑 Checking API Keys...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    if openai_key:
        print(f"   ✅ OpenAI API Key: ...{openai_key[-4:] if len(openai_key) > 4 else 'SET'}")
    else:
        print("   ❌ OpenAI API Key: NOT SET")
    
    if groq_key:
        print(f"   ✅ GROQ API Key: ...{groq_key[-4:] if len(groq_key) > 4 else 'SET'}")
    else:
        print("   ❌ GROQ API Key: NOT SET")

def main():
    """Main test function"""
    
    print("🎯 GetGSA API Test and Analysis")
    print("This will test if the APIs are working and analysis is complete")
    
    # Check API keys
    check_api_keys()
    
    # Test complete workflow
    success = test_api_and_analysis()
    
    if success:
        print("\n🏆 FINAL RESULT: ALL APIS WORKING!")
        print("🎯 Complete AI analysis is functional")
        print("🌐 System ready at: http://127.0.0.1:8001")
    else:
        print("\n⚠️ API issues detected - check configuration")
        print("💡 The system has GROQ fallback if OpenAI fails")

if __name__ == "__main__":
    main()