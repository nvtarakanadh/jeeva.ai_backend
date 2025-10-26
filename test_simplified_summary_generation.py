#!/usr/bin/env python3
"""
Test script to verify simplified summary is being generated
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from ai_analysis.ai_services import analyze_health_record_with_ai

def test_simplified_summary_generation():
    """Test if simplified summary is being generated"""
    print("🧪 Testing simplified summary generation...")
    
    # Test data
    test_record = {
        'record_type': 'lab_report',
        'title': 'Test Lab Report',
        'description': '''
        Patient: John Doe
        Age: 35
        Date: 2025-10-26
        
        Complete Blood Count:
        - White Blood Cells: 7.2 K/μL (Normal: 4.0-10.0)
        - Red Blood Cells: 4.8 M/μL (Normal: 4.5-5.5)
        - Hemoglobin: 14.2 g/dL (Normal: 13.0-17.0)
        - Platelets: 285 K/μL (Normal: 150-450)
        
        All values within normal limits.
        ''',
        'patient_id': 'test-patient-123',
        'service_date': '2025-10-26T10:00:00Z',
        'uploaded_by': 'test-user'
    }
    
    try:
        print("🔄 Generating AI analysis...")
        result = analyze_health_record_with_ai(test_record)
        
        print("✅ Analysis completed!")
        print(f"📝 Summary length: {len(result.get('summary', ''))}")
        print(f"🔍 Simplified Summary: {result.get('simplifiedSummary', 'NOT FOUND')}")
        print(f"🔍 Analysis Type: {result.get('analysisType', 'Unknown')}")
        
        if result.get('simplifiedSummary'):
            print("\n📋 Simplified Summary Content:")
            print("-" * 50)
            print(result['simplifiedSummary'])
            print("-" * 50)
            return True
        else:
            print("\n❌ No simplified summary generated!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simplified_summary_generation()
    if success:
        print("\n🎉 Simplified summary generation is working!")
    else:
        print("\n💥 Simplified summary generation is NOT working!")
        sys.exit(1)
