from rest_framework import serializers
from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer para matrículas
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_description = serializers.CharField(source='course.description', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_description',
            'user_id', 'role', 'status', 'enrolled_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrolled_at', 'updated_at']
    
    def validate(self, attrs):
        """Valida a matrícula"""
        course = attrs.get('course')
        user_id = attrs.get('user_id')
        role = attrs.get('role')
        
        # Verifica se o usuário já está matriculado
        existing_enrollment = Enrollment.objects.filter(
            course=course,
            user_id=user_id
        ).first()
        
        if existing_enrollment:
            raise serializers.ValidationError(
                "Usuário já está matriculado neste curso"
            )
        
        # Valida se o usuário não está tentando se matricular como owner
        if role == 'owner' and course.owner_id != user_id:
            raise serializers.ValidationError(
                "Apenas o proprietário do curso pode ter papel de owner"
            )
        
        return attrs


class EnrollmentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de matrículas
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'user_id',
            'role', 'status', 'enrolled_at'
        ]


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de matrículas
    """
    class Meta:
        model = Enrollment
        fields = ['course', 'role']
    
    def validate_role(self, value):
        """Valida o papel"""
        if value not in ['student', 'instructor']:
            raise serializers.ValidationError(
                "Papel deve ser 'student' ou 'instructor'"
            )
        return value


class MyCoursesSerializer(serializers.ModelSerializer):
    """
    Serializer para cursos do usuário
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_description = serializers.CharField(source='course.description', read_only=True)
    course_tags = serializers.ListField(source='course.tags', read_only=True)
    course_is_published = serializers.BooleanField(source='course.is_published', read_only=True)
    course_created_at = serializers.DateTimeField(source='course.created_at', read_only=True)
    total_lessons = serializers.IntegerField(source='course.total_lessons', read_only=True)
    total_modules = serializers.IntegerField(source='course.total_modules', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_description',
            'course_tags', 'course_is_published', 'course_created_at',
            'role', 'status', 'enrolled_at', 'total_lessons', 'total_modules'
        ]
