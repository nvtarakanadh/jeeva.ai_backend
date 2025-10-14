#!/usr/bin/env python3
"""
Test script to verify the Django server is accessible
"""
import requests
import json

def test_connection():
    """Test if the Django server is accessible"""
    print("Testing Django Server Connection")
    print("=" * 35)
    
    # Test health check endpoint
    health_url = "http://127.0.0.1:8000/api/ai/health/"
    
    try:
        print(f"Testing health check at: {health_url}")
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Server is running!")
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to Django server")
        print("Make sure the server is running with: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n[SUCCESS] Django server is accessible!")
    else:
        print("\n[FAILED] Django server is not accessible!")
