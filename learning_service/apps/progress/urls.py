from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressViewSet, InteractionViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet)
router.register(r'interactions', InteractionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
