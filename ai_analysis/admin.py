from django.contrib import admin
from .models import (
    Profile, HealthRecord, AIAnalysis, AIInsight, Consultation, 
    Notification, ConsentRequest, Consent, AccessLog, Event, 
    Schedule, Prescription, ConsultationNote, PatientAccess,
    PrescriptionFile, ConsultationNoteFile
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'record_type', 'user_id', 'created_at']
    list_filter = ['record_type', 'created_at']
    search_fields = ['title', 'description', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'record_id', 'confidence_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['summary', 'user_id']
    readonly_fields = ['id', 'created_at']


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['id', 'insight_type', 'user_id', 'confidence_score', 'created_at']
    list_filter = ['insight_type', 'created_at']
    search_fields = ['insight_type', 'content', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'consultation_date', 'status']
    list_filter = ['status', 'consultation_date', 'created_at']
    search_fields = ['reason', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'user_id', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['title', 'message', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsentRequest)
class ConsentRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'status', 'requested_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['purpose', 'message']
    readonly_fields = ['id', 'requested_at', 'created_at', 'updated_at']


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'status', 'scope', 'created_at']
    list_filter = ['status', 'scope', 'created_at']
    search_fields = ['patient_id', 'doctor_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor_id', 'patient_id', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['action', 'reason']
    readonly_fields = ['id', 'created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'user_id']
    readonly_fields = ['id', 'created_at']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor_id', 'schedule_date', 'start_time', 'status']
    list_filter = ['status', 'schedule_date', 'created_at']
    search_fields = ['notes']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'medication_name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['medication_name', 'instructions']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'consultation_id', 'doctor_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['notes']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PatientAccess)
class PatientAccessAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'access_level', 'status', 'created_at']
    list_filter = ['access_level', 'status', 'created_at']
    search_fields = ['patient_id', 'doctor_id']
    readonly_fields = ['id', 'granted_at', 'created_at', 'updated_at']


@admin.register(PrescriptionFile)
class PrescriptionFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type', 'patient_id', 'doctor_id', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'patient_id', 'doctor_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsultationNoteFile)
class ConsultationNoteFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type', 'patient_id', 'doctor_id', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'patient_id', 'doctor_id']
    readonly_fields = ['id', 'created_at', 'updated_at']