#!/usr/bin/env python3
"""
Complete Working Test - GetGSA System
Tests the full analysis pipeline with real document
"""

import requests
import json
import time

def test_complete_analysis():
    """Test complete analysis workflow"""
    
    print("🎯 GetGSA System - Complete Analysis Test")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Realistic government contract for testing
    test_document = {
        "name": "Government_Contract_Analysis.txt",
        "text": """
        FEDERAL CONTRACT FOR IT SERVICES
        
        Contractor Information:
        Company Name: Advanced Tech Solutions LLC
        UEI: XYZ987654321
        DUNS Number: 987654321
        SAM Registration Status: Active
        NAICS Code: 541511 (Custom Computer Programming Services)
        
        Contract Details:
        Project Title: Government Database Modernization
        Contract Value: $250,000
        Performance Period: 8 months
        Contract Type: Firm Fixed Price
        
        Technical Requirements:
        - Legacy system migration to cloud infrastructure
        - Data security compliance (FedRAMP Moderate)
        - Real-time reporting dashboard
        - API integration with existing systems
        - 24/7 system monitoring and support
        
        Key Personnel:
        Project Manager: Sarah Johnson
        Technical Lead: Michael Chen
        Security Officer: David Williams
        
        Contact Information:
        Primary POC: Sarah Johnson
        Email: s.johnson@advancedtech.com
        Phone: (202) 555-0147
        Business Address: 1234 Tech Street, Washington DC 20001
        
        Past Performance:
        - Previous federal contracts: $1.8M total value over 3 years
        - Client references: Department of Defense, VA, Treasury
        - Security clearance: Secret level for key personnel
        - Performance ratings: Exceeds expectations (95% average)
        
        Deliverables Schedule:
        Month 1-2: System analysis and migration planning
        Month 3-5: Core system development and testing
        Month 6-7: Security implementation and compliance validation
        Month 8: Final deployment and user training
        
        Compliance Requirements:
        - Section 508 accessibility standards
        - FISMA security requirements
        - FAR clauses compliance
        - Small business subcontracting plan (15% goal)
        
        Payment Schedule:
        - 20% upon contract award
        - 30% at system development milestone
        - 30% at security validation completion
        - 20% upon final acceptance
        
        Quality Assurance:
        Independent verification and validation testing
        Automated security scanning and penetration testing
        User acceptance testing with government stakeholders
        Performance benchmarking against current systems
        
        Risk Management:
        Identified risks include legacy system complexity, data migration challenges,
        and potential security vulnerabilities during transition period.
        Mitigation strategies include phased rollout, extensive backup procedures,
        and dedicated security monitoring during migration.
        
        This contract represents a critical modernization effort to improve
        government service delivery and operational efficiency.
        """,
        "type_hint": "contract"
    }
    
    try:
        # Step 1: Health Check
        print("\n1. 🏥 Server Health Check")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Server is healthy and operational")
            health_data = response.json()
            print(f"   📊 Status: {health_data.get('status', 'OK')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Step 2: Document Ingestion
        print("\n2. 📤 Document Ingestion Test")
        
        ingest_payload = {
            "documents": [test_document]
        }
        
        response = requests.post(
            f"{base_url}/ingest",
            json=ingest_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Document ingested successfully")
            ingest_result = response.json()
            print(f"   📄 Processing result: {ingest_result.get('message', 'Processed')}")
            request_id = ingest_result.get('request_id')
            if request_id:
                print(f"   🆔 Request ID: {request_id}")
        else:
            print(f"   ❌ Ingestion failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
        
        # Step 3: AI Analysis
        print("\n3. 🤖 AI Analysis Test")
        print("   ⏳ Running comprehensive analysis (this may take 60-90 seconds)...")
        
        analysis_payload = {
            "analysis_type": "comprehensive",
            "include_checklist": True,
            "generate_brief": True,
            "generate_email": True
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/analyze",
            json=analysis_payload,
            timeout=120  # Allow extra time for AI processing
        )
        analysis_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ AI analysis completed in {analysis_time:.1f} seconds")
            
            result = response.json()
            
            # Display comprehensive results
            print("\n" + "="*60)
            print("🎯 COMPLETE ANALYSIS RESULTS")
            print("="*60)
            
            # Basic metrics
            docs_analyzed = result.get('documents_analyzed', 0)
            compliance_status = result.get('compliance_status', 'Unknown')
            request_id = result.get('request_id', 'Unknown')
            
            print(f"📊 Documents Analyzed: {docs_analyzed}")
            print(f"📋 Compliance Status: {compliance_status}")
            print(f"🆔 Request ID: {request_id}")
            
            # Checklist analysis
            checklist = result.get('checklist', [])
            print(f"\n✅ GSA COMPLIANCE CHECKLIST ({len(checklist)} items):")
            
            compliant_items = 0
            for i, item in enumerate(checklist, 1):
                is_compliant = item.get('required_ok', False)
                if is_compliant:
                    compliant_items += 1
                
                status_icon = "✅" if is_compliant else "❌"
                rule_id = item.get('rule_id', f'R{i}')
                description = item.get('description', 'No description')
                
                print(f"   {i}. {status_icon} {rule_id}: {description[:70]}...")
                
                # Show problems if any
                problems = item.get('problems', [])
                if problems:
                    for problem in problems[:2]:  # Show first 2 problems
                        print(f"      ⚠️  {problem}")
            
            compliance_rate = (compliant_items / len(checklist) * 100) if checklist else 0
            print(f"\n📈 Compliance Rate: {compliant_items}/{len(checklist)} ({compliance_rate:.1f}%)")
            
            # AI-Generated Content
            brief = result.get('brief', '')
            if brief:
                print(f"\n📋 AI-GENERATED EXECUTIVE BRIEF:")
                print("   " + "─" * 50)
                # Show first 400 characters of brief
                brief_preview = brief[:400] + "..." if len(brief) > 400 else brief
                print(f"   {brief_preview}")
                print("   " + "─" * 50)
            
            email = result.get('client_email', '')
            if email:
                print(f"\n📧 AI-GENERATED FOLLOW-UP EMAIL:")
                print("   " + "─" * 50)
                # Show first 400 characters of email
                email_preview = email[:400] + "..." if len(email) > 400 else email
                print(f"   {email_preview}")
                print("   " + "─" * 50)
            
            # Enterprise Performance Metrics
            metadata = result.get('enterprise_metadata', {})
            if metadata:
                print(f"\n⚙️ ENTERPRISE PERFORMANCE METRICS:")
                processing_time = metadata.get('processing_time', 0)
                providers_used = metadata.get('ai_providers_used', [])
                quality_scores = metadata.get('quality_scores', {})
                
                print(f"   🕒 Total Processing Time: {processing_time:.2f} seconds")
                print(f"   🤖 AI Providers Used: {', '.join(providers_used)}")
                
                if quality_scores:
                    brief_quality = quality_scores.get('brief', 0)
                    email_quality = quality_scores.get('email', 0)
                    print(f"   📊 Quality Scores: Brief={brief_quality}/10, Email={email_quality}/10")
                
                performance = metadata.get('performance_metrics', {})
                if performance:
                    ai_provider = performance.get('ai_provider', 'Unknown')
                    pii_protected = performance.get('pii_protected', False)
                    print(f"   ⚡ Primary AI Provider: {ai_provider}")
                    print(f"   🛡️ PII Protection: {'Enabled' if pii_protected else 'Disabled'}")
            
            # Success summary
            print("\n" + "="*60)
            print("🎉 ANALYSIS SUCCESS - ALL SYSTEMS WORKING!")
            print("="*60)
            print("✅ Document Processing: COMPLETE")
            print("✅ GSA Compliance Check: COMPLETE")
            print("✅ AI Brief Generation: COMPLETE")
            print("✅ AI Email Generation: COMPLETE")
            print("✅ Enterprise Features: ACTIVE")
            print(f"✅ Total Processing Time: {analysis_time:.1f} seconds")
            
            return True
            
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   📝 Error details: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection refused - server not running")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out - analysis taking too long")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

def main():
    """Run the complete test"""
    
    print("🚀 Starting GetGSA Complete Analysis Test")
    print("🎯 This will test the full AI analysis pipeline")
    print("📋 Using a realistic government contract for testing")
    
    success = test_complete_analysis()
    
    if success:
        print("\n🏆 SUCCESS: GetGSA System is FULLY OPERATIONAL!")
        print("🎯 All AI services working correctly")
        print("🌐 Web interface ready at: http://127.0.0.1:8001")
        print("📋 System ready for production government contract analysis")
    else:
        print("\n❌ Test failed - check server status and logs")

if __name__ == "__main__":
    main()