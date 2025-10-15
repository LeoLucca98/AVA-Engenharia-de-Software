"""
URL configuration for learning_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def health_check(request):
    """Health check endpoint for the learning service."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'learning-service',
        'version': '1.0.0',
        'timestamp': '2024-01-01T12:00:00Z'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('learning/', include('apps.courses.urls')),
    path('learning/', include('apps.enrollments.urls')),
    path('learning/', include('apps.resources.urls')),
    path('learning/', include('apps.progress.urls')),
    
    # Health check
    path('healthz/', health_check, name='health_check'),
    
    # OpenAPI/Swagger
    path('learning/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('learning/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('learning/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
