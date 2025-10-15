# AVA Microservices - Ordem de Bootstrap

Este documento descreve a ordem de inicialização e configuração dos microserviços do AVA.

## 🚀 Inicialização Rápida

```bash
# 1. Configurar variáveis de ambiente
cp env.example .env

# 2. Iniciar todos os serviços
make up

# 3. Executar migrações e seed data
make migrate
make seed
make createsuperuser
```

## 📋 Ordem de Bootstrap Detalhada

### 1. **Preparação do Ambiente**

```bash
# Copiar arquivo de configuração
cp env.example .env

# Editar variáveis se necessário
nano .env
```

### 2. **Inicialização dos Bancos de Dados**

Os bancos PostgreSQL são iniciados primeiro com health checks:

```bash
# Bancos são iniciados automaticamente com:
# - auth_db (porta 5433)
# - learning_db (porta 5434) 
# - recommendation_db (porta 5435)
```

**Health Check dos Bancos:**
- Verifica se o PostgreSQL está pronto
- Testa conexão com o banco específico
- Aguarda até 5 tentativas com 10s de intervalo

### 3. **Inicialização dos Microserviços**

Ordem de dependência:

#### 3.1 **Auth Service** (Primeiro)
```bash
# Depende de: auth_db
# Porta: 8001 (interno: 8000)
# Health check: /healthz/
```

**Bootstrap do Auth Service:**
```bash
# 1. Migrações
docker-compose exec auth_service python manage.py migrate

# 2. Criar superusuário
docker-compose exec auth_service python manage.py createsuperuser

# 3. Seed data (se necessário)
docker-compose exec auth_service python manage.py seed_data
```

#### 3.2 **Learning Service** (Segundo)
```bash
# Depende de: learning_db
# Porta: 8002 (interno: 8000)
# Health check: /learning/
```

**Bootstrap do Learning Service:**
```bash
# 1. Migrações
docker-compose exec learning_service python manage.py migrate

# 2. Criar superusuário
docker-compose exec learning_service python manage.py createsuperuser

# 3. Seed data (cursos, módulos, lições)
docker-compose exec learning_service python manage.py seed_data
```

#### 3.3 **Recommendation Service** (Terceiro)
```bash
# Depende de: recommendation_db
# Porta: 8003 (interno: 8000)
# Health check: /health/
```

**Bootstrap do Recommendation Service:**
```bash
# 1. Migrações (se aplicável)
docker-compose exec recommendation_service python manage.py migrate

# 2. Seed data (se necessário)
docker-compose exec recommendation_service python manage.py seed_data
```

#### 3.4 **API Gateway** (Último)
```bash
# Depende de: auth_service, learning_service, recommendation_service
# Porta: 8080 (interno: 80)
# Health check: /healthz
```

**Bootstrap do API Gateway:**
- Inicia automaticamente após todos os serviços estarem saudáveis
- Configura roteamento para os microserviços
- Aplica configurações de CORS e rate limiting

## 🔧 Comandos de Bootstrap

### **Comandos Automáticos (Makefile)**

```bash
# Iniciar todos os serviços
make up

# Executar migrações em todos os serviços Django
make migrate

# Criar superusuários
make createsuperuser

# Executar seed data
make seed

# Verificar status
make status

# Verificar health
make health
```

### **Comandos Manuais**

```bash
# 1. Iniciar apenas os bancos
docker-compose up -d auth_db learning_db recommendation_db

# 2. Aguardar bancos ficarem saudáveis
docker-compose ps

# 3. Iniciar serviços um por vez
docker-compose up -d auth_service
docker-compose up -d learning_service
docker-compose up -d recommendation_service
docker-compose up -d api-gateway

# 4. Executar migrações
docker-compose exec auth_service python manage.py migrate
docker-compose exec learning_service python manage.py migrate

# 5. Criar superusuários
docker-compose exec auth_service python manage.py createsuperuser
docker-compose exec learning_service python manage.py createsuperuser

# 6. Executar seed data
docker-compose exec learning_service python manage.py seed_data
```

## 🏥 Health Checks

### **Bancos de Dados**
```bash
# Verificar se os bancos estão prontos
docker-compose exec auth_db pg_isready -U postgres -d auth_service
docker-compose exec learning_db pg_isready -U postgres -d learning_service
docker-compose exec recommendation_db pg_isready -U postgres -d recommendation_service
```

### **Microserviços**
```bash
# Auth Service
curl http://localhost:8001/healthz/

# Learning Service
curl http://localhost:8002/learning/

# Recommendation Service
curl http://localhost:8003/health/

# API Gateway
curl http://localhost:8080/healthz
```

## 🔍 Troubleshooting

### **Problema: Serviço não inicia**
```bash
# Verificar logs
make logs-auth
make logs-learning
make logs-recommendation
make logs-gateway

# Verificar status
make ps

# Reiniciar serviço específico
make restart-auth
```

### **Problema: Banco não conecta**
```bash
# Verificar se o banco está rodando
docker-compose ps | grep _db

# Verificar logs do banco
docker-compose logs auth_db
docker-compose logs learning_db
docker-compose logs recommendation_db

# Reiniciar banco
docker-compose restart auth_db
```

### **Problema: Migrações falham**
```bash
# Verificar conexão com banco
docker-compose exec auth_service python manage.py dbshell

# Executar migrações manualmente
docker-compose exec auth_service python manage.py migrate --verbosity=2

# Resetar migrações (cuidado!)
docker-compose exec auth_service python manage.py migrate --fake-initial
```

### **Problema: Seed data falha**
```bash
# Executar seed manualmente
docker-compose exec learning_service python manage.py shell
>>> from management.commands.seed_data import Command
>>> Command().handle()

# Verificar dados
docker-compose exec learning_service python manage.py shell
>>> from apps.courses.models import Course
>>> Course.objects.count()
```

## 📊 Monitoramento

### **Status dos Serviços**
```bash
# Status geral
make status

# Health checks
make health

# Logs em tempo real
make logs
```

### **Métricas Importantes**
- **Tempo de inicialização**: ~2-3 minutos para todos os serviços
- **Health check interval**: 30s
- **Retry attempts**: 3
- **Start period**: 60s para serviços, 40s para gateway

## 🚀 Produção

### **Configurações de Produção**
```bash
# Editar .env para produção
DEBUG=False
SECRET_KEY=<chave-segura>
DB_PASSWORD=<senha-segura>
ALLOWED_HOSTS=<domínios-produção>
ALLOWED_ORIGINS=<origins-produção>
```

### **Deploy**
```bash
# Build sem cache
make build-no-cache

# Iniciar em produção
make prod

# Verificar health
make health
```

## 📝 Logs e Debugging

### **Localização dos Logs**
- **Console**: `docker-compose logs`
- **Arquivos**: `logs/django.log` (dentro dos containers)
- **Sistema**: `journalctl -u docker` (se usando systemd)

### **Níveis de Log**
- **DEBUG**: Desenvolvimento
- **INFO**: Produção
- **ERROR**: Apenas erros

### **Comandos Úteis**
```bash
# Logs de todos os serviços
make logs

# Logs de serviço específico
make logs-auth
make logs-learning

# Logs com timestamps
docker-compose logs -t

# Logs das últimas 100 linhas
docker-compose logs --tail=100
```
