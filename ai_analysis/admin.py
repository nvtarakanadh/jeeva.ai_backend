from django.contrib import admin
from .models import HealthRecord, AIAnalysis


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'record_type', 'patient_id', 'uploaded_at']
    list_filter = ['record_type', 'uploaded_at']
    search_fields = ['title', 'description', 'patient_id']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'record_title', 'analysis_type', 'confidence', 'processed_at']
    list_filter = ['analysis_type', 'processed_at']
    search_fields = ['record_title', 'summary']
    readonly_fields = ['id', 'processed_at']