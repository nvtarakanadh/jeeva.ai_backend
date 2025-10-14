from django.urls import path
from . import views

urlpatterns = [
    path('analyze/prescription/', views.analyze_prescription, name='analyze_prescription'),
    path('analyze/health-record/', views.analyze_health_record, name='analyze_health_record'),
    path('analyze/medicines/', views.analyze_medicines, name='analyze_medicines'),
    path('analysis/<str:record_id>/', views.get_analysis, name='get_analysis'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    path('health/', views.health_check, name='health_check'),
    path('test-structure/', views.test_response_structure, name='test_response_structure'),
]
