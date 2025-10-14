#!/usr/bin/env python3
"""
Test script for the enhanced prompt format
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_prompt():
    """Test the enhanced prompt format"""
    print("Testing Enhanced Prompt Format")
    print("=" * 35)
    
    try:
        from ai_analysis.ai_services import generate_predictive_insights_from_medicines
        
        # Test with sample medicine names
        medicine_names = ["Paracetamol", "Ibuprofen"]
        
        print(f"Testing with medicines: {medicine_names}")
        print("Generating analysis with enhanced prompt...")
        
        result = generate_predictive_insights_from_medicines(medicine_names)
        
        print("\n[SUCCESS] Analysis completed!")
        print(f"Summary: {result['summary']}")
        print(f"Analysis Type: {result['analysisType']}")
        print(f"Confidence: {result['confidence']}")
        
        print(f"\nRisk Warnings ({len(result['riskWarnings'])}):")
        for i, warning in enumerate(result['riskWarnings'][:3], 1):
            print(f"  {i}. {warning}")
        
        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nPredictive Insights ({len(result['predictiveInsights'])}):")
        for i, insight in enumerate(result['predictiveInsights'][:3], 1):
            print(f"  {i}. {insight}")
        
        print(f"\nMedicine Names: {result['medicineNames']}")
        
        # Check if detailed report contains the expected format
        detailed_report = result.get('detailedReport', '')
        if '## ' in detailed_report and '**Risk Warnings**' in detailed_report:
            print("\n[SUCCESS] Detailed report contains expected markdown format!")
        else:
            print("\n[WARNING] Detailed report may not contain expected format")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_enhanced_prompt()
    if success:
        print("\n[SUCCESS] Enhanced prompt test completed!")
    else:
        print("\n[FAILED] Enhanced prompt test failed!")
        sys.exit(1)
