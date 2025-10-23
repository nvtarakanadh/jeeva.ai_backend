#!/usr/bin/env python
"""
Manual migration script for Render deployment
Run this if migrations fail during build
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("🔄 Running manual migrations...")
    
    # Show current migration status
    print("📋 Current migration status:")
    execute_from_command_line(['manage.py', 'showmigrations'])
    
    # Run migrations
    print("🔄 Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Show final status
    print("📋 Final migration status:")
    execute_from_command_line(['manage.py', 'showmigrations'])
    
    print("✅ Manual migrations completed!")
