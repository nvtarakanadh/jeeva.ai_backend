#!/usr/bin/env python3
"""
Test script for lab report analysis with simplified summary
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from ai_analysis.ai_services import analyze_lab_report_with_ai

def test_lab_analysis():
    """Test lab report analysis with simplified summary"""
    print("🧪 Testing lab report analysis with simplified summary...")
    
    # Sample lab report data
    lab_data = {
        'record_type': 'lab_test',
        'title': 'Complete Blood Count (CBC)',
        'description': '''
        Patient: John Doe, Age: 35, Male
        
        Complete Blood Count Results:
        - White Blood Cells (WBC): 7.2 K/μL (Normal: 4.5-11.0)
        - Red Blood Cells (RBC): 4.8 M/μL (Normal: 4.5-5.9)
        - Hemoglobin: 14.2 g/dL (Normal: 13.8-17.2)
        - Hematocrit: 42.1% (Normal: 40.7-50.3)
        - Platelets: 285 K/μL (Normal: 150-450)
        - Mean Corpuscular Volume (MCV): 88 fL (Normal: 80-100)
        - Mean Corpuscular Hemoglobin (MCH): 29.6 pg (Normal: 27-33)
        
        Differential Count:
        - Neutrophils: 65% (Normal: 40-70%)
        - Lymphocytes: 28% (Normal: 20-45%)
        - Monocytes: 5% (Normal: 2-10%)
        - Eosinophils: 2% (Normal: 1-4%)
        - Basophils: 0.5% (Normal: 0-1%)
        
        All values are within normal limits.
        ''',
        'file_url': ''
    }
    
    try:
        print("🔍 Starting lab report analysis...")
        result = analyze_lab_report_with_ai(lab_data)
        
        print("✅ Lab analysis completed successfully!")
        print(f"📝 Summary length: {len(result.get('summary', ''))} characters")
        print(f"🔍 Simplified Summary: {result.get('simplifiedSummary', 'NOT FOUND')}")
        print(f"🔍 Analysis Type: {result.get('analysisType', 'Unknown')}")
        print(f"🔍 Source Model: {result.get('source_model', 'Unknown')}")
        
        # Show the simplified summary if it exists
        if result.get('simplifiedSummary'):
            print("\n📋 Simplified Summary Content:")
            print("-" * 50)
            print(result['simplifiedSummary'])
            print("-" * 50)
        else:
            print("\n❌ No simplified summary found in result")
            
        return result
        
    except Exception as e:
        print(f"❌ Error in lab analysis: {str(e)}")
        return None

if __name__ == "__main__":
    test_lab_analysis()
