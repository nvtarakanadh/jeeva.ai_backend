from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
    first_name = models.CharField(max_length=120, blank=True, default="")
    last_name = models.CharField(max_length=120, blank=True, default="")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=40, blank=True, null=True)

    # Doctor-only optional fields
    specialization = models.CharField(max_length=120, blank=True, null=True)
    license_number = models.CharField(max_length=120, blank=True, null=True)
    hospital_affiliation = models.CharField(max_length=200, blank=True, null=True)

    # Optional demographics
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=40, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.role})".strip()


class HealthRecord(TimeStampedModel):
    RECORD_TYPE_CHOICES = (
        ("prescription", "Prescription"),
        ("lab_report", "Lab Report"),
        ("imaging", "Imaging"),
        ("consultation_note", "Consultation Note"),
        ("discharge_summary", "Discharge Summary"),
        ("other", "Other"),
    )

    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="records")
    record_type = models.CharField(max_length=40, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file_url = models.CharField(max_length=500, blank=True, null=True)
    file_type = models.CharField(max_length=80, blank=True, null=True)
    date_recorded = models.DateField(blank=True, null=True)

    doctor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_records")
    hospital_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title} - {self.record_type}"


class ConsentRequest(TimeStampedModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
        ("revoked", "Revoked"),
    )

    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="consent_requests_received")
    doctor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="consent_requests_sent")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    purpose = models.TextField()
    expiry_date = models.DateField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Consent {self.status} - patient={self.patient_id} doctor={self.doctor_id}"


class AIInsight(models.Model):
    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="ai_insights")
    record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE, related_name="ai_insights", blank=True, null=True)
    insight_type = models.CharField(max_length=120)
    content = models.JSONField()
    risk_level = models.CharField(max_length=40, blank=True, null=True)
    recommendations = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Insight {self.insight_type} ({self.risk_level})"


class AccessLog(models.Model):
    ACTION_CHOICES = (
        ("list_records", "List Records"),
        ("view_record", "View Record"),
        ("download_record", "Download Record"),
        ("create_record", "Create Record"),
        ("list_insights", "List Insights"),
    )

    doctor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="access_logs")
    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="accessed_logs")
    record = models.ForeignKey(HealthRecord, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=40, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.action} d={self.doctor_id} p={self.patient_id} r={self.record_id}"

