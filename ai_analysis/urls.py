from django.urls import path
from . import views
from . import simple_views
from . import cors_fix
from . import health_fix
from . import medical_report_cors_fix

urlpatterns = [
    path('analyze/prescription/', views.analyze_prescription, name='analyze_prescription'),
    path('analyze/health-record/', cors_fix.analyze_health_record_cors_fix, name='analyze_health_record'),
    path('analyze/medical-report/', medical_report_cors_fix.analyze_medical_report_cors_fix, name='analyze_medical_report'),
    path('analyze/medicines/', views.analyze_medicines, name='analyze_medicines'),
    path('analysis/<str:record_id>/', views.get_analysis, name='get_analysis'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    path('health/', health_fix.health_check_cors_fix, name='health_check'),
    path('test-structure/', views.test_response_structure, name='test_response_structure'),
    # File upload endpoints
    path('upload/prescription-file/', views.upload_prescription_file, name='upload_prescription_file'),
    path('upload/consultation-note-file/', views.upload_consultation_note_file, name='upload_consultation_note_file'),
    path('files/prescription/<str:patient_id>/', views.get_prescription_files, name='get_prescription_files'),
    path('files/consultation-note/<str:patient_id>/', views.get_consultation_note_files, name='get_consultation_note_files'),
]
