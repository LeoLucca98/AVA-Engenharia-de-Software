# 🌐 Guia de Deploy

Este guia explica como fazer deploy do AVA em ambiente de produção.

## 🎯 Estratégias de Deploy

### 1. Deploy com Docker Compose (Recomendado para MVP)

Ideal para:
- Ambientes pequenos/médios
- Deploy rápido
- Manutenção simples

### 2. Deploy com Kubernetes (Recomendado para Produção)

Ideal para:
- Ambientes grandes
- Alta disponibilidade
- Escalabilidade automática

### 3. Deploy Híbrido

Ideal para:
- Migração gradual
- Ambientes complexos
- Flexibilidade

## 🐳 Deploy com Docker Compose

### 1. Preparação do Servidor

#### Requisitos Mínimos

```bash
# CPU: 4 cores
# RAM: 8GB
# Disco: 50GB SSD
# OS: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
```

#### Instalação de Dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose git make curl

# CentOS/RHEL
sudo yum install -y docker docker-compose git make curl
sudo systemctl enable docker
sudo systemctl start docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

### 2. Configuração do Ambiente

#### Clonar Repositório

```bash
git clone <repository-url>
cd AVA-P4
```

#### Configurar Variáveis de Produção

```bash
# Copiar arquivo de exemplo
cp env.example .env.prod

# Editar para produção
nano .env.prod
```

**Arquivo `.env.prod`:**
```bash
# Produção
DEBUG=False
DEVELOPMENT_MODE=False

# Segurança
SECRET_KEY=your-super-secret-key-here-change-this
DB_PASSWORD=your-secure-database-password

# Domínios
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com,app.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# URLs dos serviços
AUTH_SERVICE_URL=http://auth_service:8000
LEARNING_SERVICE_URL=http://learning_service:8000
RECOMMENDATION_SERVICE_URL=http://recommendation_service:8000

# JWT
JWT_ALGORITHM=RS256
JWT_AUDIENCE=ava-microservices
JWT_ISSUER=ava-auth-service

# Logs
LOG_LEVEL=INFO
```

### 3. Deploy

#### Deploy Inicial

```bash
# Usar arquivo de produção
export COMPOSE_FILE=docker-compose.yml
export ENV_FILE=.env.prod

# Build e deploy
make build
make up

# Verificar status
make health
```

#### Script de Deploy Automatizado

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando deploy do AVA..."

# Backup do banco (se necessário)
echo "📦 Fazendo backup..."
# ./scripts/backup.sh

# Pull das últimas mudanças
echo "📥 Atualizando código..."
git pull origin main

# Build das imagens
echo "🔨 Build das imagens..."
docker-compose -f docker-compose.yml --env-file .env.prod build

# Deploy com zero downtime
echo "🚀 Deploy com zero downtime..."
docker-compose -f docker-compose.yml --env-file .env.prod up -d

# Aguardar serviços ficarem saudáveis
echo "⏳ Aguardando serviços..."
sleep 30

# Verificar health checks
echo "🔍 Verificando health checks..."
make health

# Executar migrações
echo "🗄️ Executando migrações..."
make migrate

echo "✅ Deploy concluído com sucesso!"
```

### 4. Configuração de Proxy Reverso

#### Nginx

```nginx
# /etc/nginx/sites-available/ava
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com app.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:4200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # API Gateway
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com -d app.yourdomain.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ☸️ Deploy com Kubernetes

### 1. Preparação do Cluster

#### Criar Cluster

```bash
# GKE (Google Cloud)
gcloud container clusters create ava-cluster \
  --num-nodes=3 \
  --machine-type=e2-standard-2 \
  --zone=us-central1-a

# EKS (AWS)
eksctl create cluster --name ava-cluster --region us-west-2

# AKS (Azure)
az aks create --resource-group ava-rg --name ava-cluster --node-count 3
```

### 2. Manifests Kubernetes

#### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ava
```

#### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ava-config
  namespace: ava
data:
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  JWT_ALGORITHM: "RS256"
  JWT_AUDIENCE: "ava-microservices"
  JWT_ISSUER: "ava-auth-service"
```

#### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ava-secrets
  namespace: ava
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DB_PASSWORD: <base64-encoded-password>
```

#### Deployments

```yaml
# k8s/auth-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: ava
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: ava/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          valueFrom:
            configMapKeyRef:
              name: ava-config
              key: DEBUG
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ava-secrets
              key: SECRET_KEY
        livenessProbe:
          httpGet:
            path: /healthz/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Services

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: ava
spec:
  selector:
    app: auth-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ava-ingress
  namespace: ava
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: ava-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8000
      - path: /learning
        pathType: Prefix
        backend:
          service:
            name: learning-service
            port:
              number: 8000
      - path: /rec
        pathType: Prefix
        backend:
          service:
            name: recommendation-service
            port:
              number: 8000
```

### 3. Deploy no Kubernetes

```bash
# Aplicar manifests
kubectl apply -f k8s/

# Verificar status
kubectl get pods -n ava
kubectl get services -n ava
kubectl get ingress -n ava

# Ver logs
kubectl logs -f deployment/auth-service -n ava
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Run tests
      run: |
        make test
        make test-coverage

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build images
      run: |
        docker build -t ava/auth-service:latest ./auth_service
        docker build -t ava/learning-service:latest ./learning_service
        docker build -t ava/recommendation-service:latest ./recommendation_service
        docker build -t ava/api-gateway:latest ./api-gateway
        docker build -t ava/frontend:latest ./ava-frontend

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to production
      run: |
        # Deploy script
        ./scripts/deploy.sh
```

## 📊 Monitoramento em Produção

### 1. Logs Centralizados

#### ELK Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
```

### 2. Métricas

#### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. Alertas

#### AlertManager

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:5001/'
```

## 🔒 Segurança em Produção

### 1. Secrets Management

```bash
# Usar Docker Secrets
echo "your-secret-key" | docker secret create secret_key -
echo "your-db-password" | docker secret create db_password -

# Ou usar ferramentas como HashiCorp Vault
```

### 2. Network Security

```yaml
# docker-compose.prod.yml
networks:
  ava_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 3. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📈 Escalabilidade

### 1. Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth-service-hpa
  namespace: ava
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Load Balancer

```yaml
# k8s/loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service-lb
  namespace: ava
spec:
  type: LoadBalancer
  selector:
    app: auth-service
  ports:
  - port: 80
    targetPort: 8000
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Serviço não inicia
```bash
# Verificar logs
docker-compose logs <service>

# Verificar recursos
docker stats

# Verificar configuração
docker-compose config
```

#### 2. Banco de dados não conecta
```bash
# Verificar conectividade
docker-compose exec <service> ping <db-service>

# Verificar logs do banco
docker-compose logs <db-service>

# Resetar banco
docker-compose down -v
docker-compose up -d
```

#### 3. JWT não funciona
```bash
# Verificar JWKS
curl https://api.yourdomain.com/auth/.well-known/jwks.json

# Verificar logs
docker-compose logs auth_service | grep -i jwt
```

### Comandos de Emergência

```bash
# Rollback rápido
docker-compose down
git checkout <previous-commit>
docker-compose up -d

# Backup de emergência
./scripts/backup.sh

# Restart de todos os serviços
docker-compose restart
```
