#!/bin/sh

# API Gateway Docker Entrypoint Script
# Handles environment variable templating and nginx startup

set -e

# Default values for environment variables
export ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-http://localhost:4200,http://localhost:3000}"
export AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://auth_service:8000}"
export LEARNING_SERVICE_URL="${LEARNING_SERVICE_URL:-http://learning_service:8000}"
export RECOMMENDATION_SERVICE_URL="${RECOMMENDATION_SERVICE_URL:-http://recommendation_service:8000}"

# Log configuration
echo "=== API Gateway Configuration ==="
echo "Allowed Origins: $ALLOWED_ORIGINS"
echo "Auth Service URL: $AUTH_SERVICE_URL"
echo "Learning Service URL: $LEARNING_SERVICE_URL"
echo "Recommendation Service URL: $RECOMMENDATION_SERVICE_URL"
echo "================================"

# Validate required environment variables
if [ -z "$ALLOWED_ORIGINS" ]; then
    echo "ERROR: ALLOWED_ORIGINS environment variable is required"
    exit 1
fi

if [ -z "$AUTH_SERVICE_URL" ]; then
    echo "ERROR: AUTH_SERVICE_URL environment variable is required"
    exit 1
fi

if [ -z "$LEARNING_SERVICE_URL" ]; then
    echo "ERROR: LEARNING_SERVICE_URL environment variable is required"
    exit 1
fi

if [ -z "$RECOMMENDATION_SERVICE_URL" ]; then
    echo "ERROR: RECOMMENDATION_SERVICE_URL environment variable is required"
    exit 1
fi

# Generate nginx configuration from template
echo "Generating nginx configuration..."
envsubst '${ALLOWED_ORIGINS} ${AUTH_SERVICE_URL} ${LEARNING_SERVICE_URL} ${RECOMMENDATION_SERVICE_URL}' \
    < /etc/nginx/templates/nginx.conf.template \
    > /etc/nginx/nginx.conf

# Validate nginx configuration
echo "Validating nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    echo "ERROR: Invalid nginx configuration"
    exit 1
fi

echo "Nginx configuration is valid. Starting nginx..."

# Execute the main command
exec "$@"
