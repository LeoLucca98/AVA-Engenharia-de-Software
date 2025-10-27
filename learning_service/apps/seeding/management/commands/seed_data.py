from django.core.management.base import BaseCommand
from django.db import transaction
from apps.courses.models import Course, Module, Lesson
from apps.resources.models import Resource


class Command(BaseCommand):
    help = 'Cria dados de exemplo para o learning service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true', help='Remove os dados seedados antes de recriar'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get('reset', False)

        seeded_courses = ['Python para Iniciantes', 'Django Web Development']

        if reset:
            self.stdout.write('Limpando dados seedados...')
            # Deleta apenas os cursos criados pelo seed. FK com CASCADE remove módulos, lições e recursos
            deleted, _ = Course.objects.filter(title__in=seeded_courses).delete()
            self.stdout.write(f'Registros removidos (em cascata): {deleted}')

        self.stdout.write('Criando/atualizando dados de exemplo...')
        
        # Criar curso 1: Python para Iniciantes
        course1, created = Course.objects.update_or_create(
            title='Python para Iniciantes',
            defaults={
                'description': 'Aprenda Python do zero com exemplos práticos e projetos reais.',
                'owner_id': 1,
                'tags': ['python', 'programação', 'iniciantes'],
                'is_published': True,
            },
        )
        self.stdout.write(('Curso criado: ' if created else 'Curso atualizado: ') + course1.title)
        
        # Criar módulo para o curso 1
        module1, created = Module.objects.update_or_create(
            course=course1,
            title='Fundamentos do Python',
            defaults={'order': 1},
        )
        self.stdout.write(('Módulo criado: ' if created else 'Módulo atualizado: ') + module1.title)
        
        # Criar lições para o módulo 1
        lesson1, created = Lesson.objects.update_or_create(
            module=module1,
            title='Introdução ao Python',
            defaults={
                'content': '''# Introdução ao Python

Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.

## Características do Python:
- Sintaxe simples e legível
- Interpretada (não precisa compilar)
- Multiplataforma
- Grande comunidade e bibliotecas

## Primeiro programa:
```python
print("Olá, mundo!")
```

## Variáveis:
```python
nome = "João"
idade = 25
altura = 1.75
```''',
                'content_type': 'markdown',
                'order': 1,
                'resource_links': [
                    {
                        'title': 'Documentação oficial do Python',
                        'url': 'https://docs.python.org/3/'
                    },
                    {
                        'title': 'Tutorial Python.org',
                        'url': 'https://docs.python.org/3/tutorial/'
                    }
                ]
            },
        )
        self.stdout.write(('Lição criada: ' if created else 'Lição atualizada: ') + lesson1.title)
        
        lesson2, created = Lesson.objects.update_or_create(
            module=module1,
            title='Variáveis e Tipos de Dados',
            defaults={
                'content': '''# Variáveis e Tipos de Dados

## Variáveis
Em Python, você não precisa declarar o tipo de uma variável. O Python infere automaticamente.

```python
# Números inteiros
idade = 25
quantidade = 100

# Números decimais
preco = 19.99
altura = 1.75

# Strings (texto)
nome = "Maria"
mensagem = 'Olá, mundo!'

# Booleanos
ativo = True
pausado = False
```

## Tipos de Dados
- **int**: números inteiros
- **float**: números decimais
- **str**: strings (texto)
- **bool**: valores booleanos (True/False)
- **list**: listas
- **dict**: dicionários
- **tuple**: tuplas''',
                'content_type': 'markdown',
                'order': 2,
                'resource_links': [
                    {
                        'title': 'Tipos de dados Python',
                        'url': 'https://docs.python.org/3/library/stdtypes.html'
                    }
                ]
            },
        )
        self.stdout.write(('Lição criada: ' if created else 'Lição atualizada: ') + lesson2.title)
        
        # Criar recursos para o curso 1
        resource1, created = Resource.objects.update_or_create(
            course=course1,
            title='Guia de Instalação do Python',
            defaults={
                'type': 'pdf',
                'url': 'https://example.com/guia-instalacao-python.pdf',
                'metadata': {
                    'pages': 15,
                    'language': 'pt-BR',
                    'author': 'Instrutor Python'
                },
                'tags': ['instalação', 'configuração', 'iniciantes']
            },
        )
        self.stdout.write(('Recurso criado: ' if created else 'Recurso atualizado: ') + resource1.title)
        
        # Criar curso 2: Django Web Development
        course2, created = Course.objects.update_or_create(
            title='Django Web Development',
            defaults={
                'description': 'Desenvolva aplicações web robustas com Django framework.',
                'owner_id': 1,
                'tags': ['django', 'web', 'python', 'backend'],
                'is_published': True
            },
        )
        self.stdout.write(('Curso criado: ' if created else 'Curso atualizado: ') + course2.title)
        
        # Criar módulo para o curso 2
        module2, created = Module.objects.update_or_create(
            course=course2,
            title='Configuração do Django',
            defaults={'order': 1},
        )
        self.stdout.write(('Módulo criado: ' if created else 'Módulo atualizado: ') + module2.title)
        
        # Criar lições para o módulo 2
        lesson3, created = Lesson.objects.update_or_create(
            module=module2,
            title='Instalação e Configuração',
            defaults={
                'content': '''# Instalação e Configuração do Django

## Instalação
```bash
pip install django
```

## Criando um projeto
```bash
django-admin startproject meuprojeto
cd meuprojeto
```

## Estrutura do projeto
```
meuprojeto/
    manage.py
    meuprojeto/
        __init__.py
        settings.py
        urls.py
        wsgi.py
```

## Executando o servidor
```bash
python manage.py runserver
```''',
                'content_type': 'markdown',
                'order': 1,
                'resource_links': [
                    {
                        'title': 'Documentação Django',
                        'url': 'https://docs.djangoproject.com/'
                    }
                ]
            },
        )
        self.stdout.write(('Lição criada: ' if created else 'Lição atualizada: ') + lesson3.title)
        
        lesson4, created = Lesson.objects.update_or_create(
            module=module2,
            title='Models e Database',
            defaults={
                'content': '''# Models e Database

## Criando um Model
```python
from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
```

## Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Admin Interface
```python
from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'ativo']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
```''',
                'content_type': 'markdown',
                'order': 2,
                'resource_links': [
                    {
                        'title': 'Django Models',
                        'url': 'https://docs.djangoproject.com/en/stable/topics/db/models/'
                    }
                ]
            },
        )
        self.stdout.write(('Lição criada: ' if created else 'Lição atualizada: ') + lesson4.title)
        
        # Criar recursos para o curso 2
        resource2, created = Resource.objects.update_or_create(
            course=course2,
            title='Django Cheat Sheet',
            defaults={
                'type': 'pdf',
                'url': 'https://example.com/django-cheat-sheet.pdf',
                'metadata': {
                    'pages': 8,
                    'language': 'en',
                    'author': 'Django Team'
                },
                'tags': ['cheat-sheet', 'referência', 'django']
            },
        )
        self.stdout.write(('Recurso criado: ' if created else 'Recurso atualizado: ') + resource2.title)
        
        resource3, created = Resource.objects.update_or_create(
            course=course2,
            title='Tutorial Django Girls',
            defaults={
                'type': 'link',
                'url': 'https://tutorial.djangogirls.org/',
                'metadata': {
                    'language': 'pt-BR',
                    'difficulty': 'beginner'
                },
                'tags': ['tutorial', 'iniciantes', 'django-girls']
            },
        )
        self.stdout.write(('Recurso criado: ' if created else 'Recurso atualizado: ') + resource3.title)
        
        self.stdout.write(
            self.style.SUCCESS('Seed concluído com sucesso (idempotente). Use --reset para recriar do zero).')
        )
