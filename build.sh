#!/bin/bash
# Build script for Render.com deployment

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
echo "Note: Database migrations will run when the service starts with DATABASE_URL"
