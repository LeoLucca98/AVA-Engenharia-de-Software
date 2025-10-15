#!/bin/bash

# Script para testar o API Gateway
# Verifica se todas as rotas estão funcionando corretamente

set -e

GATEWAY_URL="http://localhost"
AUTH_TOKEN=""

echo "🧪 Testando API Gateway..."
echo "=========================="

# Teste 1: Health Check
echo "1. Testando Health Check..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/healthz")
if [ "$response" = "200" ]; then
    echo "✅ Health Check: OK"
else
    echo "❌ Health Check: Falhou (HTTP $response)"
    exit 1
fi

# Teste 2: CORS Preflight
echo "2. Testando CORS Preflight..."
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS \
    -H "Origin: http://localhost:4200" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: Authorization" \
    "$GATEWAY_URL/auth/user/")
if [ "$response" = "204" ]; then
    echo "✅ CORS Preflight: OK"
else
    echo "❌ CORS Preflight: Falhou (HTTP $response)"
fi

# Teste 3: Rota não encontrada
echo "3. Testando rota não encontrada..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/rota-inexistente/")
if [ "$response" = "404" ]; then
    echo "✅ Rota não encontrada: OK"
else
    echo "❌ Rota não encontrada: Falhou (HTTP $response)"
fi

# Teste 4: Rate Limiting (se os serviços estiverem rodando)
echo "4. Testando Rate Limiting..."
for i in {1..5}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/auth/login/")
    echo "   Requisição $i: HTTP $response"
done

echo ""
echo "🎉 Testes do API Gateway concluídos!"
echo ""
echo "Para testar com autenticação, primeiro faça login:"
echo "curl -X POST $GATEWAY_URL/auth/login/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"email\": \"user@example.com\", \"password\": \"password\"}'"
echo ""
echo "Depois use o token retornado nas requisições autenticadas."
