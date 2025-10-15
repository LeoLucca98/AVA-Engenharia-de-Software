from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema

from .models import Progress, Interaction
from .serializers import (
    ProgressSerializer, ProgressListSerializer, MarkCompleteSerializer,
    InteractionSerializer, InteractionCreateSerializer, LessonProgressSerializer
)
from apps.common.decorators import require_authentication
from apps.common.utils import extract_user_id, send_interaction_event


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet para progresso
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user_id', 'lesson', 'completed']
    ordering_fields = ['created_at', 'updated_at', 'last_accessed']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'list':
            return ProgressListSerializer
        return ProgressSerializer
    
    def get_queryset(self):
        """Filtra progresso baseado nas permissões do usuário"""
        user_id = extract_user_id(self.request)
        
        if not user_id:
            return Progress.objects.none()
        
        # Usuário autenticado - apenas seu progresso
        return Progress.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        """Cria progresso com user_id do usuário autenticado"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        serializer.save(user_id=user_id)
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode editar seu progresso")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode deletar seu progresso")
        
        instance.delete()
    
    @extend_schema(
        summary="Marcar lição como concluída",
        description="Marca uma lição como concluída para o usuário autenticado"
    )
    @action(detail=False, methods=['post'])
    def mark_complete(self, request):
        """Marca uma lição como concluída"""
        user_id = extract_user_id(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = MarkCompleteSerializer(data=request.data)
        if serializer.is_valid():
            lesson_id = serializer.validated_data['lesson_id']
            score = serializer.validated_data.get('score')
            time_spent = serializer.validated_data.get('time_spent', 0)
            
            # Busca ou cria o progresso
            progress, created = Progress.objects.get_or_create(
                user_id=user_id,
                lesson_id=lesson_id,
                defaults={
                    'completed': True,
                    'score': score,
                    'time_spent': time_spent
                }
            )
            
            if not created:
                # Atualiza o progresso existente
                progress.completed = True
                if score is not None:
                    progress.score = score
                progress.time_spent += time_spent
                progress.save()
            
            # Envia evento de interação
            send_interaction_event(
                user_id=user_id,
                lesson_id=lesson_id,
                interaction_type='complete',
                payload={
                    'score': score,
                    'time_spent': time_spent
                }
            )
            
            response_serializer = ProgressSerializer(progress)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Obter progresso de uma lição",
        description="Obtém o progresso do usuário autenticado em uma lição específica"
    )
    @action(detail=False, methods=['get'])
    def lesson_progress(self, request):
        """Obtém o progresso de uma lição específica"""
        user_id = extract_user_id(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        lesson_id = request.query_params.get('lesson_id')
        if not lesson_id:
            return Response(
                {'error': 'Parâmetro lesson_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            progress = Progress.objects.get(
                user_id=user_id,
                lesson_id=lesson_id
            )
            serializer = LessonProgressSerializer(progress)
            return Response(serializer.data)
            
        except Progress.DoesNotExist:
            return Response(
                {'message': 'Progresso não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Listar progresso por curso",
        description="Lista o progresso do usuário autenticado em um curso específico"
    )
    @action(detail=False, methods=['get'])
    def course_progress(self, request):
        """Lista o progresso por curso"""
        user_id = extract_user_id(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'error': 'Parâmetro course_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        progress = Progress.objects.filter(
            user_id=user_id,
            lesson__module__course_id=course_id
        )
        
        serializer = ProgressListSerializer(progress, many=True)
        return Response(serializer.data)


class InteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para interações
    """
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user_id', 'lesson', 'resource', 'interaction_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação"""
        if self.action == 'create':
            return InteractionCreateSerializer
        return InteractionSerializer
    
    def get_queryset(self):
        """Filtra interações baseado nas permissões do usuário"""
        user_id = extract_user_id(self.request)
        
        if not user_id:
            return Interaction.objects.none()
        
        # Usuário autenticado - apenas suas interações
        return Interaction.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        """Cria interação com user_id do usuário autenticado"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        interaction = serializer.save(user_id=user_id)
        
        # Envia evento de interação para o recommendation service
        if interaction.lesson:
            send_interaction_event(
                user_id=user_id,
                lesson_id=interaction.lesson.id,
                interaction_type=interaction.interaction_type,
                payload=interaction.payload
            )
    
    def perform_update(self, serializer):
        """Verifica permissões ao atualizar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if serializer.instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode editar suas interações")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Verifica permissões ao deletar"""
        user_id = extract_user_id(self.request)
        if not user_id:
            raise permissions.PermissionDenied("Autenticação necessária")
        
        if instance.user_id != user_id:
            raise permissions.PermissionDenied("Apenas o próprio usuário pode deletar suas interações")
        
        instance.delete()
    
    @extend_schema(
        summary="Listar interações por tipo",
        description="Lista interações do usuário filtradas por tipo"
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Lista interações por tipo"""
        user_id = extract_user_id(request)
        if not user_id:
            return Response(
                {'error': 'Autenticação necessária'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        interaction_type = request.query_params.get('type')
        if not interaction_type:
            return Response(
                {'error': 'Parâmetro type é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        interactions = self.get_queryset().filter(interaction_type=interaction_type)
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)
