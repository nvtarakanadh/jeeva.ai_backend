#!/usr/bin/env python3
"""
Script to check and fix database connection for production
This will help identify if the backend is using the correct database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from django.conf import settings
from django.db import connection

def check_production_database():
    """Check what database the production backend is using"""
    print("🔍 CHECKING PRODUCTION DATABASE CONNECTION")
    print("=" * 50)
    
    # Check environment variables
    print("\n📊 ENVIRONMENT VARIABLES:")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL is set")
        # Hide password for security
        if '@' in database_url:
            parts = database_url.split('@')
            if len(parts) == 2:
                safe_url = parts[0].split('//')[0] + '//[HIDDEN]@' + parts[1]
                print(f"🔗 Database: {safe_url}")
        else:
            print(f"🔗 Database: {database_url}")
    else:
        print("❌ DATABASE_URL is NOT set")
        print("💡 This means the backend is using SQLite (local development)")
    
    # Check Django database configuration
    print("\n📊 DJANGO DATABASE CONFIG:")
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config['ENGINE']}")
    print(f"Name: {db_config['NAME']}")
    print(f"Host: {db_config.get('HOST', 'N/A')}")
    print(f"Port: {db_config.get('PORT', 'N/A')}")
    print(f"User: {db_config.get('USER', 'N/A')}")
    
    # Test database connection
    print("\n🔌 TESTING DATABASE CONNECTION:")
    try:
        with connection.cursor() as cursor:
            # Check if ai_insights table exists
            if 'sqlite' in db_config['ENGINE']:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='ai_insights'
                """)
            else:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name='ai_insights'
                """)
            
            table_exists = cursor.fetchone() is not None
            print(f"ai_insights table exists: {table_exists}")
            
            if table_exists:
                # Check columns
                if 'sqlite' in db_config['ENGINE']:
                    cursor.execute("PRAGMA table_info(ai_insights)")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                else:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='ai_insights'
                    """)
                    columns = cursor.fetchall()
                    column_names = [col[0] for col in columns]
                
                print(f"Columns: {column_names}")
                simplified_exists = 'simplified_summary' in column_names
                print(f"simplified_summary column exists: {simplified_exists}")
                
                if not simplified_exists:
                    print("\n❌ PROBLEM: simplified_summary column is missing!")
                    print("💡 SOLUTION: Add the column to your database")
                    if 'sqlite' in db_config['ENGINE']:
                        print("   ALTER TABLE ai_insights ADD COLUMN simplified_summary TEXT;")
                    else:
                        print("   ALTER TABLE ai_insights ADD COLUMN simplified_summary TEXT;")
                        print("   Run this in Supabase SQL Editor:")
                        print("   https://supabase.com/dashboard/project/wgcmusjsuziqjkzuaqkd/sql")
            else:
                print("❌ PROBLEM: ai_insights table does not exist!")
                print("💡 SOLUTION: Run Django migrations")
                print("   python manage.py migrate")
        
        print("\n✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 PRODUCTION DATABASE DIAGNOSTIC")
    print("This will help identify the database connection issue")
    
    success = check_production_database()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Database connection is working")
        print("💡 If simplified_summary column is missing, add it using SQL")
    else:
        print("❌ Database connection issues found")
        print("💡 Check your DATABASE_URL environment variable")
    
    print("\n🔗 Supabase SQL Editor:")
    print("https://supabase.com/dashboard/project/wgcmusjsuziqjkzuaqkd/sql")
