# 🏗️ Arquitetura do AVA

Este documento descreve a arquitetura completa do AVA (Adaptive Virtual Assistant), incluindo diagramas, fluxos de dados e decisões arquiteturais.

## 📊 Visão Geral da Arquitetura

### Diagrama de Alto Nível

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Angular Frontend<br/>Port: 4200]
    end
    
    subgraph "API Gateway Layer"
        GW[API Gateway<br/>Node.js/Express<br/>Port: 8080]
    end
    
    subgraph "Microservices Layer"
        AUTH[Auth Service<br/>Django REST<br/>Port: 8001]
        LEARN[Learning Service<br/>Django REST<br/>Port: 8002]
        REC[Recommendation Service<br/>FastAPI<br/>Port: 8003]
    end
    
    subgraph "Database Layer"
        AUTH_DB[(Auth DB<br/>PostgreSQL<br/>Port: 5433)]
        LEARN_DB[(Learning DB<br/>PostgreSQL<br/>Port: 5434)]
        REC_DB[(Recommendation DB<br/>PostgreSQL<br/>Port: 5435)]
    end
    
    subgraph "External Services"
        JWKS[JWKS Endpoint<br/>/.well-known/jwks.json]
    end
    
    FE --> GW
    GW --> AUTH
    GW --> LEARN
    GW --> REC
    AUTH --> AUTH_DB
    LEARN --> LEARN_DB
    REC --> REC_DB
    AUTH --> JWKS
    LEARN --> JWKS
    REC --> JWKS
```

## 🔄 Fluxos Principais

### 1. Fluxo de Autenticação

```mermaid
sequenceDiagram
    participant C as Cliente
    participant GW as API Gateway
    participant AUTH as Auth Service
    participant LEARN as Learning Service
    participant REC as Recommendation Service
    
    C->>AUTH: POST /auth/login
    AUTH->>AUTH: Validar credenciais
    AUTH->>AUTH: Gerar JWT RS256
    AUTH->>C: JWT Token + User Info
    
    C->>GW: Request + JWT Token
    GW->>AUTH: GET /.well-known/jwks.json
    AUTH->>GW: JWKS (Public Key)
    GW->>GW: Validar JWT
    GW->>LEARN: Request + X-User-Id Header
    LEARN->>C: Response
```

### 2. Fluxo de Aprendizado

```mermaid
sequenceDiagram
    participant U as Usuário
    participant FE as Frontend
    participant GW as API Gateway
    participant LEARN as Learning Service
    participant REC as Recommendation Service
    
    U->>FE: Acessar curso
    FE->>GW: GET /learning/courses/
    GW->>LEARN: Request + X-User-Id
    LEARN->>GW: Lista de cursos
    GW->>FE: Response
    
    U->>FE: Iniciar lição
    FE->>GW: POST /learning/progress/mark-complete
    GW->>LEARN: Request + X-User-Id
    LEARN->>LEARN: Marcar progresso
    LEARN->>REC: POST /events/interaction
    REC->>REC: Processar interação
    LEARN->>GW: Progresso atualizado
    GW->>FE: Response
```

### 3. Fluxo de Recomendações

```mermaid
sequenceDiagram
    participant U as Usuário
    participant FE as Frontend
    participant GW as API Gateway
    participant REC as Recommendation Service
    participant LEARN as Learning Service
    
    U->>FE: Solicitar recomendações
    FE->>GW: GET /rec/recommendations/me
    GW->>REC: Request + X-User-Id
    REC->>REC: Analisar perfil do usuário
    REC->>REC: Aplicar algoritmos
    REC->>GW: Lista de recomendações
    GW->>FE: Response
    
    Note over REC: Algoritmos disponíveis:<br/>- Collaborative Filtering<br/>- Content-Based<br/>- Hybrid
