# 🐳 Setup Docker - Monorepo AVA

Este documento descreve a organização padronizada dos arquivos Docker Compose no monorepo AVA.

## 📁 Estrutura dos Docker Compose

```
AVA-P4/
├── docker-compose.yml              # 🎯 Orquestração completa (raiz)
├── auth_service/
│   └── docker-compose.dev.yml      # 🔧 Desenvolvimento isolado
├── api-gateway/
│   └── docker-compose.dev.yml      # 🔧 Desenvolvimento isolado
├── learning_service/
│   └── docker-compose.dev.yml      # 🔧 Desenvolvimento isolado
├── recommendation_service/
│   └── docker-compose.dev.yml      # 🔧 Desenvolvimento isolado
└── ava-frontend/
    └── docker-compose.dev.yml      # 🔧 Desenvolvimento isolado
```

## 🚀 Como Usar

### 1. **Execução Completa (Recomendado)**
```bash
# Na raiz do projeto
docker compose up --build

# Ou usando o Makefile
make up
```

### 2. **Desenvolvimento Isolado por Serviço**

#### Auth Service
```bash
cd auth_service
docker compose -f docker-compose.dev.yml up --build
# Acesse: http://localhost:8001
```

#### API Gateway
```bash
cd api-gateway
docker compose -f docker-compose.dev.yml up --build
# Acesse: http://localhost:80
```

#### Learning Service
```bash
cd learning_service
docker compose -f docker-compose.dev.yml up --build
# Acesse: http://localhost:8002
```

#### Recommendation Service
```bash
cd recommendation_service
docker compose -f docker-compose.dev.yml up --build
# Acesse: http://localhost:8003
```

#### Frontend Angular
```bash
cd ava-frontend
docker compose -f docker-compose.dev.yml up --build
# Acesse: http://localhost:4200
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente
Cada `docker-compose.dev.yml` usa variáveis de ambiente com valores padrão:

```bash
# Exemplo para auth_service
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
DB_USER=postgres
DB_PASSWORD=postgres
AUTH_DB_NAME=auth_service
```

### Portas Padronizadas
- **Auth Service**: `8001:8000` (interno: 8000)
- **API Gateway**: `80:80`
- **Learning Service**: `8002:8000` (interno: 8000)
- **Recommendation Service**: `8003:8000` (interno: 8000)
- **Frontend**: `4200:80`

### Bancos de Dados
- **Auth DB**: `5433:5432`
- **Learning DB**: `5434:5432`
- **Recommendation DB**: `5435:5432`

## 🌐 Comunicação Entre Serviços

### Desenvolvimento Isolado
Os serviços se comunicam via `host.docker.internal`:
```yaml
environment:
  - AUTH_SERVICE_URL=http://host.docker.internal:8001
  - LEARNING_SERVICE_URL=http://host.docker.internal:8002
```

### Orquestração Completa
Os serviços se comunicam via nomes internos:
```yaml
environment:
  - AUTH_SERVICE_URL=http://auth_service:8000
  - LEARNING_SERVICE_URL=http://learning_service:8000
```

## 📋 Comandos Úteis

### Limpeza
```bash
# Parar todos os containers
docker compose down

# Remover volumes (⚠️ apaga dados)
docker compose down -v

# Limpeza completa
docker system prune -a
```

### Logs
```bash
# Logs de todos os serviços
docker compose logs -f

# Logs de um serviço específico
docker compose logs -f auth_service
```

### Rebuild
```bash
# Rebuild sem cache
docker compose build --no-cache

# Rebuild de um serviço específico
docker compose build --no-cache auth_service
```

## 🔍 Health Checks

Todos os serviços incluem health checks:
- **Auth Service**: `http://localhost:8001/healthz/`
- **API Gateway**: `http://localhost/healthz`
- **Learning Service**: `http://localhost:8002/healthz/`
- **Recommendation Service**: `http://localhost:8003/healthz`
- **Frontend**: `http://localhost:4200/healthz`

## ⚠️ Notas Importantes

1. **Ordem de Inicialização**: Os serviços aguardam os bancos de dados ficarem saudáveis
2. **Volumes**: Cada serviço tem seus próprios volumes para persistência
3. **Networks**: O docker-compose principal cria a rede `ava_net`
4. **Desenvolvimento**: Use `docker-compose.dev.yml` para desenvolvimento isolado
5. **Produção**: Use `docker-compose.yml` da raiz para orquestração completa

## 🐛 Troubleshooting

### Porta já em uso
```bash
# Verificar processos usando a porta
netstat -ano | findstr :8001

# Parar containers conflitantes
docker compose down
```

### Problemas de build
```bash
# Limpar cache do Docker
docker builder prune

# Rebuild forçado
docker compose build --no-cache --pull
```

### Problemas de banco
```bash
# Resetar banco de dados
docker compose down -v
docker compose up --build
```
