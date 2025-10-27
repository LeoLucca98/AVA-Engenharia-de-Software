# AVA - Adaptive Virtual Assistant

Sistema de microserviços para uma plataforma de aprendizado adaptativo com recomendações inteligentes.

## 🏗️ Arquitetura

O AVA é composto por 4 microserviços principais:

- **🔐 Auth Service** - Autenticação e autorização com JWT
- **📚 Learning Service** - Gestão de cursos, módulos e progresso
- **🤖 Recommendation Service** - Sistema de recomendações inteligentes
- **🚪 API Gateway** - Roteamento, CORS, rate limiting e autenticação

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Make (opcional, mas recomendado)

### 1. Configurar Ambiente

```bash
# Clonar o repositório
git clone <repository-url>
cd AVA-P4

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env se necessário
```

### 2. Iniciar Serviços

```bash
# Usando Make (recomendado)
make up

# Ou usando Docker Compose diretamente
docker-compose up -d
```

### 3. Executar Bootstrap

```bash
# Executar migrações e seed data
make migrate
make seed
make createsuperuser
```

### 4. Verificar Status

```bash
# Verificar se todos os serviços estão rodando
make status

# Verificar health checks
make health
```

## 🌐 Acessos

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **API Gateway** | http://localhost:8080 | Ponto de entrada principal |
| **Auth Service** | http://localhost:8001 | Autenticação e usuários |
| **Learning Service** | http://localhost:8002 | Cursos e aprendizado |
| **Recommendation Service** | http://localhost:8003 | Recomendações |

### Documentação da API

- **Swagger UI**: http://localhost:8080/docs/
- **ReDoc**: http://localhost:8080/redoc/
- **Learning API**: http://localhost:8002/learning/docs/

## 📁 Estrutura do Projeto

```
AVA-P4/
├── api-gateway/           # NGINX API Gateway
├── auth_service/          # Django REST - Autenticação
├── learning_service/      # Django REST - Aprendizado
├── recommendation_service/ # FastAPI - Recomendações
├── docker-compose.yml     # Orquestração completa
├── Makefile              # Comandos de gerenciamento
├── env.example           # Variáveis de ambiente
└── BOOTSTRAP.md          # Documentação de inicialização
```

## 🛠️ Comandos Disponíveis

### **Comandos Principais**

```bash
make up          # Inicia todos os serviços
make down        # Para todos os serviços
make logs        # Mostra logs de todos os serviços
make ps          # Mostra status dos containers
make status      # Status detalhado
make health      # Verifica health checks
```

### **Comandos de Desenvolvimento**

```bash
make build       # Constrói todas as imagens
make dev         # Modo desenvolvimento
make restart     # Reinicia todos os serviços
make clean       # Remove containers e volumes
```

### **Comandos de Manutenção**

```bash
make migrate     # Executa migrações
make seed        # Executa seed data
make createsuperuser # Cria superusuários
make test        # Executa testes
```

### **Comandos de Debug**

```bash
make logs-auth   # Logs do auth service
make logs-learning # Logs do learning service
make shell-auth  # Shell do auth service
make shell-learning # Shell do learning service
```

## 🔧 Configuração

### **Variáveis de Ambiente**

O arquivo `.env` contém todas as configurações:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production

# Database
DB_USER=postgres
DB_PASSWORD=postgres

# Services
AUTH_SERVICE_URL=http://auth_service:8000
LEARNING_SERVICE_URL=http://learning_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000

# CORS
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000
```

### **Portas**

| Serviço | Porta Externa | Porta Interna |
|---------|---------------|---------------|
| API Gateway | 8080 | 80 |
| Auth Service | 8001 | 8000 |
| Learning Service | 8002 | 8000 |
| Recommendation Service | 8003 | 8000 |
| Auth DB | 5433 | 5432 |
| Learning DB | 5434 | 5432 |
| Recommendation DB | 5435 | 5432 |

## 🔐 Autenticação

### **Fluxo de Autenticação**

1. **Registro/Login** via Auth Service
2. **JWT Token** retornado
3. **Validação** no API Gateway
4. **Pass-through** para microserviços

### **Exemplo de Uso**

```bash
# 1. Registrar usuário
curl -X POST http://localhost:8080/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "password": "senha123",
    "password_confirm": "senha123"
  }'

# 2. Fazer login
curl -X POST http://localhost:8080/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "senha123"
  }'

