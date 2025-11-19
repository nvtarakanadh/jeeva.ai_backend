#!/usr/bin/env python3
"""
Test script to verify simplified summary is included in API response
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from ai_analysis.models import AIAnalysis
from ai_analysis.serializers import AIAnalysisSerializer

def test_serializer():
    """Test if the serializer includes simplified summary"""
    print("🧪 Testing AIAnalysisSerializer...")
    
    # Create a test AI analysis record
    test_analysis = AIAnalysis.objects.create(
        record_id='test-record-123',
        summary='Test summary for analysis',
        simplified_summary='This is a test simplified summary in simple language.',
        key_findings=['Finding 1', 'Finding 2'],
        risk_warnings=['Warning 1'],
        recommendations=['Recommendation 1'],
        confidence=0.85,
        analysis_type='Test Analysis',
        disclaimer='Test disclaimer',
        record_title='Test Record'
    )
    
    # Serialize the data
    serializer = AIAnalysisSerializer(test_analysis)
    serialized_data = serializer.data
    
    print("✅ Serialized data:")
    print(f"📝 Summary: {serialized_data.get('summary', 'NOT FOUND')}")
    print(f"🔍 Simplified Summary: {serialized_data.get('simplifiedSummary', 'NOT FOUND')}")
    print(f"🔍 Simplified Summary (snake_case): {serialized_data.get('simplified_summary', 'NOT FOUND')}")
    print(f"🔍 Analysis Type: {serialized_data.get('analysis_type', 'NOT FOUND')}")
    
    # Check if simplified summary is present
    if serialized_data.get('simplifiedSummary'):
        print("\n✅ Simplified summary is properly included in API response!")
        print(f"📋 Content: {serialized_data['simplifiedSummary']}")
    else:
        print("\n❌ Simplified summary is missing from API response!")
    
    # Clean up
    test_analysis.delete()
    
    return serialized_data.get('simplifiedSummary') is not None

if __name__ == "__main__":
    success = test_serializer()
    print(f"\n🎯 Test result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
