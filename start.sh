#!/bin/bash
# Startup script for Render.com deployment

echo "Starting Jeeva.AI Backend Service..."

# Check if DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not found!"
    echo "Please ensure you have:"
    echo "1. Created a PostgreSQL database in Render.com"
    echo "2. Added DATABASE_URL to your environment variables"
    exit 1
fi

echo "DATABASE_URL found. Setting up database..."

# Run database migrations
python manage.py migrate

echo "Database setup completed. Starting Gunicorn server..."

# Start the application
exec gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
