# Learning Service - Microserviço de Aprendizado

Microserviço Django REST para gerenciamento de cursos, módulos, lições, matrículas e progresso de aprendizado.

## 🚀 Funcionalidades

### 📚 **Gestão de Conteúdo**
- **Cursos**: Criação, edição e gerenciamento de cursos
- **Módulos**: Organização de conteúdo em módulos
- **Lições**: Conteúdo detalhado com suporte a Markdown/HTML
- **Recursos**: Arquivos, links e materiais complementares

### 👥 **Matrículas e Progresso**
- **Matrículas**: Sistema de inscrição em cursos
- **Progresso**: Acompanhamento de conclusão de lições
- **Interações**: Registro de atividades do usuário
- **Pontuação**: Sistema de avaliação e notas

### 🔐 **Autenticação e Autorização**
- **JWT**: Integração com auth_service
- **Permissões**: Controle de acesso baseado em roles
- **Decoradores**: Utilitários para autenticação

## 🛠️ Tecnologias

- **Django 4.2.7**
- **Django REST Framework 3.14.0**
- **PostgreSQL 15**
- **JWT Authentication**
- **OpenAPI/Swagger**
- **Docker & Docker Compose**

## 📁 Estrutura do Projeto

```
learning_service/
├── apps/
│   ├── common/           # Utilitários e autenticação
│   ├── courses/          # Cursos, módulos e lições
│   ├── enrollments/      # Matrículas
│   ├── resources/        # Recursos de curso
│   ├── progress/         # Progresso e interações
│   └── seeding/          # Seeds e comandos de seed
│       └── management/
│           └── commands/
│               └── seed_data.py  # Comando de seed do Django
├── config/               # Configurações Django
├── Dockerfile            # Imagem do serviço
└── requirements.txt      # Dependências
```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose
- Git

### 1. Clone e Execute

```bash
cd learning_service
docker-compose up --build
```

### 2. Acesse o Serviço

- **API**: http://localhost:8002
- **Admin**: http://localhost:8002/admin
- **Swagger**: http://localhost:8002/learning/docs/
- **ReDoc**: http://localhost:8002/learning/redoc/

### 3. Credenciais Padrão

- **Admin**: `admin` / `admin123`

## 📚 API Endpoints

### 🎓 **Cursos**

#### Listar Cursos
```http
GET /learning/courses/
```

#### Criar Curso
```http
POST /learning/courses/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "title": "Meu Curso",
    "description": "Descrição do curso",
    "tags": ["python", "programação"],
    "is_published": true
}
```

#### Obter Curso Detalhado
```http
GET /learning/courses/{id}/
```

#### Meus Cursos
```http
GET /learning/courses/my_courses/
Authorization: Bearer <jwt_token>
```

### 📖 **Módulos**

#### Listar Módulos
```http
GET /learning/modules/?course={course_id}
```

#### Criar Módulo
```http
POST /learning/modules/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "course": 1,
    "title": "Módulo 1",
    "order": 1
}
```

### 📝 **Lições**

#### Listar Lições
```http
GET /learning/lessons/?module={module_id}
```

#### Criar Lição
```http
POST /learning/lessons/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "module": 1,
    "title": "Lição 1",
    "content": "# Conteúdo em Markdown",
    "content_type": "markdown",
    "order": 1,
    "resource_links": [
        {
            "title": "Link útil",
            "url": "https://example.com"
        }
    ]
}
```

### 📚 **Recursos**

#### Listar Recursos
```http
GET /learning/resources/?course={course_id}
```

#### Criar Recurso
```http
POST /learning/resources/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "course": 1,
    "type": "pdf",
    "title": "Material PDF",
    "url": "https://example.com/material.pdf",
    "tags": ["material", "pdf"]
}
```

### 🎯 **Matrículas**

#### Listar Minhas Matrículas
```http
GET /learning/enrollments/
Authorization: Bearer <jwt_token>
```

#### Matricular em Curso
```http
POST /learning/enrollments/enroll/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "course": 1,
    "role": "student"
}
```

#### Meus Cursos
```http
GET /learning/enrollments/my_courses/
Authorization: Bearer <jwt_token>
```

#### Desmatricular
```http
POST /learning/enrollments/unenroll/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "course_id": 1
}
```

### 📊 **Progresso**

#### Listar Meu Progresso
```http
GET /learning/progress/
Authorization: Bearer <jwt_token>
```

#### Marcar Lição como Concluída
```http
POST /learning/progress/mark_complete/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "lesson_id": 1,
    "score": 85.5,
    "time_spent": 1200
}
```

#### Progresso de uma Lição
```http
GET /learning/progress/lesson_progress/?lesson_id=1
Authorization: Bearer <jwt_token>
```

