# 🚀 Guia de Desenvolvimento

Este guia explica como configurar e executar o AVA em ambiente de desenvolvimento local.

## 📋 Pré-requisitos

### Software Necessário

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 18+ (para desenvolvimento frontend)
- **Python**: 3.11+ (para desenvolvimento backend)
- **Git**: 2.30+
- **Make**: 4.0+ (opcional, mas recomendado)

### Verificar Instalação

```bash
# Verificar versões
docker --version
docker-compose --version
node --version
python --version
git --version
make --version
```

## 🏗️ Configuração Inicial

### 1. Clonar Repositório

```bash
git clone <repository-url>
cd AVA-P4
```

### 2. Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar variáveis conforme necessário
nano .env
```

### 3. Configurações Importantes

**Arquivo `.env`:**
```bash
# Desenvolvimento
DEBUG=True
DEVELOPMENT_MODE=True

# URLs dos serviços
AUTH_SERVICE_URL=http://auth_service:8000
LEARNING_SERVICE_URL=http://learning_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000

# CORS
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000

# JWT
JWT_ALGORITHM=RS256
JWT_AUDIENCE=ava-microservices
JWT_ISSUER=ava-auth-service
```

## 🚀 Executando o Projeto

### Opção 1: Docker Compose (Recomendado)

```bash
# Iniciar todos os serviços
make up

# Ou manualmente
docker-compose up -d
```

### Opção 2: Desenvolvimento Individual

#### Auth Service
```bash
cd auth_service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

#### Learning Service
```bash
cd learning_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8002
```

#### Recommendation Service
```bash
cd recommendation_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

#### API Gateway
```bash
cd api-gateway
npm install
npm start
```

#### Frontend
```bash
cd ava-frontend
npm install
npm run dev
```

## 🔧 Comandos de Desenvolvimento

### Comandos Make

```bash
# Gerenciamento de serviços
make up              # Iniciar todos os serviços
make down            # Parar todos os serviços
make restart         # Reiniciar todos os serviços
make logs            # Ver logs de todos os serviços
make logs-auth       # Ver logs do auth service
make logs-learning   # Ver logs do learning service
make logs-rec        # Ver logs do recommendation service
make logs-gateway    # Ver logs do API gateway
make logs-frontend   # Ver logs do frontend

# Verificação de saúde
make health          # Verificar health checks
make ps              # Ver status dos containers

# Desenvolvimento
make migrate         # Executar migrações
make seed            # Executar seed data
make shell-auth      # Shell do auth service
make shell-learning  # Shell do learning service
make shell-rec       # Shell do recommendation service

# Frontend
make frontend-dev    # Servidor de desenvolvimento
make frontend-build  # Build de produção
make frontend-test   # Executar testes
make frontend-lint   # Executar linter

# Manutenção
make clean           # Limpar containers e volumes
make clean-all       # Limpar tudo (cuidado!)
make rebuild         # Rebuild de todos os serviços
```

### Comandos Docker

```bash
# Gerenciamento básico
docker-compose up -d                    # Iniciar em background
docker-compose down                     # Parar serviços
docker-compose restart <service>        # Reiniciar serviço específico
docker-compose logs -f <service>        # Ver logs de serviço específico

# Desenvolvimento
docker-compose exec auth_service python manage.py shell
docker-compose exec learning_service python manage.py shell
docker-compose exec recommendation_service python -c "import main; print('OK')"

# Debugging
docker-compose exec auth_service python manage.py dbshell
docker-compose exec learning_service python manage.py dbshell
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
make test

# Testes específicos
make test-auth
make test-learning
make test-rec
make test-frontend

# Testes com coverage
make test-coverage
```

### Testes Manuais

```bash
# Health checks
curl http://localhost:8080/healthz
curl http://localhost:8001/healthz/
curl http://localhost:8002/learning/
curl http://localhost:8003/health/

# JWKS endpoint
curl http://localhost:8001/api/.well-known/jwks.json

# Login
curl -X POST http://localhost:8080/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

## 📊 Monitoramento

### Logs Estruturados

