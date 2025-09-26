from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, HealthRecordViewSet, ConsentRequestViewSet, AIInsightViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'records', HealthRecordViewSet, basename='records')
router.register(r'consents', ConsentRequestViewSet, basename='consents')
router.register(r'ai/insights', AIInsightViewSet, basename='ai-insights')

urlpatterns = [
    path('', include(router.urls)),
]


