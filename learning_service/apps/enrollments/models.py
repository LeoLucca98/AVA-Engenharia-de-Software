from django.db import models
from django.core.exceptions import ValidationError


class Enrollment(models.Model):
    """
    Modelo para matrículas em cursos
    """
    ROLE_CHOICES = [
        ('student', 'Estudante'),
        ('instructor', 'Instrutor'),
        ('owner', 'Proprietário'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('suspended', 'Suspenso'),
        ('cancelled', 'Cancelado'),
    ]
    
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Curso'
    )
    user_id = models.IntegerField(
        verbose_name='ID do Usuário',
        help_text='ID do usuário matriculado'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Papel',
        help_text='Papel do usuário no curso'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status',
        help_text='Status da matrícula'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Matrícula'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        db_table = 'enrollments'
        unique_together = ['course', 'user_id']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['course', 'user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - User {self.user_id} ({self.role})"
    
    def clean(self):
        # Valida se o usuário não está tentando se matricular como owner
        if self.role == 'owner' and self.course.owner_id != self.user_id:
            raise ValidationError('Apenas o proprietário do curso pode ter papel de owner')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Verifica se a matrícula está ativa"""
        return self.status == 'active'
    
    @property
    def is_instructor(self):
        """Verifica se o usuário é instrutor"""
        return self.role in ['instructor', 'owner']
    
    @property
    def is_student(self):
        """Verifica se o usuário é estudante"""
        return self.role == 'student'
