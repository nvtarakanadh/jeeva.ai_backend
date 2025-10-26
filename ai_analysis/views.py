from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import uuid
import requests

from .models import HealthRecord, AIAnalysis
from .serializers import (
    HealthRecordSerializer, 
    AIAnalysisSerializer,
    PrescriptionAnalysisRequestSerializer,
    HealthRecordAnalysisRequestSerializer
)
from .ai_services import analyze_prescription_with_gemini, analyze_health_record_with_ai


def cors_response(data, status_code=200):
    """Helper function to add CORS headers to responses"""
    response = Response(data, status=status_code)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control, X-Requested-With, Accept, Origin'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Max-Age'] = '86400'
    return response


@api_view(['GET', 'HEAD', 'OPTIONS'])
def root_endpoint(request):
    """Root endpoint for API information"""
    
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status.HTTP_200_OK)
    
    # Handle HEAD request
    if request.method == 'HEAD':
        return cors_response({}, status.HTTP_200_OK)
    
    # Handle GET request
    return cors_response({
        'message': 'Jeeva AI Backend API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/ai/health/',
            'analyze_prescription': '/api/ai/analyze/prescription/',
            'analyze_health_record': '/api/ai/analyze/health-record/',
            'analyze_medical_report': '/api/ai/analyze/medical-report/',
        },
        'timestamp': timezone.now().isoformat()
    }, status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def analyze_prescription(request):
    """Analyze prescription image using AI"""
    try:
        serializer = PrescriptionAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return cors_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        # Get the uploaded image
        image = request.FILES.get('image')
        if not image:
            return cors_response(
                {'error': 'No image provided'}, 
                status.HTTP_400_BAD_REQUEST
            )
        
        # Read image bytes
        image_bytes = image.read()
        
        # Analyze prescription using Gemini AI
        analysis_result = analyze_prescription_with_gemini(image_bytes)
        
        # Create or get health record
        record_id = str(uuid.uuid4())
        health_record = HealthRecord.objects.create(
            id=record_id,
            patient_id=serializer.validated_data.get('patient_id', 'unknown'),
            record_type='prescription',
            title=serializer.validated_data.get('title', 'Prescription Analysis'),
            description=serializer.validated_data.get('description', ''),
            file_name=image.name,
            file_type=image.content_type,
            record_date=timezone.now(),
            uploaded_by=serializer.validated_data.get('uploaded_by', 'system')
        )
        
        # Create AI analysis - handle simplified_summary column gracefully
        try:
            # Try to create with simplified_summary column
            ai_analysis = AIAnalysis.objects.create(
                record_id=record_id,
                summary=analysis_result['summary'],
                simplified_summary=analysis_result.get('simplifiedSummary', ''),
                key_findings=analysis_result['keyFindings'],
                risk_warnings=analysis_result['riskWarnings'],
                recommendations=analysis_result['recommendations'],
                confidence=analysis_result['confidence'],
                analysis_type=analysis_result.get('analysisType', 'AI Analysis'),
                disclaimer=analysis_result.get('aiDisclaimer', ''),
                record_title=health_record.title
            )
        except Exception as e:
            # If simplified_summary column doesn't exist, create without it
            print(f"⚠️ simplified_summary column not available, creating without it: {str(e)}")
            ai_analysis = AIAnalysis.objects.create(
                record_id=record_id,
                summary=analysis_result['summary'],
                key_findings=analysis_result['keyFindings'],
                risk_warnings=analysis_result['riskWarnings'],
                recommendations=analysis_result['recommendations'],
                confidence=analysis_result['confidence'],
                analysis_type=analysis_result.get('analysisType', 'AI Analysis'),
                disclaimer=analysis_result.get('aiDisclaimer', ''),
                record_title=health_record.title
            )
        
        # Return the analysis result
        return cors_response({
            'success': True,
            'record_id': record_id,
            'analysis': AIAnalysisSerializer(ai_analysis).data,
            'health_record': HealthRecordSerializer(health_record).data
        }, status.HTTP_200_OK)
        
    except Exception as e:
        return cors_response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'OPTIONS'])