#### Progresso por Curso
```http
GET /learning/progress/course_progress/?course_id=1
Authorization: Bearer <jwt_token>
```

### 🔄 **Interações**

#### Listar Interações
```http
GET /learning/interactions/
Authorization: Bearer <jwt_token>
```

#### Criar Interação
```http
POST /learning/interactions/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "lesson": 1,
    "interaction_type": "view",
    "payload": {
        "time_spent": 300,
        "completed": false
    }
}
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production

# Database
DB_NAME=learning_service
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Services
AUTH_SERVICE_URL=http://auth_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000
```

### Banco de Dados

O PostgreSQL é configurado automaticamente. Para desenvolvimento local:

```bash
# Acessar o container do banco
docker-compose exec db psql -U postgres -d learning_service

# Executar migrações manualmente
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Executar seed data
docker-compose exec web python manage.py seed_data
```

## 🧪 Dados de Exemplo

O comando `seed_data` cria automaticamente:

- **2 cursos**: Python para Iniciantes e Django Web Development
- **2 módulos**: Um para cada curso
- **4 lições**: Conteúdo em Markdown com exemplos práticos
- **3 recursos**: PDFs e links úteis

### Como executar o seed

Opcional (via Docker Compose na raiz do projeto):

```powershell
# Executa o seed no container do learning_service
docker-compose exec learning_service python manage.py seed_data

# Caso o comando não seja reconhecido (após atualizar o código),
# reconstrua apenas o serviço do learning_service e tente novamente:
docker-compose build learning_service
docker-compose up -d --no-deps learning_service
docker-compose exec learning_service python manage.py seed_data
```

Para recriar do zero (limpa apenas os registros gerados pelo seed):

```powershell
docker-compose exec learning_service python manage.py seed_data --reset
```

## 🔐 Autenticação

### JWT Integration

O serviço integra com o `auth_service` para validação de tokens JWT:

1. **Header Authorization**: `Bearer <token>`
2. **Header X-User-Id**: Passado pelo API Gateway
3. **Validação Local**: Chave HS256 para desenvolvimento
4. **Validação Remota**: JWKS do auth_service para produção

### Permissões

- **Owner**: Pode editar/deletar seus cursos
- **Instructor**: Pode gerenciar conteúdo dos cursos
- **Student**: Pode acessar cursos matriculados
- **Public**: Pode ver cursos publicados

## 📊 Filtros e Busca

### Filtros Disponíveis

- **Cursos**: `owner_id`, `is_published`, `tags`
- **Módulos**: `course`
- **Lições**: `module`, `module__course`, `content_type`
- **Recursos**: `course`, `type`, `tags`
- **Progresso**: `user_id`, `lesson`, `completed`
- **Interações**: `user_id`, `lesson`, `resource`, `interaction_type`

### Busca

- **Cursos**: `title`, `description`, `tags`
- **Lições**: `title`, `content`
- **Recursos**: `title`, `tags`

### Ordenação

Todos os endpoints suportam ordenação por campos relevantes.

## 🚀 Deploy em Produção

### 1. Configurar Variáveis

```bash
DEBUG=False
SECRET_KEY=<chave-segura>
DB_HOST=<host-producao>
AUTH_SERVICE_URL=<url-auth-service>
```

### 2. SSL/TLS

Configure certificados SSL no proxy reverso.

### 3. Backup

Configure backup automático do PostgreSQL.

### 4. Monitoramento

Configure logs centralizados e métricas.

## 🤝 Integração com Outros Serviços

### Auth Service

- Validação de JWT tokens
- Obtenção de informações do usuário
- Controle de permissões

### Recommendation Service

- Envio de eventos de interação
- Endpoint: `/events/interaction`
- Dados: `user_id`, `lesson_id`, `interaction_type`, `payload`

### API Gateway

- Roteamento via `/learning/`
- Pass-through de headers
- Rate limiting e CORS

## 🧪 Testes

```bash
# Executar testes
docker-compose exec web python manage.py test

# Com cobertura
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 📝 Logs

Os logs são salvos em:
- **Console**: Saída padrão dos containers
- **Arquivo**: `logs/django.log`

## 🔧 Troubleshooting

### Problema: Erro de autenticação
- Verifique se o `auth_service` está rodando
- Confirme se o token JWT é válido
- Verifique as configurações de `AUTH_SERVICE_URL`

### Problema: Erro de banco de dados
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais de conexão
- Execute as migrações: `python manage.py migrate`

### Problema: Erro de permissão
- Verifique se o usuário está matriculado no curso
- Confirme se o curso está publicado
- Verifique o role do usuário (student/instructor/owner)
