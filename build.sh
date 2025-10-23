#!/bin/bash
# Build script for Render.com deployment

echo "🔧 Building Jeeva.AI Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=jeeva_ai_backend.settings

# Debug: Show environment variables
echo "🔍 Environment check:"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "DEBUG: $DEBUG"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"

# Always run migrations (even if DATABASE_URL is not set initially)
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "❌ Database migrations failed!"
    echo "🔍 Trying to show migration status..."
    python manage.py showmigrations
    exit 1
fi

# Show migration status for debugging
echo "🔍 Migration status:"
python manage.py showmigrations

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"