#!/usr/bin/env python
"""
Database setup script for Render.com deployment
This script handles database setup without requiring a connection during build
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Setup database for production deployment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
    django.setup()
    
    # Check if DATABASE_URL is available
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable not found!")
        print("Please ensure you have:")
        print("1. Created a PostgreSQL database in Render.com")
        print("2. Added DATABASE_URL to your environment variables")
        sys.exit(1)
    
    print("DATABASE_URL found, proceeding with database setup...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("Database migrations completed successfully!")
        
        # Create superuser if needed (optional)
        # execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
