from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime
import uuid
import requests
import json

from .models import HealthRecord, AIAnalysis
from .serializers import (
    HealthRecordSerializer, 
    AIAnalysisSerializer,
    PrescriptionAnalysisRequestSerializer,
    HealthRecordAnalysisRequestSerializer,
    MedicineAnalysisRequestSerializer
)
from .ai_services import analyze_prescription_with_gemini, analyze_health_record_with_ai, generate_predictive_insights_from_medicines, analyze_medical_report_with_scanner, analyze_image_with_gemini_vision_fast, analyze_image_instant

# Custom response function with CORS headers
def cors_response(data, status_code=200):
    response = Response(data, status=status_code)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@api_view(['GET', 'HEAD'])
def root_endpoint(request):
    """Root endpoint for the API - supports both GET and HEAD methods"""
    if request.method == 'HEAD':
        # For HEAD requests, return empty response with just headers
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # For GET requests, return full API information
    return cors_response({
        'message': 'Jeeva AI Backend API is running!',
        'status': 'healthy',
        'version': '1.0.0',
        'endpoints': {
            'health_check': '/api/ai/health/',
            'analyze_health_record': '/api/ai/analyze/health-record/',
            'analyze_prescription': '/api/ai/analyze/prescription/',
            'list_analyses': '/api/ai/analyses/'
        }
    })


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def analyze_prescription(request):
    """Analyze prescription image using AI"""
    try:
        serializer = PrescriptionAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the uploaded image
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read image bytes
        image_bytes = image.read()
        
        # Analyze prescription using Gemini AI
        analysis_result = analyze_prescription_with_gemini(image_bytes)
        
        # Create or get health record
        record_id = str(uuid.uuid4())
        
        # Create AI analysis data (database-free)
        analysis_data = {
            'id': str(uuid.uuid4()),
            'user_id': serializer.validated_data.get('patient_id', 'unknown'),
            'record_id': record_id,
            'summary': analysis_result['summary'],
            'key_findings': analysis_result['keyFindings'],
            'risk_warnings': analysis_result['riskWarnings'],
            'recommendations': analysis_result['recommendations'],
            'confidence_score': int(analysis_result['confidence'] * 100),
            'created_at': timezone.now().isoformat()
        }
        analysis_data['ai_disclaimer'] = analysis_result.get('aiDisclaimer', '')
        
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': health_record_data,
            'ai_disclaimer': analysis_result.get('aiDisclaimer', '⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance.')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Health record analysis failed with error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return Response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([JSONParser])
