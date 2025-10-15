# AVA - Fluxo de Autenticação Padronizado

Este documento descreve o fluxo de autenticação padronizado implementado no AVA, utilizando JWT RS256 com JWKS e headers confiáveis do API Gateway.

## 🔐 Arquitetura de Autenticação

### Componentes

1. **Auth Service**: Gera e valida tokens JWT RS256, expõe JWKS
2. **API Gateway**: Valida tokens e injeta headers confiáveis
3. **Learning Service**: Aceita JWT ou headers confiáveis
4. **Recommendation Service**: Aceita JWT ou headers confiáveis

### Fluxo de Autenticação

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant Learning as Learning Service
    participant Rec as Recommendation Service

    Client->>Auth: POST /auth/login
    Auth->>Client: JWT Token (RS256)
    
    Client->>Gateway: Request + JWT Token
    Gateway->>Auth: GET /.well-known/jwks.json
    Auth->>Gateway: JWKS (Public Key)
    Gateway->>Gateway: Validate JWT
    Gateway->>Learning: Request + X-User-Id Header
    Learning->>Client: Response
```

## 🛠️ Implementação

### 1. Auth Service - JWKS Endpoint

**Endpoint**: `GET /api/.well-known/jwks.json`

**Resposta**:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "key_ops": ["verify"],
      "alg": "RS256",
      "kid": "ava-auth-key-1",
      "n": "base64url-encoded-modulus",
      "e": "base64url-encoded-exponent"
    }
  ]
}
```

**Configuração JWT**:
```python
SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'AUDIENCE': 'ava-microservices',
    'ISSUER': 'ava-auth-service',
    'USER_ID_CLAIM': 'sub',  # Standard JWT claim
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### 2. API Gateway - Validação JWT

**Middleware de Validação**:
```javascript
// Valida JWT e injeta headers
function jwtValidationMiddleware(req, res, next) {
  validateToken(authHeader)
    .then(userInfo => {
      req.headers['x-user-id'] = userInfo.userId;
      req.headers['x-user-email'] = userInfo.email;
      req.headers['x-user-username'] = userInfo.username;
      req.headers['x-user-roles'] = JSON.stringify(userInfo.roles);
      next();
    })
    .catch(err => {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid or expired token',
        code: 'INVALID_TOKEN'
      });
    });
}
```

### 3. Learning Service - Helpers de Autenticação

**Classe de Permissão**:
```python
class IsAuthenticatedOrTrustedHeader(BasePermission):
    def has_permission(self, request, view):
        user = get_current_user(request)
        if user:
            request.current_user = user
            return True
        return False
```

**Extração de Usuário**:
```python
def get_current_user(request):
    # 1. Verifica headers confiáveis do Gateway
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        return {
            'user_id': int(user_id),
            'email': request.META.get('HTTP_X_USER_EMAIL', ''),
            'username': request.META.get('HTTP_X_USER_USERNAME', ''),
            'roles': request.META.get('HTTP_X_USER_ROLES', '["student"]'),
            'source': 'gateway_header'
        }
    
    # 2. Valida JWT token
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        payload = validate_jwt_token(token)
        return {
            'user_id': int(payload.get('sub')),
            'email': payload.get('email', ''),
            'username': payload.get('username', ''),
            'roles': payload.get('roles', ['student']),
            'source': 'jwt_token'
        }
    
    return None
```

### 4. Recommendation Service - Autenticação FastAPI

**Dependency de Autenticação**:
```python
def require_authentication(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    user = get_current_user(request, credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                'error': 'Authentication required',
                'message': 'Valid JWT token or trusted header required',
                'code': 'AUTHENTICATION_REQUIRED'
            }
        )
    return user
```

## 📋 Exemplos de Requests

### 1. Login e Obtenção de Token

**Request**:
```bash
curl -X POST http://localhost:8080/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response**:
```json
{
  "message": "Login realizado com sucesso",
  "access": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImF2YS1hdXRoLWtleS0xIn0...",
  "refresh": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImF2YS1hdXRoLWtleS0xIn0...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "João",
    "last_name": "Silva"
  }
}
```

### 2. Request com JWT Token

**Request**:
```bash
curl -X GET http://localhost:8080/learning/courses/ \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImF2YS1hdXRoLWtleS0xIn0..."
```

**Headers Injetados pelo Gateway**:
```
X-User-Id: 1
X-User-Email: user@example.com
X-User-Username: user
X-User-Roles: ["student"]
```

### 3. Request Interno (Service-to-Service)