@parser_classes([JSONParser])
def analyze_health_record(request):
    """Analyze health record data using AI"""
    
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status.HTTP_200_OK)
    
    try:
        serializer = HealthRecordAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return cors_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        # Check if this is an imaging record (MRI/CT/X-ray)
        record_type = serializer.validated_data.get('record_type', '')
        file_url = serializer.validated_data.get('file_url', '')
        title = serializer.validated_data.get('title', '').lower()
        file_name = serializer.validated_data.get('file_name', '').lower()
        
        is_imaging_record = (
            record_type == 'imaging' or
            'mri' in title or 'ct' in title or 'xray' in title or 'x-ray' in title or
            'mri' in file_name or 'ct' in file_name or 'xray' in file_name or 'x-ray' in file_name
        )
        
        # Check if this is a prescription image upload
        if (file_url and 
            not serializer.validated_data.get('description') and 
            record_type == 'prescription'):
            # This is a prescription image upload, use prescription analysis
            try:
                # Download the image from the URL
                image_response = requests.get(file_url)
                image_response.raise_for_status()
                image_bytes = image_response.content
                
                # Analyze prescription using Gemini AI (original model)
                analysis_result = analyze_prescription_with_gemini(image_bytes)
            except Exception as e:
                return cors_response(
                    {'error': f'Failed to download or analyze image: {str(e)}'}, 
                    status.HTTP_400_BAD_REQUEST
                )
        elif (file_url and is_imaging_record):
            # This is an MRI/CT/X-ray scan, use Dr7.ai API
            try:
                from .ai_services import analyze_mri_ct_scan_with_dr7_new as analyze_mri_ct_scan_with_dr7
                
                # Download the image from the URL
                image_response = requests.get(file_url)
                image_response.raise_for_status()
                image_bytes = image_response.content
                
                # Determine scan type
                scan_type = 'MRI'  # default
                if 'ct' in title or 'ct' in file_name:
                    scan_type = 'CT'
                elif 'xray' in title or 'x-ray' in title or 'xray' in file_name or 'x-ray' in file_name:
                    scan_type = 'XRAY'
                elif 'mri' in title or 'mri' in file_name:
                    scan_type = 'MRI'
                
                print(f"🔍 Detected {scan_type} scan, routing to Dr7.ai API")
                
                # Analyze using Dr7.ai API
                dr7_result = analyze_mri_ct_scan_with_dr7(image_bytes, scan_type)
                
                # Convert Dr7.ai result to our standard format
                analysis_result = {
                    "summary": dr7_result['summary'],
                    "simplifiedSummary": dr7_result.get('simplifiedSummary', ''),
                    "recommendations": dr7_result['recommendations'],
                    "keyFindings": dr7_result['findings'],
                    "riskWarnings": [f"Risk Level: {dr7_result['risk_level'].title()}"],
                    "confidence": 0.85,
                    "analysisType": f"AI {scan_type} Analysis",
                    "aiDisclaimer": (
                        "**Disclaimer:** This MRI/CT Scan analysis is automatically generated by an AI model "
                        "and is provided **for informational purposes only**. It does **not substitute for clinical "
                        "judgment or diagnostic evaluation**. Always consult a qualified radiologist or medical "
                        "professional for interpretation and treatment decisions."
                    )
                }
                
            except Exception as e:
                print(f"❌ Dr7.ai analysis failed: {str(e)}")
                # The Dr7.ai service now provides a fallback response, so this shouldn't happen
                # But if it does, provide a generic error message
                return cors_response({
                    'error': f'MRI/CT scan analysis is currently unavailable. Please try again later or contact support.'
                }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # This is text input or other record type, use text analysis
            analysis_result = analyze_health_record_with_ai(serializer.validated_data)
        
        # Use the record ID from the frontend if provided, otherwise create a new one
        record_id = serializer.validated_data.get('record_id', str(uuid.uuid4()))
        
        # Convert service_date string to datetime object
        service_date_str = serializer.validated_data['service_date']
        try:
            # Try parsing ISO format first
            record_date = datetime.fromisoformat(service_date_str.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time if parsing fails
            record_date = timezone.now()
        
        health_record = HealthRecord.objects.create(
            id=record_id,
            patient_id=serializer.validated_data.get('patient_id', 'unknown'),
            record_type=serializer.validated_data['record_type'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            file_url=serializer.validated_data.get('file_url'),
            file_name=serializer.validated_data.get('file_name'),
            file_type=serializer.validated_data.get('file_name', '').split('.')[-1] if serializer.validated_data.get('file_name') else None,
            record_date=record_date,
            uploaded_by=serializer.validated_data.get('uploaded_by', 'system')
        )
        
        # Create AI analysis - handle simplified_summary column gracefully
        try:
            # Try to create with simplified_summary column
            ai_analysis = AIAnalysis.objects.create(
                record_id=record_id,
                summary=analysis_result['summary'],
                simplified_summary=analysis_result.get('simplifiedSummary', ''),
                key_findings=analysis_result['keyFindings'],
                risk_warnings=analysis_result['riskWarnings'],
                recommendations=analysis_result['recommendations'],
                confidence=analysis_result['confidence'],
                analysis_type=analysis_result.get('analysisType', 'AI Analysis'),
                disclaimer=analysis_result.get('aiDisclaimer', ''),
                record_title=health_record.title
            )
        except Exception as e:
            # If simplified_summary column doesn't exist, create without it
            print(f"⚠️ simplified_summary column not available, creating without it: {str(e)}")
            ai_analysis = AIAnalysis.objects.create(
                record_id=record_id,
                summary=analysis_result['summary'],
                key_findings=analysis_result['keyFindings'],
                risk_warnings=analysis_result['riskWarnings'],
                recommendations=analysis_result['recommendations'],
                confidence=analysis_result['confidence'],
                analysis_type=analysis_result.get('analysisType', 'AI Analysis'),
                disclaimer=analysis_result.get('aiDisclaimer', ''),
                record_title=health_record.title
            )
        
        # Return the analysis result
        return cors_response({
            'success': True,
            'record_id': record_id,
            'analysis': AIAnalysisSerializer(ai_analysis).data,
            'health_record': HealthRecordSerializer(health_record).data
        }, status.HTTP_200_OK)
        
    except Exception as e:
        return cors_response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_analysis(request, record_id):
    """Get AI analysis for a specific record"""
    try:
        # Get the latest analysis for the record
        analysis = AIAnalysis.objects.filter(record_id=record_id).order_by('-processed_at').first()
        
        if not analysis:
            return cors_response(
                {'error': 'No analysis found for this record'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the health record
        try:
            health_record = HealthRecord.objects.get(id=record_id)
            health_record_data = HealthRecordSerializer(health_record).data
        except HealthRecord.DoesNotExist:
            health_record_data = None
        
        return cors_response({
            'success': True,
            'analysis': AIAnalysisSerializer(analysis).data,
            'health_record': health_record_data
        }, status.HTTP_200_OK)
        
    except Exception as e:
        return cors_response(
            {'error': f'Failed to retrieve analysis: {str(e)}'}, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_analyses(request):
    """List all AI analyses"""
    try:
        analyses = AIAnalysis.objects.all().order_by('-processed_at')
        serializer = AIAnalysisSerializer(analyses, many=True)
        
        return cors_response({
            'success': True,
            'analyses': serializer.data
        }, status.HTTP_200_OK)
        
    except Exception as e:
        return cors_response(
            {'error': f'Failed to retrieve analyses: {str(e)}'}, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return cors_response({
        'status': 'healthy',
        'message': 'Jeeva AI Backend is running',
        'timestamp': timezone.now().isoformat()
    }, status.HTTP_200_OK)


# =============================================================================
# MRI/CT SCAN ANALYSIS VIEWS
# =============================================================================

@api_view(['POST'])
def analyze_mri_ct_scan(request):
    """
    Analyze MRI/CT scan using Dr7.ai API
    
    Expected payload:
    {
        "record_id": "uuid",
        "patient_id": "uuid", 
        "scan_type": "MRI|CT|XRAY",
        "image_url": "https://...",
        "doctor_access": false
    }
    """
    try:
        from .serializers import MRI_CT_AnalysisRequestSerializer
        from .models import MRI_CT_Analysis
        from .ai_services import analyze_mri_ct_scan_with_dr7_new as analyze_mri_ct_scan_with_dr7, get_mri_ct_analysis_for_record
        import requests
        
        # Validate request data
        serializer = MRI_CT_AnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return cors_response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        record_id = data['record_id']
        patient_id = data['patient_id']
        scan_type = data['scan_type']
        doctor_access = data.get('doctor_access', False)
        
        # Check if analysis already exists
        existing_analysis = get_mri_ct_analysis_for_record(record_id)
        if existing_analysis:
            return cors_response({
                'message': 'Analysis already exists for this record',
                'analysis': existing_analysis
            }, status.HTTP_200_OK)
        
        # Get image data
        image_bytes = None
        if data.get('image_url'):
            # Download image from URL
            try:
                response = requests.get(data['image_url'], timeout=30)
                response.raise_for_status()
                image_bytes = response.content
            except Exception as e:
                return cors_response({
                    'error': f'Failed to download image: {str(e)}'
                }, status.HTTP_400_BAD_REQUEST)
        elif 'image_file' in request.FILES:
            # Get image from uploaded file
            image_file = request.FILES['image_file']
            image_bytes = image_file.read()
        else:
            return cors_response({
                'error': 'Either image_url or image_file must be provided'
            }, status.HTTP_400_BAD_REQUEST)
        
        # Analyze the scan using Dr7.ai
        print(f"🔍 Starting {scan_type} analysis for record {record_id}")
        analysis_result = analyze_mri_ct_scan_with_dr7(image_bytes, scan_type)
        
        # Save analysis to database
        mri_ct_analysis = MRI_CT_Analysis.objects.create(
            record_id=record_id,
            patient_id=patient_id,
            scan_type=scan_type,
            summary=analysis_result['summary'],
            findings=analysis_result['findings'],
            region=analysis_result['region'],
            clinical_significance=analysis_result['clinical_significance'],
            recommendations=analysis_result['recommendations'],
            risk_level=analysis_result['risk_level'],
            source_model=analysis_result['source_model'],
            doctor_access=doctor_access,
            api_usage_tokens=analysis_result.get('api_usage_tokens', 0)
        )
        
        # Serialize the response
        from .serializers import MRI_CT_AnalysisSerializer
        response_serializer = MRI_CT_AnalysisSerializer(mri_ct_analysis)
        
        print(f"✅ {scan_type} analysis completed and saved for record {record_id}")
        
        return cors_response({
            'message': f'{scan_type} scan analysis completed successfully',
            'analysis': response_serializer.data
        }, status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ Error in MRI/CT analysis: {str(e)}")
        return cors_response({
            'error': f'Analysis failed: {str(e)}'
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_mri_ct_analysis(request, record_id):
    """
    Get MRI/CT analysis for a specific record
    
    URL: /api/ai/mri-ct-analysis/{record_id}/
    """
    try:
        from .ai_services import get_mri_ct_analysis_for_record
        
        analysis = get_mri_ct_analysis_for_record(record_id)
        
        if not analysis:
            return cors_response({
                'error': 'Analysis not found for this record'
            }, status.HTTP_404_NOT_FOUND)
        
        return cors_response({
            'analysis': analysis
        }, status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Error retrieving MRI/CT analysis: {str(e)}")
        return cors_response({
            'error': f'Failed to retrieve analysis: {str(e)}'
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_mri_ct_analyses(request):
    """
    List MRI/CT analyses for a patient
    
    Query params:
    - patient_id: Patient ID to filter analyses
    - scan_type: Optional filter by scan type (MRI, CT, XRAY)
    """
    try:
        from .models import MRI_CT_Analysis
        from .serializers import MRI_CT_AnalysisSerializer
        
        patient_id = request.GET.get('patient_id')
        scan_type = request.GET.get('scan_type')
        
        if not patient_id:
            return cors_response({
                'error': 'patient_id parameter is required'
            }, status.HTTP_400_BAD_REQUEST)
        
        # Build query
        queryset = MRI_CT_Analysis.objects.filter(patient_id=patient_id)
        
        if scan_type:
            queryset = queryset.filter(scan_type=scan_type)
        
        # Serialize results
        serializer = MRI_CT_AnalysisSerializer(queryset, many=True)
        
        return cors_response({
            'analyses': serializer.data,
            'count': len(serializer.data)
        }, status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Error listing MRI/CT analyses: {str(e)}")
        return cors_response({
            'error': f'Failed to list analyses: {str(e)}'
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_doctor_access(request, record_id):
    """
    Update doctor access permission for MRI/CT analysis
    
    Payload:
    {
        "doctor_access": true/false
    }
    """
    try:
        from .models import MRI_CT_Analysis
        
        doctor_access = request.data.get('doctor_access')
        if doctor_access is None:
            return cors_response({
                'error': 'doctor_access field is required'
            }, status.HTTP_400_BAD_REQUEST)
        
        try:
            analysis = MRI_CT_Analysis.objects.get(record_id=record_id)
            analysis.doctor_access = doctor_access
            analysis.save()
            
            from .serializers import MRI_CT_AnalysisSerializer
            serializer = MRI_CT_AnalysisSerializer(analysis)
            
            return cors_response({
                'message': 'Doctor access updated successfully',
                'analysis': serializer.data
            }, status.HTTP_200_OK)
            
        except MRI_CT_Analysis.DoesNotExist:
            return cors_response({
                'error': 'Analysis not found for this record'
            }, status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        print(f"❌ Error updating doctor access: {str(e)}")
        return cors_response({
            'error': f'Failed to update doctor access: {str(e)}'
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)