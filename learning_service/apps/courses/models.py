from django.db import models
from django.core.validators import MinLengthValidator
from apps.common.utils import safe_json_loads, safe_json_dumps


class Course(models.Model):
    """
    Modelo para cursos
    """
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        verbose_name='Título'
    )
    description = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição detalhada do curso'
    )
    owner_id = models.IntegerField(
        verbose_name='ID do Proprietário',
        help_text='ID do usuário que criou o curso'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tags',
        help_text='Lista de tags para categorização'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Publicado',
        help_text='Se o curso está disponível publicamente'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        db_table = 'courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner_id']),
            models.Index(fields=['is_published']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Valida tags
        if self.tags and not isinstance(self.tags, list):
            raise ValidationError('Tags deve ser uma lista')
        
        # Limita o número de tags
        if self.tags and len(self.tags) > 10:
            raise ValidationError('Máximo de 10 tags permitidas')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def total_lessons(self):
        """Retorna o total de lições do curso"""
        return Lesson.objects.filter(module__course=self).count()
    
    @property
    def total_modules(self):
        """Retorna o total de módulos do curso"""
        return self.modules.count()


class Module(models.Model):
    """
    Modelo para módulos de curso
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Curso'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        verbose_name='Título'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição do módulo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        db_table = 'modules'
        ordering = ['course', 'order', 'created_at']
        unique_together = ['course', 'order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def total_lessons(self):
        """Retorna o total de lições do módulo"""
        return self.lessons.count()


class Lesson(models.Model):
    """
    Modelo para lições
    """
    CONTENT_TYPE_CHOICES = [
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
    ]
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Módulo'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        verbose_name='Título'
    )
    content = models.TextField(
        verbose_name='Conteúdo',
        help_text='Conteúdo da lição em Markdown ou HTML'
    )
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='markdown',
        verbose_name='Tipo de Conteúdo'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição da lição'
    )
    resource_links = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Links de Recursos',
        help_text='Lista de links para recursos externos'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Lição'
        verbose_name_plural = 'Lições'
        db_table = 'lessons'
        ordering = ['module', 'order', 'created_at']
        unique_together = ['module', 'order']
        indexes = [
            models.Index(fields=['module', 'order']),
        ]
    
    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Valida resource_links
        if self.resource_links and not isinstance(self.resource_links, list):
            raise ValidationError('Resource links deve ser uma lista')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def course(self):
        """Retorna o curso da lição"""
        return self.module.course
