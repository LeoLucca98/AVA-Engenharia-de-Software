from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from drf_spectacular.utils import extend_schema

from .models import Resource
from .serializers import (
    ResourceSerializer, ResourceListSerializer, ResourceCreateSerializer
)
from apps.common.decorators import require_authentication
from apps.common.utils import extract_user_id


class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para recursos
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'type', 'tags']
    search_fields = ['title', 'tags']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'list':
            return ResourceListSerializer
        elif self.action == 'create':
            return ResourceCreateSerializer
        return ResourceSerializer
    
    def get_queryset(self):
        """Filtra recursos baseado nas permissões do usuário"""
        user_id = extract_user_id(self.request)
        
        if not user_id:
            # Usuário não autenticado - apenas recursos de cursos públicos
            return Resource.objects.filter(course__is_published=True)
        
        # Usuário autenticado - recursos de cursos públicos + cursos do usuário
        return Resource.objects.filter(
            models.Q(course__is_published=True) | 
            models.Q(course__owner_id=user_id)
        ).distinct()
    
    def perform_create(self, serializer):
        """Verifica permissões ao criar recurso"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        course = serializer.validated_data['course']
        if course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode criar recursos")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode editar recursos")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode deletar recursos")
        
        instance.delete()
    
    @extend_schema(
        summary="Listar recursos por tipo",
        description="Lista recursos filtrados por tipo"
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Lista recursos por tipo"""
        resource_type = request.query_params.get('type')
        if not resource_type:
            return Response(
                {'error': 'Parâmetro type é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resources = self.get_queryset().filter(type=resource_type)
        serializer = ResourceListSerializer(resources, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Listar recursos por curso",
        description="Lista recursos de um curso específico"
    )
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """Lista recursos por curso"""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'error': 'Parâmetro course_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resources = self.get_queryset().filter(course_id=course_id)
        serializer = ResourceListSerializer(resources, many=True)
        return Response(serializer.data)
