#!/usr/bin/env python3
"""
Test script for the new medicine analysis functionality
"""
import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from ai_analysis.ai_services import generate_predictive_insights_from_medicines

def test_medicine_analysis():
    """Test the medicine analysis functionality"""
    print("Testing Medicine Analysis Functionality")
    print("=" * 50)
    
    # Test with sample medicine names
    test_medicines = [
        "Metformin",
        "Lisinopril", 
        "Atorvastatin",
        "Aspirin"
    ]
    
    try:
        print(f"Testing with medicines: {', '.join(test_medicines)}")
        print("\nGenerating predictive insights...")
        
        # Generate insights
        result = generate_predictive_insights_from_medicines(test_medicines)
        
        print("\n[SUCCESS] Analysis completed successfully!")
        print(f"Summary: {result['summary']}")
        print(f"Analysis Type: {result['analysisType']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Number of Risk Warnings: {len(result['riskWarnings'])}")
        print(f"Number of Recommendations: {len(result['recommendations'])}")
        print(f"Number of Predictive Insights: {len(result.get('predictiveInsights', []))}")
        
        print("\n[RISK WARNINGS]")
        for i, warning in enumerate(result['riskWarnings'][:3], 1):
            print(f"  {i}. {warning}")
        
        print("\n[RECOMMENDATIONS]")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
        
        if result.get('predictiveInsights'):
            print("\n[PREDICTIVE INSIGHTS]")
            for i, insight in enumerate(result['predictiveInsights'][:3], 1):
                print(f"  {i}. {insight}")
        
        print(f"\n[REPORT] Detailed Report Length: {len(result.get('detailedReport', ''))} characters")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_medicine_analysis()
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILED] Tests failed!")
        sys.exit(1)
