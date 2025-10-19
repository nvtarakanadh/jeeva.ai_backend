"""
Simple medical report analysis without complex AI parsing
This provides a basic analysis for testing purposes
"""
import re
from typing import Dict, List

def simple_medical_analysis(extracted_text: str, file_name: str) -> Dict:
    """Simple medical report analysis without AI"""
    
    # Basic text parsing
    text_lower = extracted_text.lower()
    
    # Extract basic information
    patient_name = "Not specified"
    if "patient:" in text_lower:
        patient_match = re.search(r'patient:\s*([^\n\r]+)', text_lower)
        if patient_match:
            patient_name = patient_match.group(1).strip().title()
    
    # Find test values
    test_values = []
    value_patterns = [
        r'(\w+):\s*(\d+(?:\.\d+)?)\s*([^\s\n\r]+)',
        r'(\w+)\s*(\d+(?:\.\d+)?)\s*([^\s\n\r]+)',
    ]
    
    for pattern in value_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            test_name, value, unit = match
            test_values.append({
                'test': test_name.title(),
                'value': value,
                'unit': unit
            })
    
    # Basic risk assessment
    risk_level = "low"
    if any(keyword in text_lower for keyword in ['high', 'elevated', 'abnormal', 'critical']):
        risk_level = "moderate"
    if any(keyword in text_lower for keyword in ['very high', 'severely elevated', 'critical']):
        risk_level = "high"
    
    # Generate basic findings
    key_findings = [
        f"**Medical Report Analysis**: {file_name} - Basic analysis completed",
        f"**Patient Information**: {patient_name}",
        f"**Test Values Found**: {len(test_values)} values identified",
        f"**Risk Assessment**: Overall risk level - {risk_level}",
        f"**Analysis Type**: Basic Medical Report Analysis"
    ]
    
    # Basic recommendations
    recommendations = [
        "💡 **Professional Review**: Consult with your healthcare provider for detailed interpretation",
        "💡 **Follow-up**: Schedule appropriate follow-up based on your healthcare provider's recommendations"
    ]
    
    # Risk warnings
    risk_warnings = [
        "⚠️ **Medical Disclaimer**: This is a basic analysis for informational purposes only",
        "⚠️ **Professional Consultation**: Always consult with qualified healthcare professionals",
        "⚠️ **Not Medical Advice**: This analysis should not replace professional medical advice"
    ]
    
    # Predictive insights
    predictive_insights = [
        f"**Overall Health Risk**: {risk_level.title()}",
        f"**Analysis Confidence**: Basic text analysis completed",
        f"**Recommendation**: Professional medical review recommended"
    ]
    
    return {
        "summary": f"Basic medical report analysis completed for {patient_name}. Found {len(test_values)} test values with {risk_level} overall risk level. Professional medical consultation recommended for detailed interpretation.",
        "keyFindings": key_findings,
        "riskWarnings": risk_warnings,
        "recommendations": recommendations,
        "predictiveInsights": predictive_insights,
        "confidence": 0.6,  # Lower confidence for basic analysis
        "analysisType": "Basic Medical Report Analysis",
        "disclaimer": "This is a basic text analysis and should not replace professional medical advice.",
        "aiDisclaimer": "⚠️ **AI Analysis Disclaimer**: This is a basic text analysis for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance."
    }
