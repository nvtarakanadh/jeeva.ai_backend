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
        
        # Create AI analysis
        ai_analysis = AIAnalysis.objects.create(
            record_id=record_id,
            summary=analysis_result['summary'],
            key_findings=analysis_result['keyFindings'],
            risk_warnings=analysis_result['riskWarnings'],
            recommendations=analysis_result['recommendations'],
            confidence=analysis_result['confidence'],
            analysis_type=analysis_result['analysisType'],
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
        
        # Check if this is an image upload (has file_url)
        if serializer.validated_data.get('file_url') and not serializer.validated_data.get('description'):
            # This is an image upload, use image analysis
            try:
                # Download the image from the URL
                image_response = requests.get(serializer.validated_data['file_url'])
                image_response.raise_for_status()
                image_bytes = image_response.content
                
                # Analyze prescription using Gemini AI (original model)
                analysis_result = analyze_prescription_with_gemini(image_bytes)
            except Exception as e:
                return cors_response(
                    {'error': f'Failed to download or analyze image: {str(e)}'}, 
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            # This is text input, use text analysis
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
        
        # Create AI analysis
        ai_analysis = AIAnalysis.objects.create(
            record_id=record_id,
            summary=analysis_result['summary'],
            key_findings=analysis_result['keyFindings'],
            risk_warnings=analysis_result['riskWarnings'],
            recommendations=analysis_result['recommendations'],
            confidence=analysis_result['confidence'],
            analysis_type=analysis_result['analysisType'],
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