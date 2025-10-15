# API Gateway - AVA Microservices

API Gateway usando NGINX para rotear requisições para os microserviços do AVA (Adaptive Virtual Assistant).

## 🚀 Funcionalidades

- **Roteamento inteligente** para microserviços
- **CORS configurável** via variáveis de ambiente
- **Rate limiting** por IP (100 req/min por serviço)
- **Compressão Gzip** para otimização
- **Pass-through de headers** importantes
- **Health check** integrado
- **Timeouts sensatos** para todas as requisições
- **Headers de segurança** configurados

## 🛠️ Tecnologias

- **NGINX 1.25 Alpine**
- **Docker & Docker Compose**
- **Environment templating** com envsubst

## 📁 Estrutura do Projeto

```
api-gateway/
├── nginx.conf.template    # Template de configuração NGINX
├── Dockerfile            # Imagem Alpine do NGINX
├── docker-entrypoint.sh  # Script de inicialização
├── docker-compose.yml    # Orquestração completa
├── env.example          # Exemplo de variáveis
└── README.md            # Esta documentação
```

## 🛣️ Rotas Configuradas

| Rota | Destino | Serviço |
|------|---------|---------|
| `/auth/` | `auth_service:8000` | Django REST |
| `/learning/` | `learning_service:8000` | Django REST |
| `/rec/` | `recommendation_service:8000` | FastAPI |
| `/healthz` | - | Health Check |

## 🔧 Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo:
```bash
cp env.example .env
```

Principais variáveis:
```bash
# CORS - Origins permitidos (separados por vírgula)
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000

# URLs dos microserviços
AUTH_SERVICE_URL=http://auth_service:8000
LEARNING_SERVICE_URL=http://learning_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000
```

### 2. Executar o Gateway

```bash
# Construir e executar
docker-compose up --build

# Em background
docker-compose up -d --build
```

### 3. Verificar Health Check

```bash
curl http://localhost/healthz
# Resposta: OK
```

## 📊 Rate Limiting

Cada serviço tem rate limiting configurado:
- **Limite**: 100 requisições por minuto por IP
- **Burst**: 20 requisições extras permitidas
- **Zonas separadas** para cada serviço

## 🔒 CORS

Configuração automática de CORS:
- **Origins configuráveis** via `ALLOWED_ORIGINS`
- **Métodos permitidos**: GET, POST, PUT, DELETE, OPTIONS
- **Headers permitidos**: Authorization, Content-Type, X-Request-Id, X-User-Id
- **Credentials**: Habilitado

## 📡 Pass-through de Headers

Os seguintes headers são automaticamente repassados:
- `Authorization` - Para autenticação JWT
- `X-Request-Id` - Para rastreamento de requisições
- `X-User-Id` - Para identificação do usuário

## ⏱️ Timeouts

Configurações de timeout sensatas:
- **Connect**: 30s
- **Send**: 30s
- **Read**: 30s

## 🏥 Health Check

Endpoint de health check disponível em:
```
GET /healthz
```

Resposta:
```
200 OK
```

## 🐳 Docker

### Build da Imagem
```bash
docker build -t api-gateway .
```

### Executar Container
```bash
docker run -p 80:80 \
  -e ALLOWED_ORIGINS="http://localhost:4200" \
  -e AUTH_SERVICE_URL="http://auth_service:8000" \
  -e LEARNING_SERVICE_URL="http://learning_service:8000" \
  -e RECOMMENDATION_SERVICE_URL="http://recommendation_service:8000" \
  api-gateway
```

## 🔍 Logs e Debugging

### Ver logs do gateway
```bash
docker-compose logs -f api-gateway
```

### Testar configuração NGINX
```bash
docker-compose exec api-gateway nginx -t
```

### Acessar container
```bash
docker-compose exec api-gateway sh
```

## 📝 Exemplos de Uso

### Autenticação
```bash
# Login
curl -X POST http://localhost/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Dados do usuário
curl -X GET http://localhost/auth/user/ \
  -H "Authorization: Bearer <jwt_token>"
```

### Learning Service
```bash
# Listar cursos
curl -X GET http://localhost/learning/courses/ \
  -H "Authorization: Bearer <jwt_token>"
```

### Recommendation Service
```bash
# Obter recomendações
curl -X GET http://localhost/rec/recommendations/ \
  -H "Authorization: Bearer <jwt_token>"
```

## 🚀 Deploy em Produção

### 1. Configurar SSL/TLS
Adicione certificados SSL no NGINX para HTTPS.

### 2. Variáveis de Produção
```bash
ALLOWED_ORIGINS=https://yourdomain.com
AUTH_SERVICE_URL=http://auth_service:8000
LEARNING_SERVICE_URL=http://learning_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000
```

### 3. Monitoramento
Configure logs centralizados e monitoramento de métricas.

## 🔧 Troubleshooting

### Problema: CORS não funciona
- Verifique se `ALLOWED_ORIGINS` está configurado corretamente
- Confirme se o origin da requisição está na lista

### Problema: Rate limit muito restritivo
- Ajuste as configurações de rate limiting no `nginx.conf.template`
- Modifique `rate=100r/m` para um valor maior

### Problema: Timeout de requisições
- Aumente os valores de timeout no template
- Verifique se os microserviços estão respondendo

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
