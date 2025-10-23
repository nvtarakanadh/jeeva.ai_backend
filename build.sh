#!/bin/bash
# Build script for Render.com deployment

echo "🔧 Building Jeeva.AI Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations if DATABASE_URL is available
if [ ! -z "$DATABASE_URL" ]; then
    echo "🔄 Running database migrations..."
    python manage.py migrate
    if [ $? -eq 0 ]; then
        echo "✅ Database migrations completed successfully!"
    else
        echo "❌ Database migrations failed!"
        exit 1
    fi
else
    echo "⚠️ DATABASE_URL not found, skipping migrations..."
fi

echo "✅ Build completed successfully!"