```

## 🏛️ Padrões Arquiteturais

### 1. Microservices

**Benefícios:**
- Escalabilidade independente
- Tecnologias heterogêneas
- Deploy independente
- Falhas isoladas

**Desafios:**
- Complexidade de rede
- Consistência de dados
- Monitoramento distribuído

### 2. API Gateway

**Responsabilidades:**
- Roteamento de requisições
- Validação JWT
- Rate limiting
- CORS
- Logging centralizado

### 3. Database per Service

**Cada serviço possui seu próprio banco:**
- **Auth Service**: Usuários, tokens, sessões
- **Learning Service**: Cursos, progresso, matrículas
- **Recommendation Service**: Interações, modelos ML

### 4. Event-Driven Architecture

**Eventos principais:**
- `user.login` - Usuário fez login
- `lesson.completed` - Lição concluída
- `course.enrolled` - Usuário se matriculou
- `interaction.created` - Nova interação

## 🔐 Segurança

### 1. Autenticação JWT RS256

```mermaid
graph LR
    A[Cliente] --> B[API Gateway]
    B --> C[Auth Service]
    C --> D[JWKS Endpoint]
    D --> B
    B --> E[Microservices]
```

**Características:**
- Chaves assimétricas (RSA 2048-bit)
- JWKS público para validação
- Tokens com expiração
- Refresh tokens

### 2. Headers Confiáveis

**Para comunicação interna:**
- `X-User-Id`: ID do usuário
- `X-User-Email`: Email do usuário
- `X-User-Username`: Nome de usuário
- `X-User-Roles`: Roles do usuário

### 3. Rate Limiting

**Limites configurados:**
- Anônimos: 100 req/hora
- Autenticados: 1000 req/hora
- Por IP: 100 req/15min

## 📊 Monitoramento e Observabilidade

### 1. Logging Estruturado

**Formato JSON com:**
- Timestamp ISO 8601
- Correlation ID
- Service name
- User ID
- Request/Response data
- Performance metrics

### 2. Health Checks

**Endpoints de saúde:**
- `/healthz` - Status do serviço
- `/health` - Informações detalhadas
- Health checks no Docker Compose

### 3. Métricas

**Métricas coletadas:**
- Response time
- Request count
- Error rate
- User activity
- Learning progress

## 🚀 Escalabilidade

### 1. Horizontal Scaling

**Estratégias:**
- Load balancer no API Gateway
- Múltiplas instâncias de serviços
- Database sharding (futuro)
- Cache distribuído (Redis)

### 2. Performance

**Otimizações:**
- Connection pooling
- Query optimization
- Caching strategies
- CDN para assets estáticos

## 🔄 CI/CD Pipeline

```mermaid
graph LR
    A[Git Push] --> B[GitHub Actions]
    B --> C[Build Images]
    C --> D[Run Tests]
    D --> E[Security Scan]
    E --> F[Deploy Staging]
    F --> G[Integration Tests]
    G --> H[Deploy Production]
```

## 📈 Roadmap Técnico

### Fase 1 - MVP ✅
- [x] Microservices básicos
- [x] Autenticação JWT
- [x] API Gateway
- [x] Frontend Angular

### Fase 2 - Melhorias 🚧
- [ ] Cache Redis
- [ ] Message Queue (RabbitMQ)
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Logging centralizado (ELK)

### Fase 3 - Avançado 📋
- [ ] Machine Learning pipeline
- [ ] Real-time notifications
- [ ] Mobile app
- [ ] Analytics dashboard

## 🛠️ Tecnologias

### Backend
- **Django REST Framework**: APIs robustas
- **FastAPI**: Performance e async
- **PostgreSQL**: Banco relacional
- **Node.js**: API Gateway

### Frontend
- **Angular**: Framework SPA
- **Angular Material**: UI components
- **RxJS**: Reactive programming

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração local
- **Make**: Automação de tarefas
- **GitHub Actions**: CI/CD

### Monitoramento
- **Structured Logging**: JSON logs
- **Health Checks**: Service monitoring
- **Correlation IDs**: Request tracing

## 📚 Referências

- [Microservices Patterns](https://microservices.io/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.io/docs)
