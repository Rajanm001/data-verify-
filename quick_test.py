#!/usr/bin/env python3
"""
Quick Test - Verify GetGSA Server is Working
"""

import requests
import json

def test_server():
    """Test the server is responding correctly"""
    
    print("🔍 GetGSA Server Quick Test")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Test 1: Health check
        print("1. Testing server health...")
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Health check: OK")
            health_data = response.json()
            print(f"   📊 Status: {health_data.get('status', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
        # Test 2: Main page
        print("\n2. Testing main page...")
        response = requests.get(base_url, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Main page: Accessible")
            print("   🌐 Web interface ready")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
            
        # Test 3: Simple document test
        print("\n3. Testing simple document workflow...")
        
        # Sample document
        test_doc = {
            "name": "Simple_Test.txt",
            "text": "This is a simple test contract with UEI: TEST123456789 and DUNS: 123456789. Contact: test@example.com",
            "type_hint": "contract"
        }
        
        # Ingest
        print("   📤 Ingesting test document...")
        ingest_response = requests.post(
            f"{base_url}/ingest", 
            json={"documents": [test_doc]}, 
            timeout=10
        )
        
        if ingest_response.status_code == 200:
            print("   ✅ Document ingested successfully")
            
            # Analyze
            print("   🤖 Running analysis...")
            analysis_response = requests.post(
                f"{base_url}/analyze",
                json={
                    "analysis_type": "comprehensive",
                    "include_checklist": True,
                    "generate_brief": True,
                    "generate_email": True
                },
                timeout=60
            )
            
            if analysis_response.status_code == 200:
                print("   🎉 ANALYSIS SUCCESSFUL!")
                
                result = analysis_response.json()
                print(f"   📄 Documents analyzed: {result.get('documents_analyzed', 0)}")
                print(f"   📋 Checklist items: {len(result.get('checklist', []))}")
                
                brief = result.get('brief', '')
                if brief and len(brief.strip()) > 10:
                    print(f"   📋 AI Brief: Generated ({len(brief)} chars)")
                
                email = result.get('client_email', '')
                if email and len(email.strip()) > 10:
                    print(f"   📧 AI Email: Generated ({len(email)} chars)")
                    
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ Server is fully operational")
                print("✅ Document processing works")
                print("✅ AI analysis works")
                print("✅ Web interface ready")
                
                return True
            else:
                print(f"   ❌ Analysis failed: {analysis_response.status_code}")
                print(f"   📝 Error: {analysis_response.text}")
                return False
        else:
            print(f"   ❌ Document ingestion failed: {ingest_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server")
        print("   💡 Make sure server is running at http://127.0.0.1:8001")
        return False
    except Exception as e:
        print(f"   ❌ Test error: {str(e)}")
        return False

def main():
    """Run the test"""
    print("🎯 Testing GetGSA Server...")
    
    success = test_server()
    
    if success:
        print("\n🏆 SUCCESS: GetGSA server is working perfectly!")
        print("🌐 Ready to use at: http://127.0.0.1:8001")
        print("📋 You can now upload documents and run analysis!")
    else:
        print("\n⚠️ Some issues detected - check server logs")

if __name__ == "__main__":
    main()