# 3. Usar token nas requisições
curl -X GET http://localhost:8080/learning/courses/ \
  -H "Authorization: Bearer <jwt_token>"
```

## 📚 Funcionalidades

### **Auth Service**
- ✅ Registro e login de usuários
- ✅ JWT tokens (access + refresh)
- ✅ Validação de senhas
- ✅ CORS configurado

### **Learning Service**
- ✅ Gestão de cursos, módulos e lições
- ✅ Sistema de matrículas
- ✅ Acompanhamento de progresso
- ✅ Recursos e interações
- ✅ OpenAPI/Swagger

### **Recommendation Service**
- ✅ Recebimento de eventos de interação
- ✅ Sistema de recomendações
- ✅ API REST com FastAPI

### **API Gateway**
- ✅ Roteamento inteligente
- ✅ CORS configurável
- ✅ Rate limiting (100 req/min)
- ✅ Health checks
- ✅ Pass-through de headers

## 🧪 Testes

### **Executar Testes**

```bash
# Todos os serviços
make test

# Serviço específico
docker-compose exec auth_service python manage.py test
docker-compose exec learning_service python manage.py test
```

### **Testar APIs**

```bash
# Health checks
make health

# Testar endpoints
curl http://localhost:8080/healthz
curl http://localhost:8080/auth/login/
curl http://localhost:8080/learning/courses/
curl http://localhost:8080/rec/recommendations/
```

## 🚀 Deploy em Produção

### **1. Configurar Produção**

```bash
# Editar .env
DEBUG=False
SECRET_KEY=<chave-segura>
DB_PASSWORD=<senha-segura>
ALLOWED_HOSTS=<domínios>
ALLOWED_ORIGINS=<origins>
```

Ou use o template pronto e ajuste seu domínio:

```bash
cp env.prod.example .env
# Edite .env e defina:
# - SECRET_KEY (valor forte)
# - ALLOWED_HOSTS (inclua o domínio público do gateway)
# - ALLOWED_ORIGINS e CORS_ALLOWED_ORIGINS (inclua o domínio público do frontend)
```

Frontend (Angular)
- Em build de produção local (docker-compose): `src/environments/environment.prod.ts` já aponta para `http://localhost:8080` (API Gateway). Não é necessário proxy do Angular.
- Em domínio público: altere `apiBaseUrl` para `https://api.seudominio.com` (ou o domínio do seu gateway) antes do build.
- O container `ava-frontend` serve o build estático com Nginx (arquivo `ava-frontend/nginx.conf`).

### **2. Deploy**

```bash
# Build sem cache
make build-no-cache

# Iniciar em produção
make prod

# Verificar health
make health
```

### **3. Monitoramento**

```bash
# Logs em tempo real
make logs

# Status dos serviços
make status

# Health checks
make health
```

## 🔍 Troubleshooting

### **Problemas Comuns**

#### **Serviço não inicia**
```bash
# Verificar logs
make logs-auth
make logs-learning

# Verificar status
make ps

# Reiniciar serviço
make restart-auth
```

#### **Banco não conecta**
```bash
# Verificar se o banco está rodando
docker-compose ps | grep _db

# Verificar logs do banco
docker-compose logs auth_db

# Reiniciar banco
docker-compose restart auth_db
```

#### **Migrações falham**
```bash
# Executar migrações manualmente
make migrate

# Verificar conexão
docker-compose exec auth_service python manage.py dbshell
```

### **Comandos de Debug**

```bash
# Acessar shell dos serviços
make shell-auth
make shell-learning

# Verificar logs específicos
make logs-auth
make logs-learning
make logs-gateway

# Status detalhado
make status
```

## 📖 Documentação

- **[BOOTSTRAP.md](BOOTSTRAP.md)** - Ordem de inicialização detalhada
- **[auth_service/README.md](auth_service/README.md)** - Documentação do Auth Service
- **[learning_service/README.md](learning_service/README.md)** - Documentação do Learning Service
- **[api-gateway/README.md](api-gateway/README.md)** - Documentação do API Gateway

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

1. Verifique a documentação
2. Consulte o [BOOTSTRAP.md](BOOTSTRAP.md) para problemas de inicialização
3. Execute `make help` para ver todos os comandos disponíveis
4. Abra uma issue no repositório
#   A V A - E n g e n h a r i a - d e - S o f t w a r e 
 
 