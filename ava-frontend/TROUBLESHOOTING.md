# Troubleshooting - Frontend AVA

## Erro: "Service Unavailable" ao fazer login

### Sintomas
Ao acessar `http://localhost:4200/auth/login` e tentar fazer login, recebe:
```json
{"error":"Service Unavailable","message":"The requested service is temporarily unavailable","code":"SERVICE_UNAVAILABLE"}
```

### Possíveis Causas e Soluções

#### 1. Frontend não está usando o proxy

**Solução:** Certifique-se de que o Angular está rodando com o proxy habilitado:

```bash
# Use o comando que inclui o proxy:
npm run dev

# OU use o Angular CLI diretamente com proxy:
ng serve --proxy-config proxy.conf.json

# NÃO use apenas:
npm start  # Este comando pode não usar o proxy
```

O `angular.json` já foi configurado para usar o proxy automaticamente, mas se ainda tiver problemas, use explicitamente `npm run dev`.

#### 2. API Gateway não está rodando

**Verificar:**
```bash
docker ps | grep api-gateway
curl http://localhost:8080/healthz
```

**Solução:** Se não estiver rodando:
```bash
docker-compose up -d api-gateway
```

#### 3. Serviços backend não estão rodando

**Verificar:**
```bash
docker ps | grep -E "auth_service|learning_service|recommendation_service"
```

**Solução:** Subir todos os serviços:
```bash
docker-compose up -d
```

#### 4. Problema de CORS

Se o erro for de CORS, verifique:
- O API Gateway está configurado para aceitar `http://localhost:4200`
- O proxy do Angular está configurado corretamente em `proxy.conf.json`

#### 5. URL base incorreta

**Verificar:** `src/environments/environment.ts`

```typescript
// Deve estar vazio quando usando proxy:
apiBaseUrl: '',

// NÃO deve ser:
apiBaseUrl: 'http://localhost:8080', // ❌ Errado quando usando proxy
```

### Checklist de Diagnóstico

1. [ ] API Gateway está rodando na porta 8080?
   ```bash
   curl http://localhost:8080/healthz
   ```

2. [ ] Frontend está rodando com proxy?
   ```bash
   npm run dev
   ```

3. [ ] Todos os serviços backend estão rodando?
   ```bash
   docker-compose ps
   ```

4. [ ] O ambiente está configurado corretamente?
   - `apiBaseUrl` está vazio em `environment.ts`?
   - `proxy.conf.json` aponta para `http://localhost:8080`?

5. [ ] Não há erros no console do navegador?
   - Abrir DevTools (F12)
   - Verificar aba Network para ver requisições falhando
   - Verificar aba Console para erros JavaScript

### Teste Manual do Endpoint

Testar se o endpoint de login está funcionando diretamente:

```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8080/auth/login/" -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@ava.com","password":"admin123"}'

# Ou usar curl se disponível
curl -X POST http://localhost:8080/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ava.com","password":"admin123"}'
```

### Logs Úteis

**API Gateway:**
```bash
docker-compose logs -f api-gateway
```

**Auth Service:**
```bash
docker-compose logs -f auth_service
```

**Frontend (console do navegador):**
- Abrir DevTools (F12)
- Aba Network: ver requisições HTTP
- Aba Console: ver erros JavaScript
