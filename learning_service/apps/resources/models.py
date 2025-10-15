from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class Resource(models.Model):
    """
    Modelo para recursos de curso
    """
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'Vídeo'),
        ('link', 'Link'),
        ('file', 'Arquivo'),
        ('image', 'Imagem'),
        ('audio', 'Áudio'),
    ]
    
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Curso'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Tipo',
        help_text='Tipo do recurso'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título do recurso'
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL',
        help_text='URL do recurso (para links e vídeos)'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Caminho do Arquivo',
        help_text='Caminho do arquivo no servidor'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadados',
        help_text='Metadados adicionais do recurso'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tags',
        help_text='Tags para categorização'
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
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        db_table = 'resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def clean(self):
        # Valida se pelo menos um dos campos url ou file_path está preenchido
        if not self.url and not self.file_path:
            raise ValidationError('Pelo menos um dos campos URL ou Caminho do Arquivo deve ser preenchido')
        
        # Valida tags
        if self.tags and not isinstance(self.tags, list):
            raise ValidationError('Tags deve ser uma lista')
        
        # Limita o número de tags
        if self.tags and len(self.tags) > 10:
            raise ValidationError('Máximo de 10 tags permitidas')
        
        # Valida metadata
        if self.metadata and not isinstance(self.metadata, dict):
            raise ValidationError('Metadados deve ser um dicionário')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def resource_url(self):
        """Retorna a URL ou caminho do recurso"""
        return self.url or self.file_path
    
    @property
    def is_external(self):
        """Verifica se o recurso é externo (URL)"""
        return bool(self.url)
    
    @property
    def is_file(self):
        """Verifica se o recurso é um arquivo"""
        return bool(self.file_path)