**Request**:
```bash
curl -X GET http://learning_service:8000/learning/courses/ \
  -H "X-User-Id: 1" \
  -H "X-User-Email: user@example.com" \
  -H "X-User-Username: user" \
  -H "X-User-Roles: [\"student\"]"
```

## ❌ Respostas de Erro

### 401 Unauthorized

**Token Inválido**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "INVALID_TOKEN"
}
```

**Token Expirado**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "TOKEN_EXPIRED"
}
```

**Token Malformado**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "MALFORMED_TOKEN"
}
```

**Header de Autorização Ausente**:
```json
{
  "error": "Unauthorized",
  "message": "Authorization header is required",
  "code": "MISSING_AUTH_HEADER"
}
```

### 403 Forbidden

**Permissões Insuficientes**:
```json
{
  "error": "Insufficient permissions",
  "message": "Required roles: ['instructor', 'owner']",
  "code": "INSUFFICIENT_PERMISSIONS"
}
```

**Acesso Negado**:
```json
{
  "error": "Access denied",
  "message": "You don't have permission to access this resource",
  "code": "ACCESS_DENIED"
}
```

## 🔧 Configuração

### Variáveis de Ambiente

**Auth Service**:
```bash
JWT_ALGORITHM=RS256
JWT_AUDIENCE=ava-microservices
JWT_ISSUER=ava-auth-service
```

**API Gateway**:
```bash
AUTH_SERVICE_JWKS_URL=http://auth_service:8000/api/.well-known/jwks.json
AUTH_SERVICE_URL=http://auth_service:8000
```

**Learning Service**:
```bash
AUTH_SERVICE_URL=http://auth_service:8000
AUTH_SERVICE_JWKS_URL=http://auth_service:8000/api/.well-known/jwks.json
```

**Recommendation Service**:
```bash
AUTH_SERVICE_URL=http://auth_service:8000
AUTH_SERVICE_JWKS_URL=http://auth_service:8000/api/.well-known/jwks.json
```

## 🧪 Testes

### 1. Teste de JWKS Endpoint

```bash
curl -X GET http://localhost:8001/api/.well-known/jwks.json
```

### 2. Teste de Validação JWT

```bash
# Obter token
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}' \
  | jq -r '.access')

# Usar token
curl -X GET http://localhost:8080/learning/courses/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Teste de Headers Confiáveis

```bash
curl -X GET http://localhost:8002/learning/courses/ \
  -H "X-User-Id: 1" \
  -H "X-User-Email: user@example.com" \
  -H "X-User-Username: user" \
  -H "X-User-Roles: [\"student\"]"
```

## 🔍 Debugging

### Logs de Autenticação

**Auth Service**:
```python
logger.info(f"JWT generated for user {user.id}")
logger.info(f"JWKS requested from {request.META.get('REMOTE_ADDR')}")
```

**API Gateway**:
```javascript
console.log(`JWT validation: ${userInfo.userId} - ${userInfo.source}`);
console.log(`Headers injected: X-User-Id=${userInfo.userId}`);
```

**Learning Service**:
```python
logger.info(f"Auth info - User: {user['user_id']}, Source: {user['source']}, Action: {action}")
```

**Recommendation Service**:
```python
logger.info(f"Auth info - User: {user['user_id']}, Source: {user['source']}, Action: {action}")
```

### Verificação de Health

```bash
# Verificar JWKS
curl -X GET http://localhost:8001/api/.well-known/jwks.json

# Verificar Gateway
curl -X GET http://localhost:8080/healthz

# Verificar Learning Service
curl -X GET http://localhost:8002/learning/

# Verificar Recommendation Service
curl -X GET http://localhost:8003/health/
```

## 🚀 Deploy

### 1. Configurar Chaves JWT

```bash
# As chaves são geradas automaticamente na primeira execução
# Em produção, configure chaves fixas via variáveis de ambiente
export JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
export JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----..."
```

### 2. Configurar JWKS URL

```bash
# Em produção, use HTTPS
export AUTH_SERVICE_JWKS_URL="https://auth.ava.com/api/.well-known/jwks.json"
```

### 3. Configurar CORS

```bash
# Configurar origins permitidos
export ALLOWED_ORIGINS="https://app.ava.com,https://admin.ava.com"
```

## 📚 Referências

- [JWT.io](https://jwt.io/) - JWT Debugger
- [RFC 7517](https://tools.ietf.org/html/rfc7517) - JSON Web Key (JWK)
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JSON Web Token (JWT)
- [Django REST Framework JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
