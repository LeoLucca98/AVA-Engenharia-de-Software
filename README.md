# AVA - Adaptive Virtual Assistant

Sistema de microserviços para uma plataforma de aprendizado adaptativo com recomendações inteligentes.

---

## 🏗️ Arquitetura

O AVA é composto por 4 microserviços principais:

- **🔐 Auth Service** – Autenticação e autorização com JWT  
- **📚 Learning Service** – Gestão de cursos, módulos e progresso  
- **🤖 Recommendation Service** – Sistema de recomendações inteligentes  
- **🚪 API Gateway** – Roteamento, CORS, rate limiting e autenticação  

---

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose  
- Make (opcional, mas recomendado)

### 1. Configurar Ambiente

```bash
# Clonar o repositório
git clone <repo-url>
cd AVA-P4

# Configurar variáveis de ambiente
cp env.example .env

# Editar .env se necessário
````

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

---

## 🌐 Acessos

| Serviço                    | URL                                            | Descrição                  |
| -------------------------- | ---------------------------------------------- | -------------------------- |
| **API Gateway**            | [http://localhost:8080](http://localhost:8080) | Ponto de entrada principal |
| **Auth Service**           | [http://localhost:8001](http://localhost:8001) | Autenticação e usuários    |
| **Learning Service**       | [http://localhost:8002](http://localhost:8002) | Cursos e aprendizado       |
| **Recommendation Service** | [http://localhost:8003](http://localhost:8003) | Recomendações              |

### Documentação da API

* **Swagger UI:** [http://localhost:8080/docs/](http://localhost:8080/docs/)
* **ReDoc:** [http://localhost:8080/redoc/](http://localhost:8080/redoc/)
* **Learning API:** [http://localhost:8002/learning/docs/](http://localhost:8002/learning/docs/)

---

## 📁 Estrutura do Projeto

```bash
AVA-P4/
├── api-gateway/              # NGINX API Gateway
├── auth_service/             # Django REST - Autenticação
├── learning_service/         # Django REST - Aprendizado
├── recommendation_service/   # FastAPI - Recomendações
├── docker-compose.yml        # Orquestração completa
├── Makefile                  # Comandos de gerenciamento
├── env.example               # Variáveis de ambiente
└── BOOTSTRAP.md              # Documentação de inicialização
```

---

## 🛠️ Comandos Disponíveis

### **Comandos Principais**

```bash
make up           # Inicia todos os serviços
make down         # Para todos os serviços
make logs         # Mostra logs de todos os serviços
make ps           # Mostra status dos containers
make status       # Status detalhado
make health       # Verifica health checks
```

### **Comandos de Desenvolvimento**

```bash
make build        # Constrói todas as imagens
make dev          # Modo desenvolvimento
make restart      # Reinicia todos os serviços
make clean        # Remove containers e volumes
```

### **Comandos de Manutenção**

```bash
make migrate         # Executa migrações
make seed            # Executa seed data
make createsuperuser # Cria superusuários
make test            # Executa testes
```

### **Comandos de Debug**

```bash
make logs-auth       # Logs do auth service
make logs-learning   # Logs do learning service
make shell-auth      # Shell do auth service
make shell-learning  # Shell do learning service
```

---

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

| Serviço                | Porta Externa | Porta Interna |
| ---------------------- | ------------- | ------------- |
| API Gateway            | 8080          | 80            |
| Auth Service           | 8001          | 8000          |
| Learning Service       | 8002          | 8000          |
| Recommendation Service | 8003          | 8000          |
| Auth DB                | 5433          | 5432          |
| Learning DB            | 5434          | 5432          |
| Recommendation DB      | 5435          | 5432          |

---

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
-d '{ "email": "user@example.com", "password": "senha123" }'

# 3. Usar token nas requisições
curl -X GET http://localhost:8080/learning/courses/ \
-H "Authorization: Bearer <token>"
```

---

## 📚 Funcionalidades

### **Auth Service**

* ✅ Registro e login de usuários
* ✅ JWT tokens (access + refresh)
* ✅ Validação de senhas
* ✅ CORS configurado

### **Learning Service**

* ✅ Gestão de cursos, módulos e lições
* ✅ Sistema de matrículas
* ✅ Acompanhamento de progresso
* ✅ Recursos e interações
* ✅ OpenAPI/Swagger

### **Recommendation Service**

* ✅ Recebimento de eventos de interação
* ✅ Sistema de recomendações
* ✅ API REST com FastAPI

### **API Gateway**

* ✅ Roteamento inteligente
* ✅ CORS configurável
* ✅ Rate limiting (100 req/min)
* ✅ Health checks
* ✅ Pass-through de headers

---

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

---

## 🚀 Deploy em Produção

### **1. Configurar Produção**

```bash
# Editar .env
DEBUG=False
SECRET_KEY=
DB_PASSWORD=
ALLOWED_HOSTS=
ALLOWED_ORIGINS=
```

Ou use o template pronto e ajuste seu domínio:

```bash
cp env.prod.example .env
# Edite .env e defina:
# - SECRET_KEY (valor forte)
# - ALLOWED_HOSTS (domínio público)
# - ALLOWED_ORIGINS / CORS_ALLOWED_ORIGINS (frontend)
```

### **Frontend (Angular)**

* Em build local (docker-compose):
  `src/environments/environment.prod.ts` já aponta para `http://localhost:8080`.
  Não é necessário proxy do Angular.

* Em domínio público:
  altere `apiBaseUrl` para `https://api.seudominio.com` antes do build.

* O container `ava-frontend` serve o build estático com Nginx (`ava-frontend/nginx.conf`).

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
make logs
make status
make health
```

---

## 🔍 Troubleshooting

### **Problemas Comuns**

#### **Serviço não inicia**

```bash
make logs-auth
make logs-learning
make ps
make restart-auth
```

#### **Banco não conecta**

```bash
docker-compose ps | grep _db
docker-compose logs auth_db
docker-compose restart auth_db
```

#### **Migrações falham**

```bash
make migrate
docker-compose exec auth_service python manage.py dbshell
```

---

## 📖 Documentação

* **[BOOTSTRAP.md](BOOTSTRAP.md)** – Ordem de inicialização detalhada
* **[auth_service/README.md](auth_service/README.md)** – Documentação do Auth Service
* **[learning_service/README.md](learning_service/README.md)** – Documentação do Learning Service
* **[api-gateway/README.md](api-gateway/README.md)** – Documentação do API Gateway

---

# AVA - Engenharia de Software

