from rest_framework import serializers
import json
from .models import HealthRecord, AIAnalysis


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = '__all__'


class AIAnalysisSerializer(serializers.ModelSerializer):
    key_findings = serializers.SerializerMethodField()
    risk_warnings = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'
    
    def get_key_findings(self, obj):
        try:
            return json.loads(obj.key_findings) if obj.key_findings else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_risk_warnings(self, obj):
        try:
            return json.loads(obj.risk_warnings) if obj.risk_warnings else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_recommendations(self, obj):
        try:
            return json.loads(obj.recommendations) if obj.recommendations else []
        except (json.JSONDecodeError, TypeError):
            return []


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


class MedicineAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for medicine-based predictive analysis requests"""
    medicine_names = serializers.ListField(
        child=serializers.CharField(max_length=255),
        help_text="List of medicine names to analyze"
    )
    patient_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    title = serializers.CharField(max_length=255, required=False, default="Medicine Analysis")
    description = serializers.CharField(required=False, default="", allow_blank=True)
    uploaded_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    record_id = serializers.CharField(max_length=255, required=False, allow_blank=True)