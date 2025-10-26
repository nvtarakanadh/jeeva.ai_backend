#!/usr/bin/env python3
"""
Test script for Dr7.ai API integration
This script tests the connectivity and basic functionality of the Dr7.ai API
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def test_dr7_connectivity():
    """Test Dr7.ai API connectivity"""
    print("🔍 Testing Dr7.ai API connectivity...")
    
    try:
        from ai_analysis.ai_services import test_dr7_api_connectivity
        
        if test_dr7_api_connectivity():
            print("✅ Dr7.ai API connectivity test passed!")
            return True
        else:
            print("❌ Dr7.ai API connectivity test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Dr7.ai connectivity: {str(e)}")
        return False

def test_dr7_text_analysis():
    """Test Dr7.ai text analysis functionality"""
    print("\n🔍 Testing Dr7.ai text analysis...")
    
    try:
        from ai_analysis.ai_services import analyze_text_with_dr7
        
        # Test with sample prescription text
        sample_text = """
        Prescription for John Doe
        Date: 2024-01-15
        
        Medications:
        1. Metformin 500mg - Take twice daily with meals
        2. Lisinopril 10mg - Take once daily in the morning
        3. Atorvastatin 20mg - Take once daily at bedtime
        
        Instructions: Follow up in 3 months for blood work
        """
        
        result = analyze_text_with_dr7(sample_text, "prescription")
        
        if result and result.get('summary'):
            print("✅ Dr7.ai text analysis test passed!")
            print(f"📝 Analysis summary length: {len(result['summary'])} characters")
            print(f"🔍 Source model: {result.get('source_model', 'unknown')}")
            return True
        else:
            print("❌ Dr7.ai text analysis test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Dr7.ai text analysis: {str(e)}")
        return False

def test_health_record_analysis():
    """Test health record analysis with Dr7.ai integration"""
    print("\n🔍 Testing health record analysis with Dr7.ai...")
    
    try:
        from ai_analysis.ai_services import analyze_health_record_with_ai
        
        # Test with sample health record data
        sample_record = {
            'record_type': 'lab_report',
            'title': 'Blood Test Results',
            'description': """
            Complete Blood Count Results:
            - Hemoglobin: 12.5 g/dL (Normal: 12-16)
            - White Blood Cells: 8.2 K/uL (Normal: 4-11)
            - Platelets: 250 K/uL (Normal: 150-450)
            - Glucose: 95 mg/dL (Normal: 70-100)
            
            All values are within normal range.
            """
        }
        
        result = analyze_health_record_with_ai(sample_record)
        
        if result and result.get('summary'):
            print("✅ Health record analysis test passed!")
            print(f"📝 Analysis summary length: {len(result['summary'])} characters")
            print(f"🔍 Analysis type: {result.get('analysisType', 'unknown')}")
            return True
        else:
            print("❌ Health record analysis test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health record analysis: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Dr7.ai API Integration Tests")
    print("=" * 50)
    
    # Check if API key is configured
    if not hasattr(settings, 'DR7_API_KEY') or not settings.DR7_API_KEY:
        print("❌ DR7_API_KEY not configured in Django settings")
        print("Please add DR7_API_KEY to your environment variables")
        return False
    
    print(f"🔑 Using Dr7.ai API key: {settings.DR7_API_KEY[:10]}...")
    
    # Run tests
    tests = [
        test_dr7_connectivity,
        test_dr7_text_analysis,
        test_health_record_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dr7.ai integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
