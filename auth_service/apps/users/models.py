from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuário customizado que estende AbstractUser
    """
    email = models.EmailField(
        unique=True,
        verbose_name='E-mail'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Nome'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Sobrenome'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de cadastro'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_roles(self):
        """
        Retorna os roles do usuário baseado em permissões.
        Roles podem ser: 'admin', 'instructor', 'student'
        """
        roles = []
        if self.is_superuser or self.is_staff:
            roles.append('admin')
        # Por padrão, todos os usuários têm role 'student'
        if 'student' not in roles:
            roles.append('student')
        return roles