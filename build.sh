#!/bin/bash
# Build script for Render.com deployment

echo "🔧 Building Jeeva.AI Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=jeeva_ai_backend.settings

# Run database migrations if DATABASE_URL is available
if [ ! -z "$DATABASE_URL" ]; then
    echo "🔄 Running database migrations..."
    python manage.py migrate --noinput
    if [ $? -eq 0 ]; then
        echo "✅ Database migrations completed successfully!"
    else
        echo "❌ Database migrations failed!"
        exit 1
    fi
else
    echo "⚠️ DATABASE_URL not found, skipping migrations..."
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"