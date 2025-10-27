from rest_framework import serializers
from .models import Progress, Interaction


class ProgressSerializer(serializers.ModelSerializer):
    """
    Serializer para progresso
    """
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    module_title = serializers.CharField(source='lesson.module.title', read_only=True)
    
    class Meta:
        model = Progress
        fields = [
            'id', 'user_id', 'lesson', 'lesson_title', 'course_title',
            'module_title', 'completed', 'score', 'time_spent',
            'last_accessed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at', 'last_accessed']
    
    def validate_score(self, value):
        """Valida a pontuação"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Pontuação deve estar entre 0 e 100")
        return value
    
    def validate_time_spent(self, value):
        """Valida o tempo gasto"""
        if value < 0:
            raise serializers.ValidationError("Tempo gasto deve ser um número positivo")
        return value


class ProgressListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de progresso
    """
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    
    class Meta:
        model = Progress
        fields = [
            'id', 'lesson', 'lesson_title', 'course_title',
            'completed', 'score', 'time_spent', 'last_accessed'
        ]


class MarkCompleteSerializer(serializers.Serializer):
    """
    Serializer para marcar lição como concluída
    """
    lesson_id = serializers.IntegerField()
    score = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0.0,
        max_value=100.0
    )
    time_spent = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0
    )
    
    def validate_lesson_id(self, value):
        """Valida o ID da lição"""
        from apps.courses.models import Lesson
        
        try:
            lesson = Lesson.objects.get(id=value)
        except Lesson.DoesNotExist:
            raise serializers.ValidationError("Lição não encontrada")
        
        return value


class InteractionSerializer(serializers.ModelSerializer):
    """
    Serializer para interações
    """
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    target_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'user_id', 'lesson', 'lesson_title',
            'resource', 'resource_title', 'target_title',
            'interaction_type', 'payload', 'created_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at']
    
    def get_target_title(self, obj):
        """Retorna o título do alvo da interação"""
        return obj.target.title if obj.target else None
    
    def validate_payload(self, value):
        """Valida o payload"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload deve ser um dicionário")
        return value
    
    def validate(self, attrs):
        """Valida a interação"""
        lesson = attrs.get('lesson')
        resource = attrs.get('resource')
        
        # Valida se pelo menos um dos campos está preenchido
        if not lesson and not resource:
            raise serializers.ValidationError(
                "Pelo menos um dos campos Lição ou Recurso deve ser preenchido"
            )
        
        return attrs


class InteractionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de interações
    """
    class Meta:
        model = Interaction
        fields = [
            'lesson', 'resource', 'interaction_type', 'payload'
        ]
    
    def validate_interaction_type(self, value):
        """Valida o tipo de interação"""
        valid_types = ['view', 'like', 'note', 'answer', 'download', 'share', 'bookmark']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Tipo de interação deve ser um dos seguintes: {', '.join(valid_types)}"
            )
        return value


class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer para progresso de uma lição específica
    """
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    module_title = serializers.CharField(source='lesson.module.title', read_only=True)
    
    class Meta:
        model = Progress
        fields = [
            'id', 'lesson', 'lesson_title', 'course_title',
            'module_title', 'completed', 'score', 'time_spent',
            'last_accessed', 'created_at', 'updated_at'
        ]
