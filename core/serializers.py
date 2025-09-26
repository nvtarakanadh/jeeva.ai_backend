from rest_framework import serializers
from .models import Profile, HealthRecord, ConsentRequest, AIInsight, AccessLog


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "role",
            "first_name",
            "last_name",
            "email",
            "phone",
            "specialization",
            "license_number",
            "hospital_affiliation",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact",
            "created_at",
            "updated_at",
        )


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = (
            "id",
            "patient",
            "record_type",
            "title",
            "description",
            "file_url",
            "file_type",
            "date_recorded",
            "doctor",
            "hospital_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("patient", "doctor", "created_at", "updated_at")


class NestedProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "first_name", "last_name", "email")


class ConsentRequestSerializer(serializers.ModelSerializer):
    doctor = NestedProfileSerializer(read_only=True)
    patient = NestedProfileSerializer(read_only=True)
    class Meta:
        model = ConsentRequest
        fields = (
            "id",
            "patient",
            "doctor",
            "status",
            "purpose",
            "expiry_date",
            "requested_at",
            "responded_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "patient",
            "doctor",
            "requested_at",
            "responded_at",
            "created_at",
            "updated_at",
        )


class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = (
            "id",
            "patient",
            "record",
            "insight_type",
            "content",
            "risk_level",
            "recommendations",
            "created_at",
        )
        read_only_fields = ("patient", "created_at")


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ("id", "doctor", "patient", "record", "action", "reason", "created_at")
        read_only_fields = ("id", "created_at")


