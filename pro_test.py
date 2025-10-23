#!/usr/bin/env python3
"""
PRO TEST: Comprehensive test of both AI analysis endpoints
"""
import requests
import json

def test_prescription_endpoint():
    """Test prescription analysis endpoint"""
    print("\n🧪 PRO TEST: Prescription Analysis")
    print("=" * 50)
    
    data = {
        "record_id": "test-prescription-pro",
        "file_name": "image1.jpg",
        "record_type": "prescription",  # EXACT value from frontend
        "title": "Test Prescription",
        "description": "Test prescription analysis",
        "service_date": "2025-10-23T13:43:22.934Z",
        "file_url": "https://example.com/test-prescription.jpg",
        "patient_id": "test-patient-123"
    }
    
    url = "http://127.0.0.1:8000/api/ai/analyze/health-record/"
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('analysis', {}).get('summary', '')
            
            # Check if it's prescription analysis
            if "Multi-medication Analysis" in summary and "prescription" in summary.lower():
                print("✅ CORRECT: Prescription analysis returned")
                print(f"📊 Summary: {summary[:100]}...")
            else:
                print("❌ WRONG: Expected prescription analysis but got different result")
                print(f"📊 Summary: {summary[:100]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_lab_report_endpoint():
    """Test lab report analysis endpoint"""
    print("\n🧪 PRO TEST: Lab Report Analysis")
    print("=" * 50)
    
    data = {
        "record_id": "test-lab-pro",
        "file_name": "image5.jpg",
        "record_type": "lab-result",  # EXACT value from frontend
        "title": "Test Lab Report",
        "description": "Test lab report analysis",
        "service_date": "2025-10-23T13:43:22.934Z",
        "file_url": "https://example.com/test-lab.jpg",
        "patient_id": "test-patient-123"
    }
    
    url = "http://127.0.0.1:8000/api/ai/analyze/medical-report/"
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('analysis', {}).get('summary', '')
            
            # Check if it's lab report analysis
            if "Laboratory Analysis" in summary and "lab report" in summary.lower():
                print("✅ CORRECT: Lab report analysis returned")
                print(f"📊 Summary: {summary[:100]}...")
            else:
                print("❌ WRONG: Expected lab report analysis but got different result")
                print(f"📊 Summary: {summary[:100]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def main():
    print("🚀 PRO COMPREHENSIVE TEST")
    print("Testing both endpoints with EXACT frontend values")
    print("=" * 60)
    
    test_prescription_endpoint()
    test_lab_report_endpoint()
    
    print("\n" + "=" * 60)
    print("🏁 PRO TEST COMPLETE")

if __name__ == "__main__":
    main()
