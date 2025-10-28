# Auth Service - Microserviço de Autenticação Django REST

Este é um microserviço Django REST responsável por autenticação e autorização de usuários, implementado com JWT (JSON Web Tokens) e PostgreSQL.

## 🚀 Funcionalidades

- **Registro de usuários** (`/api/register/`)
- **Login com JWT** (`/api/login/`)
- **Dados do usuário logado** (`/api/user/`)
- **Atualização de perfil** (`/api/user/profile/`)
- **Alteração de senha** (`/api/user/change-password/`)
- **Refresh de tokens** (`/api/token/refresh/`)

## 🛠️ Tecnologias

- **Django 4.2.7**
- **Django REST Framework 3.14.0**
- **djangorestframework-simplejwt 5.3.0**
- **PostgreSQL 15**
- **Docker & Docker Compose**
- **Nginx** (proxy reverso)

## 📁 Estrutura do Projeto

```
auth_service/
├── apps/
│   └── users/
│       ├── models.py          # Modelo User customizado
│       ├── serializers.py     # Serializers para API
│       ├── views.py           # Views da API
│       ├── urls.py            # URLs do app
│       └── admin.py           # Configuração do admin
├── config/
│   ├── settings.py            # Configurações do Django
│   ├── urls.py                # URLs principais
│   ├── wsgi.py                # WSGI
│   └── asgi.py                # ASGI
├── docker-compose.dev.yml     # Orquestração de containers (desenvolvimento)
├── Dockerfile                 # Imagem do serviço
├── nginx.conf                 # Configuração do Nginx
├── requirements.txt           # Dependências Python
└── manage.py                  # Script de gerenciamento
```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Git

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd auth_service
```

### 2. Execute com Docker Compose

```bash
# Construir e executar os containers
docker-compose -f docker-compose.dev.yml up --build

# Ou em background
docker-compose -f docker-compose.dev.yml up -d --build
```

### 3. Acesse o serviço

- **API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

## 📚 Endpoints da API

### Registro de Usuário
```http
POST /api/register/
Content-Type: application/json

{
    "email": "usuario@exemplo.com",
    "username": "usuario",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "password": "senha123",
    "password_confirm": "senha123"
}
```

### Login
```http
POST /api/login/
Content-Type: application/json

{
    "email": "usuario@exemplo.com",
    "password": "senha123"
}
```

**Resposta:**
```json
{
    "message": "Login realizado com sucesso!",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "usuario@exemplo.com",
        "username": "usuario",
        "first_name": "Nome",
        "last_name": "Sobrenome",
        "full_name": "Nome Sobrenome",
        "is_active": true,
        "date_joined": "2024-01-01T12:00:00Z"
    }
}
```

### Dados do Usuário Logado
```http
GET /api/user/
Authorization: Bearer <access_token>
```

### Atualizar Perfil
```http
PUT /api/user/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "Novo Nome",
    "last_name": "Novo Sobrenome"
}
```

### Alterar Senha
```http
POST /api/user/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "old_password": "senha_atual",
    "new_password": "nova_senha123",
    "new_password_confirm": "nova_senha123"
}
```

### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `env.example`:

```bash
cp env.example .env
```

Principais variáveis:
- `DEBUG`: Modo debug (True/False)
- `SECRET_KEY`: Chave secreta do Django
- `DB_*`: Configurações do banco PostgreSQL

### Banco de Dados

O PostgreSQL é configurado automaticamente via Docker Compose. Para desenvolvimento local:

```bash
# Acessar o container do banco
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d auth_service

# Executar migrações
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Criar superusuário
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

## 🧪 Testes

```bash
# Executar testes
docker-compose -f docker-compose.dev.yml exec web python manage.py test

# Com cobertura
docker-compose -f docker-compose.dev.yml exec web coverage run --source='.' manage.py test
docker-compose -f docker-compose.dev.yml exec web coverage report
```

## 📝 Logs

Os logs são salvos em:
- **Console**: Saída padrão dos containers
- **Arquivo**: `logs/django.log` (dentro do container)

## 🔒 Segurança

- Autenticação JWT com tokens de acesso e refresh
- Validação de senhas com critérios de segurança
- CORS configurado para desenvolvimento
- Headers de segurança do Django
- Usuário não-root no container

## 🚀 Deploy em Produção

1. **Altere as variáveis de ambiente**:
   - `DEBUG=False`
   - `SECRET_KEY` segura
   - Configurações de banco de produção

2. **Configure SSL/TLS** no Nginx

3. **Use um banco de dados gerenciado** (RDS, Cloud SQL, etc.)

4. **Configure backup** do banco de dados
