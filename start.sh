#!/bin/bash
# Startup script for Render.com deployment

echo "🚀 Starting Jeeva.AI Backend Service..."

# Check if DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable not found!"
    echo "Please ensure you have:"
    echo "1. Created a PostgreSQL database in Render.com"
    echo "2. Added DATABASE_URL to your environment variables"
    echo "3. The DATABASE_URL should look like: postgresql://user:pass@host:port/db"
    exit 1
fi

echo "✅ DATABASE_URL found. Setting up database..."

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
else
    echo "❌ Database setup failed!"
    exit 1
fi

echo "🚀 Starting Gunicorn server on port $PORT..."

# Start the application
exec gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
