from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema

from .models import Enrollment
from .serializers import (
    EnrollmentSerializer, EnrollmentListSerializer, 
    EnrollmentCreateSerializer, MyCoursesSerializer
)
from apps.common.decorators import require_authentication
from apps.common.auth_helpers import get_user_id_from_request, IsAuthenticatedOrTrustedHeader


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet para matrículas"""

    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'user_id', 'role', 'status']
    ordering_fields = ['enrolled_at', 'updated_at']
    ordering = ['-enrolled_at']

    permission_classes = [IsAuthenticatedOrTrustedHeader]

    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'list':
            return EnrollmentListSerializer
        elif self.action == 'create':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def get_queryset(self):
        """Filtra matrículas baseado nas permissões do usuário"""
        user_id = get_user_id_from_request(self.request)

        if not user_id:
            return Enrollment.objects.none()

        # Usuário autenticado - apenas suas matrículas
        return Enrollment.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        """Cria matrícula com user_id do usuário autenticado"""
        user_id = get_user_id_from_request(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")

        # Verifica se o usuário já está matriculado
        course = serializer.validated_data['course']
        existing_enrollment = Enrollment.objects.filter(
            course=course,
            user_id=user_id,
            status='active'
        ).first()

        if existing_enrollment:
            raise permissions.PermissionDenied("Usuário já está matriculado neste curso")

        serializer.save(user_id=user_id)

    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = get_user_id_from_request(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")

        if serializer.instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode editar sua matrícula")

        serializer.save()

    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = get_user_id_from_request(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")

        if instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode cancelar sua matrícula")

        instance.delete()
    
    @extend_schema(
        summary="Listar cursos do usuário",
        description="Lista todos os cursos do usuário autenticado com informações de matrícula"
    )
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Lista cursos do usuário autenticado"""
        user_id = get_user_id_from_request(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        enrollments = Enrollment.objects.filter(user_id=user_id, status='active')
        serializer = MyCoursesSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Matricular em curso",
        description="Matricula o usuário autenticado em um curso"
    )
    @action(detail=False, methods=['post'])
    def enroll(self, request):
        """Matricula o usuário em um curso"""
        user_id = get_user_id_from_request(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = EnrollmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Verifica se o usuário já está matriculado
            course = serializer.validated_data['course']
            existing_enrollment = Enrollment.objects.filter(
                course=course,
                user_id=user_id
            ).first()

            if existing_enrollment:
                # Se não está ativa, reativa matrícula (cancelled/completed/suspended)
                if existing_enrollment.status != 'active':
                    # Atualiza papel se fornecido
                    new_role = serializer.validated_data.get('role')
                    if new_role:
                        existing_enrollment.role = new_role
                    existing_enrollment.status = 'active'
                    existing_enrollment.save()
                    response_serializer = EnrollmentSerializer(existing_enrollment)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                # Já está ativa: tornar idempotente e retornar 200 com a matrícula
                response_serializer = EnrollmentSerializer(existing_enrollment)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            # Cria a matrícula
            enrollment = serializer.save(user_id=user_id)
            response_serializer = EnrollmentSerializer(enrollment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Desmatricular de curso",
        description="Desmatricula o usuário autenticado de um curso"
    )
    @action(detail=False, methods=['post'])
    def unenroll(self, request):
        """Desmatricula o usuário de um curso"""
        user_id = get_user_id_from_request(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            enrollment = Enrollment.objects.get(
                course_id=course_id,
                user_id=user_id,
                status='active'
            )
            enrollment.status = 'cancelled'
            enrollment.save()
            
            return Response(
                {'message': 'Desmatriculado com sucesso'}, 
                status=status.HTTP_200_OK
            )
            
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Matrícula não encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
