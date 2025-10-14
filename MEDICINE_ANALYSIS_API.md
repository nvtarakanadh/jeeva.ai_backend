# Medicine Analysis API Documentation

## Overview

The Medicine Analysis API provides AI-powered predictive insights based on extracted medicine names. This feature uses Google's Gemini AI to analyze medicine combinations and provide comprehensive health insights including risk warnings, suggested tests, and predictive analytics.

## New Features

### 1. Predictive Medicine Analysis
- **Function**: `generate_predictive_insights_from_medicines(medicine_names)`
- **Purpose**: Analyzes medicine names and generates comprehensive predictive insights
- **AI Model**: Google Gemini 2.5 Flash

### 2. Enhanced AI Analysis Model
New fields added to `AIAnalysis` model:
- `predictive_insights`: JSON field storing AI-generated predictive insights
- `detailed_report`: Text field with comprehensive medical report
- `medicine_names`: JSON field storing analyzed medicine names

### 3. New API Endpoint
- **URL**: `/api/ai/analyze/medicines/`
- **Method**: POST
- **Content-Type**: application/json

## API Usage

### Request Format

```json
{
    "medicine_names": [
        "Metformin",
        "Lisinopril",
        "Atorvastatin",
        "Aspirin"
    ],
    "patient_id": "patient_123",
    "title": "Medicine Analysis",
    "description": "Analysis of prescribed medicines",
    "uploaded_by": "doctor_456",
    "record_id": "optional_record_id"
}
```

### Response Format

```json
{
    "success": true,
    "record_id": "generated_or_provided_id",
    "analysis": {
        "id": 1,
        "summary": "Predictive analysis completed for 4 medicines...",
        "key_findings": [
            "Analyzed 4 medicines: Metformin, Lisinopril, Atorvastatin, Aspirin",
            "Drug interaction analysis completed",
            "Risk assessment and monitoring recommendations generated",
            "Predictive health insights provided"
        ],
        "risk_warnings": [
            "⚠️ 4 medicines require careful monitoring",
            "⚠️ Potential drug interactions detected",
            "⚠️ Regular health monitoring essential"
        ],
        "recommendations": [
            "💡 Schedule regular blood tests",
            "💡 Monitor vital signs closely",
            "💡 Report any side effects immediately",
            "💡 Follow up with healthcare provider regularly"
        ],
        "predictive_insights": [
            "AI analysis suggests monitoring specific health parameters",
            "Predictive models indicate potential health outcomes",
            "Risk stratification completed based on medicine profile"
        ],
        "confidence": 0.85,
        "analysis_type": "Predictive Medicine Analysis",
        "detailed_report": "Comprehensive medical report in markdown format...",
        "medicine_names": ["Metformin", "Lisinopril", "Atorvastatin", "Aspirin"]
    },
    "health_record": {
        "id": "record_id",
        "patient_id": "patient_123",
        "record_type": "prescription",
        "title": "Medicine Analysis",
        "description": "Analysis of medicines: Metformin, Lisinopril, Atorvastatin, Aspirin",
        "record_date": "2024-01-01T12:00:00Z",
        "uploaded_by": "doctor_456"
    },
    "medicine_names": ["Metformin", "Lisinopril", "Atorvastatin", "Aspirin"]
}
```

## Analysis Components

### 1. Risk Warnings
- Specific safety concerns for each medicine
- Potential drug interactions between medicines
- Contraindications and precautions
- Side effects to monitor

### 2. Suggested Tests
- Blood tests recommended for monitoring
- Imaging studies that might be needed
- Vital signs to track regularly
- Specialized tests for specific medicines

### 3. Predictive Insights
- Potential health outcomes based on medicine combinations
- Risk factors that may develop
- Timeline for expected effects
- Warning signs to watch for

### 4. Detailed Report
Comprehensive markdown report for each medicine including:
- Medicine Name
- Primary Use
- Risk Warnings
- Required Monitoring
- Potential Side Effects
- Drug Interactions
- Lifestyle Considerations
- Follow-up Requirements

## Integration with Existing System

### Prescription Analysis Enhancement
The existing prescription analysis now uses the new predictive insights function:
- Medicine names are extracted from prescription images/text
- Predictive insights are generated using Gemini AI
- Enhanced analysis results include predictive insights

### Backward Compatibility
- All existing API endpoints continue to work
- New fields are optional and have default values
- Existing analysis results are preserved

## Error Handling

### Common Error Scenarios
1. **No Medicine Names**: Returns 400 error if medicine_names is empty
2. **Gemini API Issues**: Returns 500 error with detailed message
3. **Invalid Medicine Names**: Handles gracefully with fallback analysis

### Fallback Behavior
- If JSON parsing fails, provides basic analysis
- If specific medicines aren't recognized, uses general medical guidance
- Always includes medical disclaimers and consultation recommendations

## Testing

### Test Script
Run the test script to verify functionality:
```bash
cd Jeeva_AI_BackEnd
python test_medicine_analysis.py
```

### Manual Testing
Use the API endpoint with sample medicine names:
```bash
curl -X POST http://localhost:8000/api/ai/analyze/medicines/ \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_names": ["Metformin", "Lisinopril"],
    "patient_id": "test_patient",
    "title": "Test Analysis"
  }'
```

## Configuration

### Required Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key for AI analysis
- `FIRECRAWL_API_KEY`: For medicine information lookup (optional)

### Database Migration
The new fields require a database migration:
```bash
python manage.py makemigrations ai_analysis
python manage.py migrate
```

## Security Considerations

1. **API Key Protection**: Ensure Gemini API key is properly secured
2. **Input Validation**: Medicine names are validated and sanitized
3. **Medical Disclaimers**: All responses include appropriate medical disclaimers
4. **Data Privacy**: Patient data is handled according to privacy requirements

## Future Enhancements

1. **Medicine Database Integration**: Direct integration with medicine databases
2. **Dosage Analysis**: Include dosage information in analysis
3. **Patient History**: Consider patient medical history in predictions
4. **Real-time Monitoring**: Continuous monitoring of medicine effects
5. **Alert System**: Automated alerts for potential issues

## Support

For issues or questions regarding the Medicine Analysis API:
1. Check the test script for basic functionality
2. Review error logs for detailed error information
3. Verify API key configuration
4. Ensure database migrations are applied
