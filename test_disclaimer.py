#!/usr/bin/env python3
"""
Test script to verify the AI disclaimer is included in API responses
"""
import requests
import json

def test_disclaimer_in_response():
    """Test that the AI disclaimer is included in the API response"""
    print("Testing AI Disclaimer in API Response")
    print("=" * 40)
    
    # Test the medicine analysis endpoint
    url = "http://127.0.0.1:8000/api/ai/analyze/medicines/"
    
    test_data = {
        "medicine_names": ["Paracetamol", "Ibuprofen"],
        "patient_id": "test_patient_123",
        "title": "Test Medicine Analysis"
    }
    
    try:
        print(f"Making request to: {url}")
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('analysis', {})
            
            print(f"Response status: {response.status_code}")
            print(f"Analysis keys: {list(analysis.keys())}")
            
            # Check if ai_disclaimer is in the response
            if 'ai_disclaimer' in analysis:
                print(f"\n[SUCCESS] AI Disclaimer found in response!")
                print(f"Disclaimer: {analysis['ai_disclaimer']}")
            else:
                print(f"\n[ERROR] AI Disclaimer NOT found in response")
                print(f"Available fields: {list(analysis.keys())}")
            
            # Check if risk_warnings are present
            if 'risk_warnings' in analysis:
                print(f"\n[SUCCESS] Risk Warnings found: {len(analysis['risk_warnings'])} items")
                for i, warning in enumerate(analysis['risk_warnings'][:3], 1):
                    print(f"  {i}. {warning}")
            else:
                print(f"\n[ERROR] Risk Warnings NOT found")
            
            # Check if predictive_insights are present
            if 'predictive_insights' in analysis:
                print(f"\n[SUCCESS] Predictive Insights found: {len(analysis['predictive_insights'])} items")
                for i, insight in enumerate(analysis['predictive_insights'][:3], 1):
                    print(f"  {i}. {insight}")
            else:
                print(f"\n[ERROR] Predictive Insights NOT found")
            
            return True
            
        else:
            print(f"[ERROR] API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the API. Make sure the Django server is running")
        return False
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_disclaimer_in_response()
    if success:
        print("\n[SUCCESS] Disclaimer test completed!")
    else:
        print("\n[FAILED] Disclaimer test failed!")
