# 🩻 MRI/CT Scan Analysis with Dr7.ai API

This document describes the implementation of MRI/CT scan analysis features using the Dr7.ai API in the Jeeva.AI project.

## 🎯 Overview

The MRI/CT scan analysis module provides AI-powered radiology image interpretation using the Dr7.ai API with the `medsiglip-v1` model. It offers comprehensive analysis of MRI, CT, and X-ray scans with detailed findings, clinical significance, and recommendations.

## 🏗️ Architecture

### Backend Components

1. **Database Model**: `MRI_CT_Analysis` in `ai_analysis/models.py`
2. **API Service**: Dr7.ai integration in `ai_analysis/ai_services.py`
3. **Views**: REST API endpoints in `ai_analysis/views.py`
4. **Serializers**: Data validation in `ai_analysis/serializers.py`
5. **URL Routes**: API endpoints in `ai_analysis/urls.py`

### Frontend Components

1. **Service**: `mriCtAnalysisService.ts` - API communication
2. **Modal**: `MRIAnalysisModal.tsx` - Analysis display
3. **Button**: `MRIAnalysisButton.tsx` - Analysis trigger
4. **Integration**: `HealthRecordAIAnalysis.tsx` - Health records integration

## 🔧 Setup Instructions

### 1. Environment Configuration

Add your Dr7.ai API key to the environment variables:

```bash
# .env file
DR7_API_KEY=your_dr7_api_key_here
```

### 2. Database Migration

Run the database migration to create the MRI/CT analysis table:

```bash
python manage.py makemigrations ai_analysis
python manage.py migrate
```

### 3. API Key Configuration

Ensure your Dr7.ai API key is properly configured in Django settings:

```python
# settings.py
DR7_API_KEY = os.getenv('DR7_API_KEY')
```

## 📡 API Endpoints

### 1. Analyze MRI/CT Scan
```
POST /api/ai/analyze/mri-ct-scan/
```

**Request Body:**
```json
{
  "record_id": "uuid",
  "patient_id": "uuid",
  "scan_type": "MRI|CT|XRAY",
  "image_url": "https://...",
  "doctor_access": false
}
```

**Response:**
```json
{
  "message": "MRI scan analysis completed successfully",
  "analysis": {
    "id": 1,
    "record_id": "uuid",
    "patient_id": "uuid",
    "scan_type": "MRI",
    "summary": "Detailed analysis summary (>100 words)...",
    "findings": ["Finding 1", "Finding 2"],
    "region": "brain",
    "clinical_significance": "Clinical interpretation...",
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "risk_level": "moderate",
    "source_model": "medsiglip-v1",
    "doctor_access": false,
    "created_at": "2025-01-01T00:00:00Z",
    "disclaimer": "Medical disclaimer text..."
  }
}
```

### 2. Get MRI/CT Analysis
```
GET /api/ai/mri-ct-analysis/{record_id}/
```

### 3. List MRI/CT Analyses
```
GET /api/ai/mri-ct-analyses/?patient_id={patient_id}&scan_type={scan_type}
```

### 4. Update Doctor Access
```
PUT /api/ai/mri-ct-analysis/{record_id}/doctor-access/
```

## 🧠 AI Analysis Features

### Dr7.ai Integration

- **Model**: `medsiglip-v1` (Multimodal Image + Text)
- **Capability**: Radiology image understanding
- **Input**: Base64 encoded images (JPG, PNG, DICOM)
- **Output**: Structured medical analysis

### Analysis Components

1. **Summary**: Detailed paragraph (>100 words) with patient-understandable explanation
2. **Findings**: Structured list of detected abnormalities
3. **Region**: Anatomical region identification
4. **Clinical Significance**: Medical interpretation and potential conditions
5. **Recommendations**: Next-step advice and follow-up recommendations
6. **Risk Level**: Automated risk assessment (low, moderate, high, critical)

### Risk Level Determination

The system automatically determines risk levels based on keyword analysis:

- **Critical**: emergency, urgent, critical, severe, life-threatening, acute
- **High**: abnormal, concerning, significant, pathological, lesion, mass
- **Moderate**: mild, slight, minor, incidental, follow-up
- **Low**: Default for normal findings

