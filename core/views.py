import json
import re
import os
import requests

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Profile, HealthRecord, ConsentRequest, AIInsight, AccessLog
from .serializers import (
    ProfileSerializer,
    HealthRecordSerializer,
    ConsentRequestSerializer,
    AIInsightSerializer,
)


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def me(self, request):
        email = request.headers.get("X-User-Email") or request.query_params.get("email")
        if not email:
            return Response({"detail": "email required"}, status=400)
        profile, _ = Profile.objects.get_or_create(email=email, defaults={"first_name": "", "last_name": ""})
        return Response(ProfileSerializer(profile).data)

    @me.mapping.put
    def update_me(self, request):
        email = request.headers.get("X-User-Email") or request.data.get("email")
        if not email:
            return Response({"detail": "email required"}, status=400)
        profile, _ = Profile.objects.get_or_create(email=email)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class HealthRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = HealthRecordSerializer

    def get_queryset(self):
        email = self.request.headers.get("X-User-Email")
        me = Profile.objects.filter(email=email).first()
        role = self.request.query_params.get("role") or (me.role if me else "patient")

        # Patient sees own records
        if role == "patient":
            return HealthRecord.objects.filter(patient=me).order_by("-created_at")

        # Doctor sees records for patients who approved consent
        if role == "doctor":
            approved_patient_ids = ConsentRequest.objects.filter(
                doctor=me, status="approved"
            ).values_list("patient_id", flat=True)
            qs = HealthRecord.objects.filter(patient_id__in=approved_patient_ids)
            patient_email = self.request.query_params.get("patient_email")
            if patient_email:
                patient = Profile.objects.filter(email=patient_email).first()
                if patient:
                    qs = qs.filter(patient=patient)
            return qs.order_by("-created_at")

        # Fallback: no records
        return HealthRecord.objects.none()

    # Ensure clients always see freshest records
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Log list access for doctors
        email = request.headers.get("X-User-Email")
        me = Profile.objects.filter(email=email).first()
        if me and me.role == "doctor":
            patient_email = request.query_params.get("patient_email")
            patient = Profile.objects.filter(email=patient_email).first() if patient_email else None
            AccessLog.objects.create(doctor=me, patient=patient or me, action="list_records")
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        return response

    def perform_create(self, serializer):
        email = self.request.headers.get("X-User-Email")
        me = Profile.objects.get(email=email)
        # If a doctor is creating a record for a patient (e.g., prescription), allow passing patient_email
        patient_email = self.request.data.get("patient_email")
        patient = me
        if patient_email and me.role == "doctor":
            patient = Profile.objects.get(email=patient_email)
        serializer.save(patient=patient, doctor=(me if me.role == "doctor" else None))

    @action(detail=False, methods=["post"])
    def upload(self, request):
        """Simple file upload to MEDIA; returns a URL/path. For POC only."""
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "file required"}, status=400)
        # Save under uploads/<uuid>/<filename>
        path = default_storage.save(f"uploads/{file_obj.name}", ContentFile(file_obj.read()))
        return Response({"file_url": default_storage.url(path), "path": path})


class ConsentRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ConsentRequestSerializer

    def get_queryset(self):
        email = self.request.headers.get("X-User-Email")
        me = Profile.objects.filter(email=email).first()
        role = self.request.query_params.get("role")
        # If role filter is specified, scope accordingly
        if role == "doctor":
            return ConsentRequest.objects.filter(doctor=me).order_by("-created_at")
        if role == "patient":
            return ConsentRequest.objects.filter(patient=me).order_by("-created_at")

        # For detail routes without role, allow objects where current user is either party
        return ConsentRequest.objects.filter(
            Q(doctor=me) | Q(patient=me)
        ).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        # doctor sends request to patient by email
        doctor_email = request.headers.get("X-User-Email")
        patient_email = request.data.get("patient_email")
        purpose = request.data.get("purpose") or "Access to health records"
        expiry_date = request.data.get("expiry_date")

        if not patient_email:
            return Response({"detail": "patient_email is required"}, status=400)

        doctor = Profile.objects.get(email=doctor_email)
        patient, _ = Profile.objects.get_or_create(email=patient_email, defaults={"first_name": "", "last_name": ""})

        consent = ConsentRequest.objects.create(
            patient=patient, doctor=doctor, purpose=purpose, expiry_date=expiry_date or None
        )
        return Response(ConsentRequestSerializer(consent).data, status=201)

    def partial_update(self, request, *args, **kwargs):
        # patient approves/denies
        instance = self.get_object()
        status_value = request.data.get("status")
        if status_value not in {"approved", "denied", "revoked"}:
            return Response({"detail": "invalid status"}, status=400)
        instance.status = status_value
        instance.responded_at = instance.responded_at or instance.updated_at
        instance.save(update_fields=["status", "responded_at", "updated_at"])
        return Response(ConsentRequestSerializer(instance).data)


