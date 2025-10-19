#!/bin/bash
# Build script for Render.com deployment

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL not found. Skipping database migrations during build."
    echo "Database will be set up when the service starts."
else
    echo "DATABASE_URL found. Running database migrations..."
    python setup_database.py
fi

echo "Build completed successfully!"
