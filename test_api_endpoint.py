#!/usr/bin/env python3
"""
Test script for the medicine analysis API endpoint
"""
import requests
import json

def test_medicine_api():
    """Test the medicine analysis API endpoint"""
    print("Testing Medicine Analysis API Endpoint")
    print("=" * 45)
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/ai/analyze/medicines/"
    
    # Test data
    test_data = {
        "medicine_names": ["Paracetamol", "Ibuprofen"],
        "patient_id": "test_patient_123",
        "title": "Test Medicine Analysis",
        "description": "Testing the new predictive insights functionality"
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Test data: {json.dumps(test_data, indent=2)}")
        print("\nSending request...")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] API call successful!")
            print(f"Record ID: {result.get('record_id', 'N/A')}")
            
            analysis = result.get('analysis', {})
            print(f"\nAnalysis Summary:")
            print(f"  Summary: {analysis.get('summary', 'N/A')}")
            print(f"  Analysis Type: {analysis.get('analysis_type', 'N/A')}")
            print(f"  Confidence: {analysis.get('confidence', 'N/A')}")
            
            print(f"\nRisk Warnings ({len(analysis.get('risk_warnings', []))}):")
            for i, warning in enumerate(analysis.get('risk_warnings', [])[:3], 1):
                print(f"  {i}. {warning}")
            
            print(f"\nRecommendations ({len(analysis.get('recommendations', []))}):")
            for i, rec in enumerate(analysis.get('recommendations', [])[:3], 1):
                print(f"  {i}. {rec}")
            
            if analysis.get('predictive_insights'):
                print(f"\nPredictive Insights ({len(analysis.get('predictive_insights', []))}):")
                for i, insight in enumerate(analysis.get('predictive_insights', [])[:3], 1):
                    print(f"  {i}. {insight}")
            
            print(f"\nMedicine Names: {analysis.get('medicine_names', [])}")
            
            # Check if we have clean medicine names
            medicine_names = analysis.get('medicine_names', [])
            if medicine_names and all(med and not any(char in str(med) for char in ['[', ']', '`', 'json']) for med in medicine_names):
                print("\n[PASS] Medicine names are clean!")
            else:
                print("\n[FAIL] Medicine names still contain formatting artifacts")
            
            return True
            
        else:
            print(f"\n[ERROR] API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to the API. Make sure the Django server is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out. The API might be taking too long to respond")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_medicine_api()
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILED] Tests failed!")
