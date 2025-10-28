#!/bin/bash

# Auth Service Entrypoint Script
# Handles database migrations and startup

set -e

echo "=== Auth Service Startup ==="

# Wait for database to be ready (apenas se DB_HOST estiver definido)
if [ -n "$DB_HOST" ]; then
    echo "Waiting for database..."
    while ! pg_isready -h $DB_HOST -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do
        echo "Database is unavailable - sleeping"
        sleep 1
    done
    
    echo "Database is ready!"
    
    # Run migrations
    echo "Running database migrations..."
    python manage.py migrate
    
    # Seed data (cria usuário admin)
    echo "Seeding initial data..."
    python manage.py seed_data || echo "Seed data command not found or failed, continuing..."
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput || echo "Static files collection skipped"
else
    echo "DB_HOST not set, skipping database operations"
fi

echo "=== Auth Service Ready ==="

# Execute the main command
exec "$@"
