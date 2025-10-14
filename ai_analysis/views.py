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
    HealthRecordAnalysisRequestSerializer,
    MedicineAnalysisRequestSerializer
)
from .ai_services import analyze_prescription_with_gemini, analyze_health_record_with_ai, generate_predictive_insights_from_medicines


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
            predictive_insights=analysis_result.get('predictiveInsights', []),
            detailed_report=analysis_result.get('detailedReport', ''),
            medicine_names=analysis_result.get('medicineNames', []),
            disclaimer=analysis_result.get('disclaimer', ''),
            ai_disclaimer=analysis_result.get('aiDisclaimer', ''),
            confidence=analysis_result['confidence'],
            analysis_type=analysis_result['analysisType'],
            record_title=health_record.title
        )
        
        # Return the analysis result
        analysis_data = AIAnalysisSerializer(ai_analysis).data
        analysis_data['ai_disclaimer'] = analysis_result.get('aiDisclaimer', '')
        
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': HealthRecordSerializer(health_record).data,
            'ai_disclaimer': analysis_result.get('aiDisclaimer', '⚠️ **AI Analysis Disclaimer**: This analysis is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider for personalized medical guidance.')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([JSONParser])
def analyze_health_record(request):
    """Analyze health record data using AI"""
    try:
        serializer = HealthRecordAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
                return Response(
                    {'error': f'Failed to download or analyze image: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
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
            predictive_insights=analysis_result.get('predictiveInsights', []),
            detailed_report=analysis_result.get('detailedReport', ''),
            medicine_names=analysis_result.get('medicineNames', []),
            confidence=analysis_result['confidence'],
            analysis_type=analysis_result['analysisType'],
            record_title=health_record.title
        )
        
        # Return the analysis result
        analysis_data = AIAnalysisSerializer(ai_analysis).data
        analysis_data['ai_disclaimer'] = analysis_result.get('aiDisclaimer', '')
        
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': analysis_data,
            'health_record': HealthRecordSerializer(health_record).data,
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
        analyses = AIAnalysis.objects.all().order_by('-processed_at')
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
        
        # Create health record
        health_record = HealthRecord.objects.create(
            id=record_id,
            patient_id=serializer.validated_data.get('patient_id', 'unknown'),
            record_type='prescription',
            title=serializer.validated_data.get('title', 'Medicine Analysis'),
            description=serializer.validated_data.get('description', f"Analysis of medicines: {', '.join(medicine_names)}"),
            record_date=timezone.now(),
            uploaded_by=serializer.validated_data.get('uploaded_by', 'system')
        )
        
        # Create AI analysis with new fields
        ai_analysis = AIAnalysis.objects.create(
            record_id=record_id,
            summary=analysis_result['summary'],
            key_findings=analysis_result['keyFindings'],
            risk_warnings=analysis_result['riskWarnings'],
            recommendations=analysis_result['recommendations'],
            predictive_insights=analysis_result.get('predictiveInsights', []),
            detailed_report=analysis_result.get('detailedReport', ''),
            medicine_names=analysis_result.get('medicineNames', medicine_names),
            confidence=analysis_result['confidence'],
            analysis_type=analysis_result['analysisType'],
            record_title=health_record.title
        )
        
        # Return the analysis result
        return Response({
            'success': True,
            'record_id': record_id,
            'analysis': AIAnalysisSerializer(ai_analysis).data,
            'health_record': HealthRecordSerializer(health_record).data,
            'medicine_names': medicine_names
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Medicine analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Jeeva AI Backend is running',
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)

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