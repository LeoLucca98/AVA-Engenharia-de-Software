from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Course, Module, Lesson
from .serializers import (
    CourseSerializer, CourseListSerializer, CourseDetailSerializer,
    ModuleSerializer, LessonSerializer, LessonListSerializer
)
from apps.common.auth_helpers import (
    IsAuthenticatedOrTrustedHeader, IsOwnerOrInstructor, IsStudentOrInstructor,
    get_user_id_from_request, log_auth_info
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para cursos
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner_id', 'is_published', 'tags']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticatedOrTrustedHeader]
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'list':
            return CourseListSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def get_queryset(self):
        """Filtra cursos baseado nas permissões do usuário"""
        user_id = get_user_id_from_request(self.request)
        log_auth_info(self.request, "get_queryset")
        
        if not user_id:
            # Usuário não autenticado - apenas cursos públicos
            return Course.objects.filter(is_published=True)
        
        # Usuário autenticado - cursos públicos + cursos do usuário
        return Course.objects.filter(
            models.Q(is_published=True) | 
            models.Q(owner_id=user_id)
        ).distinct()
    
    def perform_create(self, serializer):
        """Define o owner_id ao criar um curso"""
        user_id = get_user_id_from_request(self.request)
        log_auth_info(self.request, "perform_create")
        
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        serializer.save(owner_id=user_id)
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = get_user_id_from_request(self.request)
        log_auth_info(self.request, "perform_update")
        
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode editar o curso")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode deletar o curso")
        
        instance.delete()
    
    @extend_schema(
        summary="Listar cursos do usuário",
        description="Lista todos os cursos do usuário autenticado"
    )
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Lista cursos do usuário autenticado"""
        user_id = extract_user_id(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        courses = Course.objects.filter(owner_id=user_id)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para módulos
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        """Filtra módulos baseado nas permissões do usuário"""
        user_id = extract_user_id(self.request)
        course_id = self.request.query_params.get('course')
        
        if not user_id:
            # Usuário não autenticado - apenas módulos de cursos públicos
            return Module.objects.filter(course__is_published=True)
        
        # Usuário autenticado - módulos de cursos públicos + cursos do usuário
        return Module.objects.filter(
            models.Q(course__is_published=True) | 
            models.Q(course__owner_id=user_id)
        ).distinct()
    
    def perform_create(self, serializer):
        """Verifica permissões ao criar módulo"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        course = serializer.validated_data['course']
        if course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode criar módulos")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode editar módulos")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode deletar módulos")
        
        instance.delete()


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para lições
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module', 'module__course', 'content_type']
    search_fields = ['title', 'content']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer
    
    def get_queryset(self):
        """Filtra lições baseado nas permissões do usuário"""
        user_id = extract_user_id(self.request)
        
        if not user_id:
            # Usuário não autenticado - apenas lições de cursos públicos
            return Lesson.objects.filter(module__course__is_published=True)
        
        # Usuário autenticado - lições de cursos públicos + cursos do usuário
        return Lesson.objects.filter(
            models.Q(module__course__is_published=True) | 
            models.Q(module__course__owner_id=user_id)
        ).distinct()
    
    def perform_create(self, serializer):
        """Verifica permissões ao criar lição"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        module = serializer.validated_data['module']
        if module.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode criar lições")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.module.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode editar lições")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.module.course.owner_id != user_id:
            raise permissions.PermissionDenied("Apenas o proprietário pode deletar lições")
        
        instance.delete()
