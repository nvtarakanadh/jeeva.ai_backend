#!/usr/bin/env python3
"""
Test script to verify AI analysis endpoints are working correctly
"""
import requests
import json

# Test data
test_data_prescription = {
    "record_id": "test-prescription-123",
    "file_name": "image1.jpg",
    "record_type": "prescription",
    "title": "Test Prescription",
    "description": "Test prescription analysis",
    "service_date": "2025-10-23T13:43:22.934Z",
    "file_url": "https://example.com/test-prescription.jpg",
    "patient_id": "test-patient-123"
}

test_data_lab = {
    "record_id": "test-lab-456",
    "file_name": "image5.jpg", 
    "record_type": "lab-result",
    "title": "Test Lab Report",
    "description": "Test lab report analysis",
    "service_date": "2025-10-23T13:43:22.934Z",
    "file_url": "https://example.com/test-lab.jpg",
    "patient_id": "test-patient-123"
}

def test_endpoint(url, data, endpoint_name):
    """Test an endpoint and print results"""
    print(f"\n🧪 Testing {endpoint_name}")
    print(f"📍 URL: {url}")
    print(f"📋 Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Response Summary: {result.get('analysis', {}).get('summary', 'No summary')[:100]}...")
            print(f"🔍 Key Findings Count: {len(result.get('analysis', {}).get('key_findings', []))}")
            print(f"⚠️ Risk Warnings Count: {len(result.get('analysis', {}).get('risk_warnings', []))}")
            print(f"💡 Recommendations Count: {len(result.get('analysis', {}).get('recommendations', []))}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request Failed: {str(e)}")

def main():
    print("🚀 Testing AI Analysis Endpoints")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000/api/ai"
    
    # Test prescription endpoint
    test_endpoint(
        f"{base_url}/analyze/health-record/",
        test_data_prescription,
        "Prescription Analysis (health-record endpoint)"
    )
    
    # Test lab report endpoint
    test_endpoint(
        f"{base_url}/analyze/medical-report/",
        test_data_lab,
        "Lab Report Analysis (medical-report endpoint)"
    )
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete")

if __name__ == "__main__":
    main()
