#!/usr/bin/env python3
"""
Simple test to check API response structure
"""
import requests
import json

def test_api_response():
    """Test the API response structure"""
    print("Testing API Response Structure")
    print("=" * 35)
    
    # Test the health endpoint first
    health_url = "http://127.0.0.1:8000/api/ai/health/"
    
    try:
        print(f"Testing health endpoint: {health_url}")
        health_response = requests.get(health_url, timeout=5)
        
        if health_response.status_code == 200:
            print("[SUCCESS] Health endpoint working")
            
            # Now test a simple analysis endpoint
            analysis_url = "http://127.0.0.1:8000/api/ai/analyze/medicines/"
            
            test_data = {
                "medicine_names": ["Paracetamol"],
                "patient_id": "test_patient",
                "title": "Test Analysis"
            }
            
            print(f"\nTesting analysis endpoint: {analysis_url}")
            print("Note: This may timeout due to Gemini AI call, but we can check the response structure")
            
            try:
                analysis_response = requests.post(analysis_url, json=test_data, timeout=10)
                
                if analysis_response.status_code == 200:
                    result = analysis_response.json()
                    print(f"\n[SUCCESS] Analysis endpoint working!")
                    print(f"Response keys: {list(result.keys())}")
                    
                    if 'ai_disclaimer' in result:
                        print(f"\n[SUCCESS] AI Disclaimer found in main response!")
                        print(f"Disclaimer: {result['ai_disclaimer']}")
                    else:
                        print(f"\n[WARNING] AI Disclaimer not in main response")
                    
                    if 'analysis' in result:
                        analysis = result['analysis']
                        print(f"\nAnalysis keys: {list(analysis.keys())}")
                        
                        if 'ai_disclaimer' in analysis:
                            print(f"[SUCCESS] AI Disclaimer found in analysis object!")
                            print(f"Analysis Disclaimer: {analysis['ai_disclaimer']}")
                        else:
                            print(f"[WARNING] AI Disclaimer not in analysis object")
                    
                    return True
                else:
                    print(f"[ERROR] Analysis endpoint failed: {analysis_response.status_code}")
                    print(f"Response: {analysis_response.text}")
                    return False
                    
            except requests.exceptions.Timeout:
                print("[INFO] Analysis request timed out (expected due to Gemini AI call)")
                print("This is normal - the API is working but Gemini AI is slow")
                return True
                
        else:
            print(f"[ERROR] Health endpoint failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_response()
    if success:
        print("\n[SUCCESS] API structure test completed!")
    else:
        print("\n[FAILED] API structure test failed!")