def analyze_health_record(request):
    """Analyze health record data using AI - DATABASE-FREE VERSION"""
    try:
        print(f"🔍 Received request data: {request.data}")
        print(f"🔍 Request content type: {request.content_type}")
        
        serializer = HealthRecordAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"❌ Serializer validation failed: {serializer.errors}")
            return cors_response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        
        # Check if this is an image upload (has file_url)
        if serializer.validated_data.get('file_url') and not serializer.validated_data.get('description'):
            # This is an image upload, use medical report analysis
            try:
                # Download the image from the URL
                image_response = requests.get(serializer.validated_data['file_url'])
                image_response.raise_for_status()
                image_bytes = image_response.content
                
                # Create a file-like object for the medical report scanner
                from io import BytesIO
                file_obj = BytesIO(image_bytes)
                file_obj.name = serializer.validated_data.get('file_name', 'medical_report.jpg')
                
                # Use INSTANT analysis for production to avoid worker timeouts
                print(f"⚡ Using INSTANT analysis for production deployment: {file_obj.name}")
                analysis_result = analyze_image_instant(file_obj, file_obj.name)
            except Exception as e:
                return Response(
                    {'error': f'Failed to download or analyze image: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # This is text input, use text analysis
            analysis_result = analyze_health_record_with_ai(serializer.validated_data)
        
        # DATABASE-FREE SOLUTION: Skip database operations entirely
        print(f"⚡ Using DATABASE-FREE analysis for instant results")
        
        # Use the record ID from the frontend if provided, otherwise create a new one
        record_id = serializer.validated_data.get('record_id', str(uuid.uuid4()))
        
        # Create health record data without database storage
        health_record_data = {
            'id': record_id,
            'user_id': serializer.validated_data.get('patient_id', 'unknown'),
            'record_type': serializer.validated_data['record_type'],
            'title': serializer.validated_data['title'],
            'description': serializer.validated_data.get('description', ''),
            'file_url': serializer.validated_data.get('file_url'),
            'file_name': serializer.validated_data.get('file_name'),
            'service_date': serializer.validated_data['service_date'],
            'created_at': timezone.now().isoformat()
        }
        
        # Create AI analysis data (database-free)
        analysis_data = {
            'id': str(uuid.uuid4()),
            'user_id': serializer.validated_data.get('patient_id', 'unknown'),
            'record_id': record_id,
            'summary': analysis_result['summary'],
            'key_findings': analysis_result['keyFindings'],
            'risk_warnings': analysis_result['riskWarnings'],
            'recommendations': analysis_result['recommendations'],
            'confidence_score': int(analysis_result['confidence'] * 100),
            'created_at': timezone.now().isoformat()
        }
        analysis_data['ai_disclaimer'] = analysis_result.get('aiDisclaimer', '')
        
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': health_record_data,
            'ai_disclaimer': analysis_result.get('aiDisclaimer', '⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance.')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_analysis(request, record_id):
    """Get AI analysis for a specific record"""
    try:
        # Get the latest analysis for the record
        analysis = AIAnalysis.objects.filter(record_id=record_id).order_by('-processed_at').first()
        
        if not analysis:
            return Response(
                {'error': 'No analysis found for this record'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the health record
        try:
            health_record = HealthRecord.objects.get(id=record_id)
            health_record_data = HealthRecordSerializer(health_record).data
        except HealthRecord.DoesNotExist:
            health_record_data = None
        
        return Response({
            'success': True,
            'analysis': AIAnalysisSerializer(analysis).data,
            'health_record': health_record_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve analysis: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_analyses(request):
    """List all AI analyses"""
    try:
        analyses = AIAnalysis.objects.all().order_by('-created_at')
        serializer = AIAnalysisSerializer(analyses, many=True)
        
        return Response({
            'success': True,
            'analyses': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve analyses: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([JSONParser])
def analyze_medicines(request):
    """Analyze medicines and generate predictive insights using Gemini AI"""
    try:
        serializer = MedicineAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get medicine names from request
        medicine_names = serializer.validated_data['medicine_names']
        
        if not medicine_names:
            return Response(
                {'error': 'No medicine names provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate predictive insights using Gemini AI
        analysis_result = generate_predictive_insights_from_medicines(medicine_names)
        
        # Use the record ID from the frontend if provided, otherwise create a new one
        record_id = serializer.validated_data.get('record_id', str(uuid.uuid4()))
        
        # Create health record data (database-free)
        health_record_data = {
            'id': record_id,
            'user_id': serializer.validated_data.get('patient_id', 'unknown'),
            'record_type': 'prescription',
            'title': serializer.validated_data.get('title', 'Medicine Analysis'),
            'description': serializer.validated_data.get('description', f"Analysis of medicines: {', '.join(medicine_names)}"),
            'service_date': timezone.now().date().isoformat(),
            'created_at': timezone.now().isoformat()
        }
        
        # Create AI analysis data (database-free)
        analysis_data = {
            'id': str(uuid.uuid4()),
            'user_id': serializer.validated_data.get('patient_id', 'unknown'),
            'record_id': record_id,
            'summary': analysis_result['summary'],
            'key_findings': analysis_result['keyFindings'],
            'risk_warnings': analysis_result['riskWarnings'],
            'recommendations': analysis_result['recommendations'],
            'confidence_score': int(analysis_result['confidence'] * 100),
            'created_at': timezone.now().isoformat()
        }
        
        # Return the analysis result
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': health_record_data,
            'medicine_names': medicine_names
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Medicine analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'HEAD'])
def health_check(request):
    """Health check endpoint - supports both GET and HEAD methods"""
    if request.method == 'HEAD':
        # For HEAD requests, return empty response with just headers
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # For GET requests, return full health information
    return cors_response({
        'status': 'healthy',
        'message': 'Jeeva AI Backend is running',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def analyze_medical_report(request):
    """Analyze medical report (PDF or image) using the MedicalReportScanner"""
    try:
        # Get the uploaded file
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get other parameters
        title = request.data.get('title', 'Medical Report Analysis')
        description = request.data.get('description', '')
        patient_id = request.data.get('patient_id', 'unknown')
        uploaded_by = request.data.get('uploaded_by', 'system')
        
        # Debug: Log file information
        print(f"🔍 DEBUG: File name: {uploaded_file.name}")
        print(f"🔍 DEBUG: File size: {uploaded_file.size}")
        print(f"🔍 DEBUG: File content type: {uploaded_file.content_type}")
        
        # Analyze medical report using the scanner
        analysis_result = analyze_medical_report_with_scanner(uploaded_file, uploaded_file.name)
        
        # Create or get health record
        record_id = str(uuid.uuid4())
        
        # Create health record data (database-free)
        health_record_data = {
            'id': record_id,
            'user_id': patient_id,
            'record_type': 'lab_test',
            'title': title,
            'description': description,
            'file_name': uploaded_file.name,
            'service_date': timezone.now().date().isoformat(),
            'created_at': timezone.now().isoformat()
        }
        
        # Create AI analysis data (database-free)
        analysis_data = {
            'id': str(uuid.uuid4()),
            'user_id': patient_id,
            'record_id': record_id,
            'summary': analysis_result['summary'],
            'key_findings': analysis_result['keyFindings'],
            'risk_warnings': analysis_result['riskWarnings'],
            'recommendations': analysis_result['recommendations'],
            'confidence_score': int(analysis_result['confidence'] * 100),
            'created_at': timezone.now().isoformat()
        }
        analysis_data['ai_disclaimer'] = analysis_result.get('aiDisclaimer', '')
        
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': health_record_data,
            'ai_disclaimer': analysis_result.get('aiDisclaimer', '⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance.')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Medical report analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def test_response_structure(request):
    """Test endpoint to check response structure"""
    mock_analysis = {
        "summary": "**Paracetamol** - Comprehensive medical analysis completed. This medicine requires careful monitoring and adherence to prescribed dosage.",
        "keyFindings": [
            "**Medicine Analysis**: Paracetamol - Detailed medical evaluation completed",
            "**Safety Assessment**: Risk factors and contraindications identified with probability estimates"
        ],
        "riskWarnings": [
            "⚠️ **Paracetamol** - Requires careful monitoring and adherence to prescribed dosage",
            "⚠️ **Drug Interactions** - Potential interactions may occur, consult healthcare provider before taking other medications"
        ],
        "recommendations": [
            "💡 **Blood Tests** - Schedule comprehensive blood panel including liver function, kidney function, and complete blood count",
            "💡 **Vital Signs** - Monitor blood pressure, heart rate, and temperature regularly"
        ],
        "predictiveInsights": [
            "**Paracetamol** - High probability (85-90%) of therapeutic effectiveness with proper adherence",
            "**Side Effect Risk** - Moderate risk (15-25%) of gastrointestinal disturbances, monitor closely"
        ],
        "ai_disclaimer": "⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice.",
        "disclaimer": "This AI-generated analysis is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment.",
        "medicineNames": ["Paracetamol"],
        "confidence": 0.85,
        "analysisType": "Predictive Medicine Analysis"
    }
    
    return Response({
        'success': True,
        'record_id': 'test-123',
        'analysis': mock_analysis,
        'ai_disclaimer': "⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance."
    })


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_prescription_file(request):
    """Upload prescription file (image or PDF)"""
    try:
        # Get the uploaded file
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only JPEG, PNG, and PDF files are allowed.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get form data
        patient_id = request.data.get('patient_id')
        doctor_id = request.data.get('doctor_id')
        consultation_id = request.data.get('consultation_id')
        description = request.data.get('description', '')
        
        if not patient_id or not doctor_id:
            return Response(
                {'error': 'patient_id and doctor_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine file type
        file_type = 'pdf' if file.content_type == 'application/pdf' else 'image'
        
        # Create prescription file record
        from .models import PrescriptionFile
        prescription_file = PrescriptionFile.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            consultation_id=consultation_id,
            file_name=file.name,
            file_type=file_type,
            file_url=f'/media/prescriptions/{file.name}',  # This would be updated with actual storage URL
            file_size=file.size,
            description=description
        )
        
        # Here you would typically save the file to your storage system
        # For now, we'll just return the created record
        
        return Response({
            'success': True,
            'file_id': str(prescription_file.id),
            'file_name': prescription_file.file_name,
            'file_type': prescription_file.file_type,
            'file_size': prescription_file.file_size,
            'created_at': prescription_file.created_at
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_consultation_note_file(request):
    """Upload consultation note file (image or PDF)"""
    try:
        # Get the uploaded file
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only JPEG, PNG, and PDF files are allowed.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get form data
        patient_id = request.data.get('patient_id')
        doctor_id = request.data.get('doctor_id')
        consultation_id = request.data.get('consultation_id')
        description = request.data.get('description', '')
        
        if not patient_id or not doctor_id:
            return Response(
                {'error': 'patient_id and doctor_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine file type
        file_type = 'pdf' if file.content_type == 'application/pdf' else 'image'
        
        # Create consultation note file record
        from .models import ConsultationNoteFile
        consultation_file = ConsultationNoteFile.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            consultation_id=consultation_id,
            file_name=file.name,
            file_type=file_type,
            file_url=f'/media/consultation-notes/{file.name}',  # This would be updated with actual storage URL
            file_size=file.size,
            description=description
        )
        
        # Here you would typically save the file to your storage system
        # For now, we'll just return the created record
        
        return Response({
            'success': True,
            'file_id': str(consultation_file.id),
            'file_name': consultation_file.file_name,
            'file_type': consultation_file.file_type,
            'file_size': consultation_file.file_size,
            'created_at': consultation_file.created_at
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_prescription_files(request, patient_id):
    """Get all prescription files for a patient"""
    try:
        from .models import PrescriptionFile
        
        files = PrescriptionFile.objects.filter(patient_id=patient_id).order_by('-created_at')
        
        file_data = []
        for file in files:
            file_data.append({
                'id': str(file.id),
                'file_name': file.file_name,
                'file_type': file.file_type,
                'file_url': file.file_url,
                'file_size': file.file_size,
                'description': file.description,
                'doctor_id': str(file.doctor_id),
                'consultation_id': str(file.consultation_id) if file.consultation_id else None,
                'created_at': file.created_at
            })
        
        return Response({
            'success': True,
            'files': file_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get prescription files: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_consultation_note_files(request, patient_id):
    """Get all consultation note files for a patient"""
    try:
        from .models import ConsultationNoteFile
        
        files = ConsultationNoteFile.objects.filter(patient_id=patient_id).order_by('-created_at')
        
        file_data = []
        for file in files:
            file_data.append({
                'id': str(file.id),
                'file_name': file.file_name,
                'file_type': file.file_type,
                'file_url': file.file_url,
                'file_size': file.file_size,
                'description': file.description,
                'doctor_id': str(file.doctor_id),
                'consultation_id': str(file.consultation_id) if file.consultation_id else None,
                'created_at': file.created_at
            })
        
        return Response({
            'success': True,
            'files': file_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get consultation note files: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )