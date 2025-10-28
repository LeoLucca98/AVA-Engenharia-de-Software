# 📝 Convenções de Desenvolvimento

Este documento define as convenções e padrões de desenvolvimento para o projeto AVA.

## 🌿 Git Branch Strategy

### Estrutura de Branches

```
main
├── develop
├── feature/nova-funcionalidade
├── bugfix/correcao-bug
├── hotfix/correcao-critica
└── release/versao-1.0.0
```

### Tipos de Branch

| Tipo | Prefixo | Descrição | Exemplo |
|------|---------|-----------|---------|
| **Feature** | `feature/` | Nova funcionalidade | `feature/user-profile` |
| **Bugfix** | `bugfix/` | Correção de bug | `bugfix/login-error` |
| **Hotfix** | `hotfix/` | Correção crítica | `hotfix/security-patch` |
| **Release** | `release/` | Preparação de release | `release/v1.2.0` |
| **Chore** | `chore/` | Tarefas de manutenção | `chore/update-deps` |

### Workflow

```mermaid
graph LR
    A[main] --> B[develop]
    B --> C[feature/nova-funcionalidade]
    C --> D[Pull Request]
    D --> B
    B --> E[release/v1.0.0]
    E --> A
    A --> F[hotfix/correcao-critica]
    F --> A
    F --> B
```

## 📝 Convenções de Commit

### Formato de Commit

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(auth): add JWT validation` |
| `fix` | Correção de bug | `fix(api): resolve CORS issue` |
| `docs` | Documentação | `docs(readme): update installation guide` |
| `style` | Formatação | `style(frontend): fix linting errors` |
| `refactor` | Refatoração | `refactor(service): improve error handling` |
| `test` | Testes | `test(auth): add unit tests for login` |
| `chore` | Manutenção | `chore(deps): update dependencies` |
| `perf` | Performance | `perf(api): optimize database queries` |
| `ci` | CI/CD | `ci(github): add automated tests` |
| `build` | Build | `build(docker): update base images` |

### Escopos

| Escopo | Descrição |
|--------|-----------|
| `auth` | Auth Service |
| `learning` | Learning Service |
| `rec` | Recommendation Service |
| `gateway` | API Gateway |
| `frontend` | Angular Frontend |
| `docs` | Documentação |
| `deps` | Dependências |
| `ci` | CI/CD |
| `docker` | Docker |

### Exemplos

```bash
# Feature
feat(auth): add password reset functionality

# Bug fix
fix(learning): resolve course enrollment validation

# Documentation
docs(api): add OpenAPI specifications

# Refactoring
refactor(gateway): improve JWT validation logic

# Test
test(rec): add integration tests for recommendations

# Chore
chore(deps): update Django to 4.2.7
```

### Regras

1. **Primeira linha**: máximo 50 caracteres
2. **Corpo**: máximo 72 caracteres por linha
3. **Usar imperativo**: "add" não "added" ou "adds"
4. **Não terminar com ponto**
5. **Usar inglês** para commits
6. **Referenciar issues**: `Closes #123`

## 🏗️ Convenções de Código

### Python (Django/FastAPI)

#### Nomenclatura

```python
# Classes: PascalCase
class UserProfileView(APIView):
    pass

# Funções e variáveis: snake_case
def get_user_profile(user_id):
    user_data = {}
    return user_data

# Constantes: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Arquivos e módulos: snake_case
user_views.py
auth_helpers.py
```

#### Estrutura de Arquivos

```
service/
├── apps/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── utils.py
│   └── feature/
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       └── tests.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### Imports

```python
# Ordem dos imports
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
from django.db import models
from rest_framework import serializers
import requests

# 3. Local imports
from apps.common.models import BaseModel
from apps.users.serializers import UserSerializer
```

### TypeScript/JavaScript (Angular)

#### Nomenclatura

```typescript
// Classes: PascalCase
export class UserService {
  private userData: UserData;
  
  // Métodos: camelCase
  public getUserProfile(userId: string): Observable<User> {
    return this.http.get<User>(`/api/users/${userId}`);
  }
}

// Interfaces: PascalCase
export interface UserData {
  id: string;
  email: string;
  username: string;
}

// Constantes: UPPER_SNAKE_CASE
export const API_BASE_URL = 'http://localhost:8080';
export const MAX_RETRY_ATTEMPTS = 3;

// Arquivos: kebab-case
user.service.ts
auth.guard.ts
user-profile.component.ts
```

#### Estrutura de Arquivos

```
src/
├── app/
│   ├── core/
│   │   ├── services/
│   │   ├── guards/
│   │   └── interceptors/
│   ├── shared/
│   │   ├── components/
│   │   ├── models/
│   │   └── utils/
│   ├── features/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── courses/
│   └── app.component.ts
├── assets/
├── environments/
└── styles/
```

### Docker

#### Dockerfile

```dockerfile
# Use multi-stage builds
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine as production
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY . .
EXPOSE 8000
CMD ["npm", "start"]
```

#### Nomenclatura

```yaml
# docker-compose.yml
services:
  # Nomes: kebab-case
  auth-service:
    build:
      context: ./auth_service
      dockerfile: Dockerfile
    container_name: ava-auth-service
    ports:
      - "8001:8000"
```

## 📊 Convenções de API

### REST Endpoints

#### Nomenclatura

```bash
# URLs: kebab-case
GET /api/users
GET /api/user-profiles
POST /api/course-enrollments

# Parâmetros: snake_case
GET /api/courses?is_published=true&owner_id=123

