from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Progress(models.Model):
    """
    Modelo para progresso do usuário em lições
    """
    user_id = models.IntegerField(
        verbose_name='ID do Usuário',
        help_text='ID do usuário'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Lição'
    )
    completed = models.BooleanField(
        default=False,
        verbose_name='Concluído',
        help_text='Se a lição foi concluída'
    )
    score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name='Pontuação',
        help_text='Pontuação obtida na lição (0-100)'
    )
    time_spent = models.PositiveIntegerField(
        default=0,
        verbose_name='Tempo Gasto (segundos)',
        help_text='Tempo gasto na lição em segundos'
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        verbose_name='Último Acesso'
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
        verbose_name = 'Progresso'
        verbose_name_plural = 'Progressos'
        db_table = 'progress'
        unique_together = ['user_id', 'lesson']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['lesson']),
            models.Index(fields=['completed']),
            models.Index(fields=['user_id', 'completed']),
        ]
    
    def __str__(self):
        return f"User {self.user_id} - {self.lesson.title} ({'Concluído' if self.completed else 'Em andamento'})"
    
    @property
    def course(self):
        """Retorna o curso da lição"""
        return self.lesson.course
    
    @property
    def module(self):
        """Retorna o módulo da lição"""
        return self.lesson.module


class Interaction(models.Model):
    """
    Modelo para interações do usuário com lições e recursos
    """
    INTERACTION_TYPE_CHOICES = [
        ('view', 'Visualização'),
        ('like', 'Curtida'),
        ('note', 'Nota'),
        ('answer', 'Resposta'),
        ('download', 'Download'),
        ('share', 'Compartilhamento'),
        ('bookmark', 'Favorito'),
    ]
    
    user_id = models.IntegerField(
        verbose_name='ID do Usuário',
        help_text='ID do usuário'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
        verbose_name='Lição'
    )
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
        verbose_name='Recurso'
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPE_CHOICES,
        verbose_name='Tipo de Interação'
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados Adicionais',
        help_text='Dados específicos da interação'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    class Meta:
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'
        db_table = 'interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['lesson']),
            models.Index(fields=['resource']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        target = self.lesson.title if self.lesson else self.resource.title if self.resource else 'Desconhecido'
        return f"User {self.user_id} - {self.interaction_type} - {target}"
    
    def clean(self):
        # Valida se pelo menos um dos campos lesson ou resource está preenchido
        if not self.lesson and not self.resource:
            raise ValidationError('Pelo menos um dos campos Lição ou Recurso deve ser preenchido')
        
        # Valida payload
        if self.payload and not isinstance(self.payload, dict):
            raise ValidationError('Payload deve ser um dicionário')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def target(self):
        """Retorna o alvo da interação (lição ou recurso)"""
        return self.lesson or self.resource
