#!/usr/bin/env python3
"""
Test the response structure endpoint
"""
import requests
import json

def test_structure():
    """Test the response structure"""
    print("Testing Response Structure")
    print("=" * 30)
    
    url = "http://127.0.0.1:8000/api/ai/test-structure/"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Got response!")
            print(f"Response keys: {list(result.keys())}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\nAnalysis keys: {list(analysis.keys())}")
                
                # Check each field
                fields_to_check = [
                    'summary', 'keyFindings', 'riskWarnings', 'recommendations', 
                    'predictiveInsights', 'ai_disclaimer', 'disclaimer'
                ]
                
                print(f"\nField Analysis:")
                for field in fields_to_check:
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
                    print(f"\n✓ ai_disclaimer in main response")
                    print(f"  Value: {result['ai_disclaimer']}")
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
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_structure()
    if success:
        print("\n[SUCCESS] Structure test completed!")
    else:
        print("\n[FAILED] Structure test failed!")
