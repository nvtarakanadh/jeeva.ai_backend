from django.db import models
from django.utils import timezone
import uuid




class Profile(models.Model):
    """User profiles with roles (patient/doctor)"""
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    full_name = models.TextField()
    email = models.TextField()
    phone = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    blood_group = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    emergency_contact_name = models.TextField(blank=True, null=True)
    emergency_contact_phone = models.TextField(blank=True, null=True)
    emergency_contact_relationship = models.TextField(blank=True, null=True)
    role = models.TextField(choices=ROLE_CHOICES, default='patient')
    specialization = models.TextField(blank=True, null=True)
    license_number = models.TextField(blank=True, null=True)
    hospital_affiliation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.role})"


class HealthRecord(models.Model):
    """Health records and medical documents"""
    RECORD_TYPES = [
        ('lab_test', 'Lab Test'),
        ('prescription', 'Prescription'),
        ('imaging', 'Imaging'),
        ('consultation', 'Consultation'),
        ('vaccination', 'Vaccination'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4)
    title = models.TextField()
    record_type = models.TextField(choices=RECORD_TYPES)
    description = models.TextField(blank=True, null=True)
    file_url = models.TextField(blank=True, null=True)
    file_name = models.TextField(blank=True, null=True)
    service_date = models.DateField(default=timezone.now)
    provider_name = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'health_records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.record_type})"


class AIAnalysis(models.Model):
    """AI analysis results for health records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4)
    record_id = models.UUIDField(default=uuid.uuid4)
    summary = models.TextField()
    key_findings = models.TextField(default='[]')
    risk_warnings = models.TextField(default='[]', blank=True)
    recommendations = models.TextField(default='[]')
    confidence_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ai_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Analysis for {self.record_id}"


class AIInsight(models.Model):
    """Additional AI insights and predictions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record_id = models.UUIDField(blank=True, null=True)
    user_id = models.UUIDField(default=uuid.uuid4)
    insight_type = models.TextField()
    content = models.TextField()
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_insights'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.insight_type} - {self.user_id}"


class Consultation(models.Model):
    """Doctor-patient consultations"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('scheduled_no_consent', 'Scheduled No Consent'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(default=uuid.uuid4)
    doctor_id = models.UUIDField(default=uuid.uuid4)
    consultation_date = models.DateField()
    consultation_time = models.TimeField()
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='scheduled')
    consent_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation {self.id} - {self.consultation_date}"


class Notification(models.Model):
    """User notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4)
    profile_id = models.UUIDField(blank=True, null=True)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user_id}"


class ConsentRequest(models.Model):
    """Consent requests from doctors to patients"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(default=uuid.uuid4)
    doctor_id = models.UUIDField(default=uuid.uuid4)
    purpose = models.TextField()
    requested_data_types = models.JSONField(default=list)
    duration_days = models.IntegerField(default=30)
    status = models.TextField(choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consent_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consent Request {self.id} - {self.status}"


class Consent(models.Model):
    """Active consents granted by patients"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(default=uuid.uuid4)
    doctor_id = models.UUIDField(default=uuid.uuid4)
    record_ids = models.JSONField(default=list, blank=True)
    scope = models.TextField(default='view')
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consent {self.id} - {self.status}"


class AccessLog(models.Model):
    """Access logging for audit trails"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.UUIDField()
    patient_id = models.UUIDField()
    record_id = models.UUIDField(blank=True, null=True)
    action = models.TextField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'access_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Access Log {self.id} - {self.action}"


class Event(models.Model):
    """System events and activities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4)
    event_type = models.TextField()
    event_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Event {self.event_type} - {self.user_id}"


class Schedule(models.Model):
    """Doctor schedules and appointments"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.UUIDField()
    patient_id = models.UUIDField(blank=True, null=True)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.TextField(choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Schedule {self.id} - {self.schedule_date}"


class Prescription(models.Model):
    """Prescription management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(default=uuid.uuid4)
    doctor_id = models.UUIDField(default=uuid.uuid4)
    consultation_id = models.UUIDField(blank=True, null=True)
    medication_name = models.TextField()
    dosage = models.TextField()
    frequency = models.TextField()
    duration = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription {self.id} - {self.medication_name}"


class ConsultationNote(models.Model):
    """Notes from consultations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation_id = models.UUIDField()
    doctor_id = models.UUIDField()
    notes = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation Note {self.id}"


class PatientAccess(models.Model):
    """Patient access controls for doctors"""
    ACCESS_LEVEL_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('full', 'Full'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(default=uuid.uuid4)
    doctor_id = models.UUIDField(default=uuid.uuid4)
    access_level = models.TextField(choices=ACCESS_LEVEL_CHOICES, default='view')
    granted_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_access'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Patient Access {self.id} - {self.access_level}"


class PrescriptionFile(models.Model):
    """File uploads for prescriptions"""
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    doctor_id = models.UUIDField()
    consultation_id = models.UUIDField(blank=True, null=True)
    file_name = models.TextField()
    file_type = models.TextField(choices=FILE_TYPE_CHOICES)
    file_url = models.TextField()  # S3 URL or local media URL
    file_size = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription File {self.id} - {self.file_name}"


class ConsultationNoteFile(models.Model):
    """File uploads for consultation notes"""
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    doctor_id = models.UUIDField()
    consultation_id = models.UUIDField(blank=True, null=True)
    file_name = models.TextField()
    file_type = models.TextField(choices=FILE_TYPE_CHOICES)
    file_url = models.TextField()  # S3 URL or local media URL
    file_size = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_note_files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation Note File {self.id} - {self.file_name}"