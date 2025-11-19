#!/usr/bin/env python3
"""
Test MRI/CT analysis with Dr7.ai API
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def test_mri_analysis():
    """Test MRI analysis with Dr7.ai API"""
    print("🔍 Testing MRI analysis with Dr7.ai...")
    
    try:
        from ai_analysis.ai_services import analyze_mri_ct_scan_with_dr7_new
        
        # Create a small test image (1x1 pixel JPEG)
        test_image = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        result = analyze_mri_ct_scan_with_dr7_new(test_image, 'MRI')
        print('✅ MRI analysis completed successfully')
        print(f'📝 Summary length: {len(result.get("summary", ""))} characters')
        print(f'🔍 Simplified Summary: {result.get("simplifiedSummary", "NOT FOUND")}')
        print(f'🔍 Source model: {result.get("source_model", "unknown")}')
        
        # Show the simplified summary if it exists
        if result.get('simplifiedSummary'):
            print("\n📋 Simplified Summary Content:")
            print("-" * 50)
            print(result['simplifiedSummary'])
            print("-" * 50)
        else:
            print("\n❌ No simplified summary found in result")
        return True
        
    except Exception as e:
        print(f'❌ MRI analysis failed: {str(e)}')
        return False

if __name__ == "__main__":
    success = test_mri_analysis()
    sys.exit(0 if success else 1)