# Headers: kebab-case
Authorization: Bearer <token>
X-Request-ID: <uuid>
X-User-ID: 123
```

#### Response Format

```json
{
  "data": {
    "id": 1,
    "title": "Python Course",
    "description": "Learn Python programming"
  },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  },
  "links": {
    "self": "/api/courses/1",
    "next": "/api/courses?page=2"
  }
}
```

#### Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required"],
      "password": ["Password too short"]
    }
  },
  "request_id": "req_123456789"
}
```

### Status Codes

| Código | Descrição | Uso |
|--------|-----------|-----|
| 200 | OK | Sucesso |
| 201 | Created | Recurso criado |
| 400 | Bad Request | Dados inválidos |
| 401 | Unauthorized | Não autenticado |
| 403 | Forbidden | Sem permissão |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Validação falhou |
| 500 | Internal Server Error | Erro do servidor |

## 🧪 Convenções de Testes

### Estrutura de Testes

```python
# test_<module>.py
import pytest
from django.test import TestCase
from rest_framework.test import APITestCase

class TestUserModel(TestCase):
    """Testes para o modelo User."""
    
    def setUp(self):
        """Configuração inicial."""
        self.user = User.objects.create(
            email='test@example.com',
            username='testuser'
        )
    
    def test_user_creation(self):
        """Testa criação de usuário."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
    
    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        self.assertEqual(str(self.user), 'test@example.com')
```

### Nomenclatura de Testes

```python
# Métodos: test_<action>_<condition>
def test_create_user_with_valid_data(self):
    pass

def test_create_user_with_invalid_email(self):
    pass

def test_update_user_profile(self):
    pass

def test_delete_user_account(self):
    pass
```

### Cobertura de Testes

```bash
# Mínimo: 80% de cobertura
# Ideal: 90%+ de cobertura

# Comandos
make test-coverage
pytest --cov=. --cov-report=html
```

## 📚 Convenções de Documentação

### README

```markdown
# Nome do Projeto

Breve descrição do projeto.

## 🚀 Instalação

```bash
# Comandos de instalação
```

## 📖 Uso

```bash
# Exemplos de uso
```

## 🧪 Testes

```bash
# Como executar testes
```

## 📝 Licença

MIT License
```

### Docstrings

```python
def calculate_user_score(user_id: int, course_id: int) -> float:
    """
    Calcula a pontuação do usuário em um curso.
    
    Args:
        user_id (int): ID do usuário
        course_id (int): ID do curso
        
    Returns:
        float: Pontuação do usuário (0.0 a 1.0)
        
    Raises:
        UserNotFound: Se o usuário não existir
        CourseNotFound: Se o curso não existir
        
    Example:
        >>> score = calculate_user_score(123, 456)
        >>> print(f"Score: {score:.2f}")
        Score: 0.85
    """
    pass
```

### Comentários

```python
# Comentários explicam o "porquê", não o "o que"
# BOM: Calcula a média ponderada considerando a dificuldade
score = (easy_score * 0.3) + (hard_score * 0.7)

# RUIM: Soma os scores
score = easy_score + hard_score
```

## 🔧 Convenções de Configuração

### Environment Variables

```bash
# Nomenclatura: UPPER_SNAKE_CASE
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
API_BASE_URL=http://localhost:8080

# Agrupamento por serviço
# Auth Service
AUTH_JWT_SECRET=...
AUTH_JWT_EXPIRY=3600

# Learning Service
LEARNING_DB_HOST=localhost
LEARNING_DB_PORT=5432

# Recommendation Service
REC_ALGORITHM=collaborative_filtering
REC_CACHE_TTL=300
```

### Docker Compose

```yaml
# Ordem dos serviços
version: '3.8'

services:
  # 1. Databases
  auth_db:
    image: postgres:15
    
  # 2. Services
  auth_service:
    build: ./auth_service
    depends_on:
      - auth_db
      
  # 3. Gateway
  api_gateway:
    build: ./api-gateway
    depends_on:
      - auth_service
      - learning_service
      
  # 4. Frontend
  frontend:
    build: ./ava-frontend
    depends_on:
      - api_gateway
```

## 📋 Checklist de Code Review

### Funcionalidade
- [ ] Código funciona conforme especificado
- [ ] Testes passam
- [ ] Não quebra funcionalidades existentes
- [ ] Performance adequada

### Código
- [ ] Segue convenções de nomenclatura
- [ ] Código limpo e legível
- [ ] Sem código duplicado
- [ ] Tratamento de erros adequado

### Segurança
- [ ] Não expõe informações sensíveis
- [ ] Validação de entrada
- [ ] Autenticação/autorização adequada
- [ ] Logs de segurança

### Documentação
- [ ] README atualizado
- [ ] Docstrings em funções/métodos
- [ ] Comentários explicativos
- [ ] Changelog atualizado

## 🚀 Release Process

### Versionamento

```bash
# Semantic Versioning: MAJOR.MINOR.PATCH
# MAJOR: Breaking changes
# MINOR: New features (backward compatible)
# PATCH: Bug fixes (backward compatible)

# Exemplos
1.0.0  # Primeira versão estável
1.1.0  # Nova funcionalidade
1.1.1  # Correção de bug
2.0.0  # Breaking change
```

### Changelog

```markdown
# Changelog

## [1.1.0] - 2024-01-15

### Added
- Nova funcionalidade de recomendações
- Suporte a múltiplos idiomas

### Changed
- Melhorada performance da API
- Atualizada interface do usuário

### Fixed
- Correção de bug no login
- Resolvido problema de CORS

### Security
- Atualizada versão do Django
- Melhorada validação de JWT
```


### Recursos

- **Style Guide**: `/docs/style-guide/`
- **API Documentation**: `/docs/api/`
- **Architecture**: `/docs/architecture.md`

---

**Última atualização**: 
**Versão**: 1.0.0
