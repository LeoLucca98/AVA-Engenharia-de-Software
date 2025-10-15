from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Course, Module, Lesson
from apps.common.utils import validate_tags, validate_metadata


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer para cursos
    """
    total_lessons = serializers.ReadOnlyField()
    total_modules = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'owner_id', 'tags',
            'is_published', 'created_at', 'updated_at',
            'total_lessons', 'total_modules'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_id']
    
    def validate_tags(self, value):
        """Valida e limpa as tags"""
        return validate_tags(value)
    
    def validate_title(self, value):
        """Valida o título"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Título deve ter pelo menos 3 caracteres")
        return value.strip()
    
    def validate_description(self, value):
        """Valida a descrição"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Descrição deve ter pelo menos 10 caracteres")
        return value.strip()


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de cursos
    """
    total_lessons = serializers.ReadOnlyField()
    total_modules = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'owner_id', 'tags',
            'is_published', 'created_at', 'total_lessons', 'total_modules'
        ]


class ModuleSerializer(serializers.ModelSerializer):
    """
    Serializer para módulos
    """
    total_lessons = serializers.ReadOnlyField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'course', 'course_title', 'title', 'order',
            'created_at', 'updated_at', 'total_lessons'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Valida o título"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Título deve ter pelo menos 3 caracteres")
        return value.strip()
    
    def validate_order(self, value):
        """Valida a ordem"""
        if value < 0:
            raise serializers.ValidationError("Ordem deve ser um número positivo")
        return value


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer para lições
    """
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'course_title', 'module_title', 'title',
            'content', 'content_type', 'order', 'resource_links',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Valida o título"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Título deve ter pelo menos 3 caracteres")
        return value.strip()
    
    def validate_content(self, value):
        """Valida o conteúdo"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Conteúdo deve ter pelo menos 10 caracteres")
        return value.strip()
    
    def validate_order(self, value):
        """Valida a ordem"""
        if value < 0:
            raise serializers.ValidationError("Ordem deve ser um número positivo")
        return value
    
    def validate_resource_links(self, value):
        """Valida os links de recursos"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Resource links deve ser uma lista")
        
        # Valida cada link
        for link in value:
            if not isinstance(link, dict):
                raise serializers.ValidationError("Cada link deve ser um objeto")
            
            if 'url' not in link or 'title' not in link:
                raise serializers.ValidationError("Cada link deve ter 'url' e 'title'")
        
        return value


class LessonListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de lições
    """
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'course_title', 'module_title', 'title',
            'content_type', 'order', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para curso com módulos e lições
    """
    modules = ModuleSerializer(many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    total_modules = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'owner_id', 'tags',
            'is_published', 'created_at', 'updated_at',
            'total_lessons', 'total_modules', 'modules'
        ]
