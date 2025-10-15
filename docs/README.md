# AVA - Documentação Completa

Bem-vindo à documentação completa do AVA (Adaptive Virtual Assistant) - uma plataforma de microserviços para aprendizado adaptativo com recomendações inteligentes.

## 📚 Índice

- [🏗️ Arquitetura](architecture.md) - Diagramas e fluxos do sistema
- [🚀 Guia de Desenvolvimento](development.md) - Como rodar localmente
- [🌐 Guia de Deploy](deployment.md) - Deploy em produção
- [📝 Convenções](conventions.md) - Padrões de commit e branch
- [🔐 Autenticação](authentication.md) - Fluxo de autenticação JWT
- [📊 APIs](apis.md) - Documentação das APIs
- [🧪 Testes](testing.md) - Guia de testes
- [🔧 Troubleshooting](troubleshooting.md) - Solução de problemas

## 🎯 Visão Geral

O AVA é composto por 4 microserviços principais:

| Serviço | Tecnologia | Porta | Descrição |
|---------|------------|-------|-----------|
| **API Gateway** | Node.js/Express | 8080 | Roteamento e validação JWT |
| **Auth Service** | Django REST | 8001 | Autenticação e autorização |
| **Learning Service** | Django REST | 8002 | Cursos e progresso |
| **Recommendation Service** | FastAPI | 8003 | Recomendações inteligentes |
| **Frontend** | Angular | 4200 | Interface do usuário |

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento)
- Python 3.11+ (para desenvolvimento)
- Make (opcional)

### Instalação

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd AVA-P4

# 2. Configurar ambiente
cp env.example .env

# 3. Iniciar serviços
make up

# 4. Verificar status
make health
```

### Acessos

- **Frontend**: http://localhost:4200
- **API Gateway**: http://localhost:8080
- **Auth Service**: http://localhost:8001
- **Learning Service**: http://localhost:8002
- **Recommendation Service**: http://localhost:8003

### Documentação das APIs

- **Auth Service**: http://localhost:8001/api/docs/
- **Learning Service**: http://localhost:8002/learning/docs/
- **Recommendation Service**: http://localhost:8003/docs/

## 📋 Comandos Úteis

```bash
# Desenvolvimento
make up          # Iniciar todos os serviços
make down        # Parar todos os serviços
make logs        # Ver logs de todos os serviços
make health      # Verificar health checks

# Frontend
make frontend-dev    # Servidor de desenvolvimento
make frontend-build  # Build de produção

# Manutenção
make migrate     # Executar migrações
make seed        # Executar seed data
make clean       # Limpar containers
```

## 🔗 Links Importantes

- [Postman Collection](collections/AVA-API.postman_collection.json)
- [Insomnia Collection](collections/AVA-API.json)
- [Diagramas de Arquitetura](architecture.md#diagramas)
- [Fluxo de Autenticação](authentication.md#fluxo)

## 📞 Suporte

Para dúvidas e suporte:

1. Consulte a documentação específica
2. Verifique o [Troubleshooting](troubleshooting.md)
3. Abra uma issue no repositório
4. Entre em contato com a equipe de desenvolvimento

---

**Última atualização**: $(date)
**Versão**: 1.0.0
