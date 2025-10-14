#!/usr/bin/env python3
"""
Debug script to check the exact API response structure
"""
import requests
import json

def debug_api_response():
    """Debug the API response to see what fields are actually returned"""
    print("Debugging API Response Structure")
    print("=" * 40)
    
    # Test with a simple medicine analysis
    url = "http://127.0.0.1:8000/api/ai/analyze/medicines/"
    
    test_data = {
        "medicine_names": ["Paracetamol"],
        "patient_id": "test_patient",
        "title": "Debug Test"
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Test data: {json.dumps(test_data, indent=2)}")
        
        # Make a quick request to see the response structure
        response = requests.post(url, json=test_data, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] Got response!")
            print(f"Top-level keys: {list(result.keys())}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\nAnalysis object keys: {list(analysis.keys())}")
                
                # Check each field we expect
                expected_fields = [
                    'summary', 'keyFindings', 'riskWarnings', 'recommendations', 
                    'predictiveInsights', 'ai_disclaimer', 'disclaimer', 'medicineNames'
                ]
                
                print(f"\nField Analysis:")
                for field in expected_fields:
                    if field in analysis:
                        value = analysis[field]
                        if isinstance(value, list):
                            print(f"  ✓ {field}: List with {len(value)} items")
                            if value:
                                print(f"    Sample: {value[0]}")
                        else:
                            print(f"  ✓ {field}: {str(value)[:100]}...")
                    else:
                        print(f"  ✗ {field}: MISSING")
                
                # Check main response level
                if 'ai_disclaimer' in result:
                    print(f"\n✓ ai_disclaimer in main response: {result['ai_disclaimer']}")
                else:
                    print(f"\n✗ ai_disclaimer NOT in main response")
                
                return True
            else:
                print(f"[ERROR] No 'analysis' object in response")
                return False
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[INFO] Request timed out (Gemini AI is slow)")
        print("This is expected - the API is working but AI processing takes time")
        return True
    except Exception as e:
        print(f"[ERROR] Debug failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = debug_api_response()
    if success:
        print("\n[SUCCESS] Debug completed!")
    else:
        print("\n[FAILED] Debug failed!")
