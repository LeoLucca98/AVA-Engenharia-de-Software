#!/bin/bash

# Learning Service Entrypoint Script
# Handles database migrations and startup

set -e

echo "=== Learning Service Startup ==="

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Seed data
echo "Seeding initial data..."
python manage.py seed_data

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Learning Service Ready ==="

# Execute the main command
exec "$@"
