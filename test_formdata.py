#!/usr/bin/env python3
"""
Test script to verify FormData handling in medical report endpoint
"""
import requests
import io

def test_formdata_endpoint():
    """Test the medical report endpoint with FormData"""
    print("🧪 Testing Medical Report Endpoint with FormData")
    print("=" * 50)
    
    # Create a dummy file
    dummy_file = io.BytesIO(b"dummy lab report content")
    
    # Prepare FormData
    files = {
        'file': ('test_lab_report.jpg', dummy_file, 'image/jpeg')
    }
    
    data = {
        'title': 'Test Lab Report',
        'description': 'Test lab report analysis',
        'patient_id': 'test-patient-123',
        'uploaded_by': 'test-user-123'
    }
    
    url = "http://127.0.0.1:8000/api/ai/analyze/medical-report/"
    
    print(f"📍 URL: {url}")
    print(f"📋 FormData: {data}")
    print(f"📁 File: test_lab_report.jpg")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
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

if __name__ == "__main__":
    test_formdata_endpoint()
