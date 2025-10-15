from rest_framework import serializers
from .models import Resource
from apps.common.utils import validate_tags, validate_metadata


class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer para recursos
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    resource_url = serializers.ReadOnlyField()
    is_external = serializers.ReadOnlyField()
    is_file = serializers.ReadOnlyField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'course', 'course_title', 'type', 'title',
            'url', 'file_path', 'resource_url', 'metadata',
            'tags', 'created_at', 'updated_at',
            'is_external', 'is_file'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Valida o título"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Título deve ter pelo menos 3 caracteres")
        return value.strip()
    
    def validate_tags(self, value):
        """Valida e limpa as tags"""
        return validate_tags(value)
    
    def validate_metadata(self, value):
        """Valida e limpa os metadados"""
        return validate_metadata(value)
    
    def validate(self, attrs):
        """Valida o recurso"""
        url = attrs.get('url')
        file_path = attrs.get('file_path')
        
        # Valida se pelo menos um dos campos está preenchido
        if not url and not file_path:
            raise serializers.ValidationError(
                "Pelo menos um dos campos URL ou Caminho do Arquivo deve ser preenchido"
            )
        
        return attrs


class ResourceListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de recursos
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    resource_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'course', 'course_title', 'type', 'title',
            'resource_url', 'created_at'
        ]


class ResourceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de recursos
    """
    class Meta:
        model = Resource
        fields = [
            'course', 'type', 'title', 'url', 'file_path',
            'metadata', 'tags'
        ]
    
    def validate_type(self, value):
        """Valida o tipo"""
        valid_types = ['pdf', 'video', 'link', 'file', 'image', 'audio']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Tipo deve ser um dos seguintes: {', '.join(valid_types)}"
            )
        return value
