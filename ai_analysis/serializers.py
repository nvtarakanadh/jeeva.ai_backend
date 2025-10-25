from rest_framework import serializers
from .models import HealthRecord, AIAnalysis


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = '__all__'


class AIAnalysisSerializer(serializers.ModelSerializer):
    ai_disclaimer = serializers.CharField(source='disclaimer', read_only=True)
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'


class PrescriptionAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for prescription analysis requests"""
    image = serializers.ImageField()
    title = serializers.CharField(max_length=255, required=False, default="Prescription Analysis")
    description = serializers.CharField(required=False, default="")
    record_type = serializers.CharField(default="prescription")
    patient_id = serializers.CharField(max_length=255, required=False)
    uploaded_by = serializers.CharField(max_length=255, required=False)


class HealthRecordAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for health record analysis requests"""
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    record_type = serializers.CharField()
    service_date = serializers.CharField()  # Changed from DateTimeField to CharField
    file_url = serializers.URLField(required=False, allow_blank=True)
    file_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    patient_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    uploaded_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    record_id = serializers.CharField(max_length=255, required=False, allow_blank=True)  # Add record_id field