## 🎨 Frontend Integration

### Health Records Integration

The MRI/CT analysis is automatically integrated into the health records system:

1. **Automatic Detection**: Scans are automatically detected based on file names and titles
2. **Enhanced Button**: AI Analytics button shows scan-specific icons and text
3. **Dual Analysis**: Supports both regular AI analysis and specialized MRI/CT analysis
4. **Consent Management**: Patients can control doctor access to their scan results

### UI Components

#### MRIAnalysisModal
- Comprehensive analysis display
- Risk level indicators
- Findings and recommendations
- Doctor access controls
- Medical disclaimer

#### MRIAnalysisButton
- Smart analysis triggering
- Progress indicators
- Error handling
- Existing analysis detection

## 🔒 Security & Privacy

### Data Protection
- Secure API key storage
- Patient consent management
- Doctor access controls
- Medical disclaimer display

### Consent Management
- Patients control doctor access
- Granular permission system
- Audit trail for access changes

## 📊 Database Schema

### MRI_CT_Analysis Table

```sql
CREATE TABLE mri_ct_analysis (
    id SERIAL PRIMARY KEY,
    record_id VARCHAR(255) UNIQUE NOT NULL,
    patient_id VARCHAR(255) NOT NULL,
    scan_type VARCHAR(10) NOT NULL, -- MRI, CT, XRAY
    summary TEXT NOT NULL,
    findings JSON NOT NULL,
    region VARCHAR(100) NOT NULL,
    clinical_significance TEXT NOT NULL,
    recommendations JSON NOT NULL,
    risk_level VARCHAR(20) NOT NULL, -- low, moderate, high, critical
    source_model VARCHAR(50) DEFAULT 'medsiglip-v1',
    doctor_access BOOLEAN DEFAULT FALSE,
    api_usage_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Usage Examples

### Backend Usage

```python
from ai_analysis.ai_services import analyze_mri_ct_scan_with_dr7

# Analyze an MRI scan
with open('mri_scan.jpg', 'rb') as f:
    image_bytes = f.read()

result = analyze_mri_ct_scan_with_dr7(image_bytes, 'MRI')
print(result['summary'])
print(result['findings'])
```

### Frontend Usage

```typescript
import { analyzeMRICTScan } from '@/services/mriCtAnalysisService';

const request = {
  record_id: 'uuid',
  patient_id: 'uuid',
  scan_type: 'MRI',
  image_url: 'https://example.com/scan.jpg',
  doctor_access: false
};

const result = await analyzeMRICTScan(request);
console.log(result.analysis.summary);
```

## 🔧 Error Handling

### API Errors
- Invalid image format
- API rate limiting
- Network connectivity issues
- Authentication failures

### Fallback Responses
- Graceful degradation when Dr7.ai API fails
- Manual review recommendations
- Error logging and monitoring

## 📈 Monitoring & Analytics

### API Usage Tracking
- Token consumption monitoring
- Request success/failure rates
- Performance metrics
- Cost tracking

### Analysis Quality
- Summary length validation
- Risk level accuracy
- User feedback collection
- Continuous improvement

## 🚨 Medical Disclaimer

**Important**: This MRI/CT Scan analysis is automatically generated by an AI model (Dr7.ai) and is provided **for informational purposes only**. It does **not substitute for clinical judgment or diagnostic evaluation**. Always consult a qualified radiologist or medical professional for interpretation and treatment decisions.

## 🔄 Future Enhancements

1. **Multi-slice Analysis**: Support for MRI slice sequences
2. **DICOM Support**: Native DICOM file processing
3. **Comparative Analysis**: Before/after scan comparisons
4. **Integration**: PACS system integration
5. **Mobile Support**: Mobile-optimized analysis interface

## 📞 Support

For technical support or questions about the MRI/CT analysis feature:

- **Backend Issues**: Check Django logs and API responses
- **Frontend Issues**: Check browser console and network requests
- **API Issues**: Verify Dr7.ai API key and quota limits
- **Database Issues**: Check migration status and table structure

---

**Built with ❤️ for better healthcare using Dr7.ai technology**