class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = AIInsightSerializer

    def get_queryset(self):
        email = self.request.headers.get("X-User-Email")
        me = Profile.objects.filter(email=email).first()
        role = self.request.query_params.get("role") or (me.role if me else "patient")

        if role == "patient":
            return AIInsight.objects.filter(patient=me).order_by("-created_at")

        if role == "doctor":
            approved_patient_ids = ConsentRequest.objects.filter(
                doctor=me, status="approved"
            ).values_list("patient_id", flat=True)
            return AIInsight.objects.filter(patient_id__in=approved_patient_ids).order_by("-created_at")

        return AIInsight.objects.none()

    # Ensure responses are not cached and always reflect latest insights
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        return response

    @action(detail=False, methods=["post"])
    def analyze(self, request):
        email = request.headers.get("X-User-Email")
        me = Profile.objects.get(email=email)
        record_id = request.data.get("record_id")
        record_text = request.data.get("record_text") or ""
        record_type = request.data.get("record_type") or "other"
        patient_email = request.data.get("patient_email")
        image_base64 = request.data.get("image_base64")  # optional, for handwritten prescriptions/images
        image_mime = request.data.get("image_mime") or "image/png"
        patient = me
        if patient_email and me.role == "doctor":
            # Ensure consent exists and approved
            patient = Profile.objects.get(email=patient_email)
            if not ConsentRequest.objects.filter(doctor=me, patient=patient, status="approved").exists():
                return Response({"detail": "Consent not approved"}, status=403)

        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            return Response({"detail": "GEMINI_API_KEY missing"}, status=500)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            parts = []
            prompt_text = (
                "You are a medical assistant. Extract a concise JSON with keys: "
                "summary (string), indicators (array of strings), risk_level (low|medium|high), "
                "recommendations (array of strings). Use only JSON in response.\n"
                f"Record type: {record_type}.\n"
                f"Patient-provided text: {record_text}"
            )
            parts.append({"text": prompt_text})
            if image_base64:
                parts.append({"inline_data": {"mime_type": image_mime, "data": image_base64}})

            body = {"contents": [{"parts": parts}]}
            r = requests.post(url, json=body, timeout=45)
            r.raise_for_status()
            data = r.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            def parse_json_loose(s: str):
                if not s:
                    return {}
                cleaned = s.strip()
                # remove triple backticks fences if present
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```[a-zA-Z0-9]*\n?", "", cleaned)
                    cleaned = cleaned.rstrip("`")
                # find first JSON object
                m = re.search(r"\{[\s\S]*\}", cleaned)
                if m:
                    cleaned = m.group(0)
                try:
                    return json.loads(cleaned)
                except Exception:
                    return {"raw": s}

            parsed = parse_json_loose(text)

            insight = AIInsight.objects.create(
                patient=patient,
                record_id=record_id,
                insight_type=record_type,
                content=parsed or {},
                risk_level=(parsed.get("risk_level") if isinstance(parsed, dict) else None),
                recommendations=(parsed.get("recommendations") if isinstance(parsed, dict) else None),
            )
            return Response(AIInsightSerializer(insight).data, status=201)
        except Exception as e:
            return Response({"detail": str(e)}, status=502)

from django.shortcuts import render

# Create your views here.
