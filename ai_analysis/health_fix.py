"""
Ultra-simple health check with CORS fix
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def health_check_cors_fix(request):
    """Ultra-simple health check with CORS fix"""
    
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    # Handle HEAD request (for health checks)
    if request.method == "HEAD":
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # Handle GET request
    health_data = {
        'status': 'healthy',
        'message': 'Jeeva AI Backend is running with CORS fix',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'cors': 'enabled'
    }
    
    response = JsonResponse(health_data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
