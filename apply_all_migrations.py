#!/usr/bin/env python3
"""
Script to apply all Django migrations to Render PostgreSQL database
This will create all the necessary tables including ai_insights with simplified_summary
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def apply_all_migrations():
    """Apply all Django migrations to Render PostgreSQL database"""
    print("🔄 Applying all Django migrations to Render PostgreSQL database...")
    
    try:
        # Run migrations
        print("📦 Running: python manage.py migrate")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ All migrations applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying migrations: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 Applying Django migrations to Render PostgreSQL database...")
    
    success = apply_all_migrations()
    if success:
        print("\n🎉 All migrations applied successfully!")
        print("🚀 AI Analysis should now work with Simplified Summary!")
        print("📱 Test by uploading a health record on your deployed app!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