```bash
# Ver logs em tempo real
docker-compose logs -f

# Filtrar por serviço
docker-compose logs -f auth_service
docker-compose logs -f learning_service

# Logs em JSON
tail -f logs/auth_service.json.log | jq .
```

### Health Checks

```bash
# Verificar status
make health

# Endpoints de saúde
curl http://localhost:8080/healthz
curl http://localhost:8001/healthz/
curl http://localhost:8002/learning/
curl http://localhost:8003/health/
```

## 🔍 Debugging

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :8001
lsof -i :8001

# Parar processo
kill -9 <PID>
```

#### 2. Banco de dados não conecta
```bash
# Verificar containers
docker-compose ps

# Ver logs do banco
docker-compose logs auth_db

# Resetar banco
docker-compose down -v
docker-compose up -d
```

#### 3. JWT não funciona
```bash
# Verificar JWKS
curl http://localhost:8001/api/.well-known/jwks.json

# Verificar logs
docker-compose logs auth_service | grep -i jwt
```

### Debugging Avançado

#### Django Debug
```bash
# Shell interativo
docker-compose exec auth_service python manage.py shell

# Debug SQL
docker-compose exec auth_service python manage.py dbshell

# Verificar configurações
docker-compose exec auth_service python manage.py diffsettings
```

#### FastAPI Debug
```bash
# Logs detalhados
docker-compose exec recommendation_service python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import main
"
```

## 📝 Desenvolvimento de Features

### 1. Nova Feature no Auth Service

```bash
# Criar nova app
docker-compose exec auth_service python manage.py startapp apps/new_feature

# Adicionar ao INSTALLED_APPS
# Criar models, views, serializers
# Executar migrações
docker-compose exec auth_service python manage.py makemigrations
docker-compose exec auth_service python manage.py migrate
```

### 2. Nova Feature no Learning Service

```bash
# Criar nova app
docker-compose exec learning_service python manage.py startapp apps/new_feature

# Seguir mesmo processo do auth service
```

### 3. Nova Feature no Recommendation Service

```bash
# Adicionar endpoint no main.py
# Criar novos models se necessário
# Testar com curl ou Postman
```

### 4. Nova Feature no Frontend

```bash
# Gerar novo componente
cd ava-frontend
ng generate component components/new-feature

# Gerar novo serviço
ng generate service services/new-feature

# Gerar novo módulo
ng generate module modules/new-feature
```

## 🔄 Workflow de Desenvolvimento

### 1. Branch Strategy

```bash
# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Desenvolver
# ... fazer commits ...

# Push e criar PR
git push origin feature/nova-funcionalidade
```

### 2. Code Review

- Verificar se testes passam
- Verificar se documentação está atualizada
- Verificar se logs estão estruturados
- Verificar se health checks funcionam

### 3. Deploy

```bash
# Merge para main
# GitHub Actions executa CI/CD
# Deploy automático para staging
# Testes de integração
# Deploy para produção
```

## 📚 Recursos Úteis

### Documentação das APIs

- **Auth Service**: http://localhost:8001/api/docs/
- **Learning Service**: http://localhost:8002/learning/docs/
- **Recommendation Service**: http://localhost:8003/docs/

### Ferramentas de Desenvolvimento

- **Postman**: Collection em `docs/collections/`
- **Insomnia**: Collection em `docs/collections/`
- **Docker Desktop**: Interface gráfica
- **VS Code**: Extensões recomendadas

### Extensões VS Code

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "bradlc.vscode-tailwindcss",
    "angular.ng-template",
    "ms-vscode.vscode-json"
  ]
}
```

## 🆘 Suporte

### Problemas Comuns

1. **Container não inicia**: Verificar logs com `docker-compose logs <service>`
2. **Banco não conecta**: Verificar se o container do banco está rodando
3. **JWT inválido**: Verificar se o JWKS está acessível
4. **CORS error**: Verificar ALLOWED_ORIGINS no .env

### Contato

- **Slack**: #ava-dev
- **Email**: dev@ava.com
- **Issues**: GitHub Issues
- **Wiki**: Documentação interna

---

**Última atualização**: $(date)
**Versão**: 1.0.0
