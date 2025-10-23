from django.db import models
from django.utils import timezone


class HealthRecord(models.Model):
    """Model to store health record information"""
    RECORD_TYPES = [
        ('lab_test', 'Lab Test'),
        ('prescription', 'Prescription'),
        ('imaging', 'Imaging'),
        ('consultation', 'Consultation'),
        ('vaccination', 'Vaccination'),
        ('other', 'Other'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    patient_id = models.CharField(max_length=255)
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    record_date = models.DateTimeField()
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'health_records'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.record_type})"


class AIAnalysis(models.Model):
    """Model to store AI analysis results"""
    id = models.AutoField(primary_key=True)
    record_id = models.CharField(max_length=255)
    summary = models.TextField()
    key_findings = models.JSONField(default=list)
    risk_warnings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    confidence = models.FloatField(default=0.0)
    analysis_type = models.CharField(max_length=100, default='AI Analysis')
    processed_at = models.DateTimeField(default=timezone.now)
    record_title = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'ai_insights'
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"AI Analysis for {self.record_title}"