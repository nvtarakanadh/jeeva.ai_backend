#!/usr/bin/env python3
"""
Comprehensive debugging script to check why simplified summary is not appearing
This will check both local and production database configurations
"""

import os
import sys
import django
from django.db import connection
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def debug_database_config():
    """Debug database configuration and table structure"""
    print("🔍 DEBUGGING SIMPLIFIED SUMMARY ISSUE")
    print("=" * 50)
    
    # Check database configuration
    print("\n📊 DATABASE CONFIGURATION:")
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config['ENGINE']}")
    print(f"Name: {db_config['NAME']}")
    print(f"Host: {db_config.get('HOST', 'N/A')}")
    print(f"Port: {db_config.get('PORT', 'N/A')}")
    print(f"User: {db_config.get('USER', 'N/A')}")
    
    # Check if we're using SQLite or PostgreSQL
    if 'sqlite' in db_config['ENGINE']:
        print("🔍 Using SQLite (local development)")
    else:
        print("🔍 Using PostgreSQL (production)")
    
    try:
        with connection.cursor() as cursor:
            # Check if ai_insights table exists
            print("\n📋 CHECKING TABLES:")
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
            
            if not table_exists:
                print("❌ PROBLEM: ai_insights table does not exist!")
                return False
            
            # Check columns in ai_insights table
            print("\n📊 CHECKING COLUMNS IN ai_insights:")
            if 'sqlite' in db_config['ENGINE']:
                cursor.execute("PRAGMA table_info(ai_insights)")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            else:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='ai_insights'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
            
            # Check specifically for simplified_summary
            simplified_exists = any('simplified_summary' in str(col) for col in columns)
            print(f"\n✅ simplified_summary column exists: {simplified_exists}")
            
            if not simplified_exists:
                print("❌ PROBLEM: simplified_summary column does not exist!")
                print("💡 SOLUTION: Add the column using SQL:")
                if 'sqlite' in db_config['ENGINE']:
                    print("   ALTER TABLE ai_insights ADD COLUMN simplified_summary TEXT;")
                else:
                    print("   ALTER TABLE ai_insights ADD COLUMN simplified_summary TEXT;")
                return False
            
            # Check if there are any existing records
            print("\n📊 CHECKING EXISTING RECORDS:")
            cursor.execute("SELECT COUNT(*) FROM ai_insights")
            count = cursor.fetchone()[0]
            print(f"Total records in ai_insights: {count}")
            
            if count > 0:
                # Check if any records have simplified_summary
                cursor.execute("SELECT COUNT(*) FROM ai_insights WHERE simplified_summary IS NOT NULL AND simplified_summary != ''")
                with_summary = cursor.fetchone()[0]
                print(f"Records with simplified_summary: {with_summary}")
                
                if with_summary == 0:
                    print("⚠️  WARNING: No records have simplified_summary content!")
                    print("💡 This means the backend is not saving simplified_summary")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

def check_backend_code():
    """Check if backend code is properly configured"""
    print("\n🔍 CHECKING BACKEND CODE:")
    
    # Check if views.py includes simplified_summary
    views_file = os.path.join(os.path.dirname(__file__), 'ai_analysis', 'views.py')
    if os.path.exists(views_file):
        with open(views_file, 'r') as f:
            content = f.read()
            if 'simplified_summary' in content:
                print("✅ views.py includes simplified_summary")
            else:
                print("❌ views.py does NOT include simplified_summary")
    
    # Check if models.py includes simplified_summary
    models_file = os.path.join(os.path.dirname(__file__), 'ai_analysis', 'models.py')
    if os.path.exists(models_file):
        with open(models_file, 'r') as f:
            content = f.read()
            if 'simplified_summary' in content:
                print("✅ models.py includes simplified_summary")
            else:
                print("❌ models.py does NOT include simplified_summary")
    
    # Check if serializers.py includes simplified_summary
    serializers_file = os.path.join(os.path.dirname(__file__), 'ai_analysis', 'serializers.py')
    if os.path.exists(serializers_file):
        with open(serializers_file, 'r') as f:
            content = f.read()
            if 'simplifiedSummary' in content:
                print("✅ serializers.py includes simplifiedSummary")
            else:
                print("❌ serializers.py does NOT include simplifiedSummary")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE DEBUGGING SCRIPT")
    print("This will help identify why simplified summary is not appearing")
    
    # Check database
    db_ok = debug_database_config()
    
    # Check backend code
    check_backend_code()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("✅ Database structure looks correct")
        print("💡 If simplified summary still not appearing, check:")
        print("   1. Backend deployment has latest code")
        print("   2. Frontend is reading simplifiedSummary field")
        print("   3. AI analysis is generating simplified_summary content")
    else:
        print("❌ Database issues found - fix them first")
    
    print("\n🔍 Next steps:")
    print("1. Run this script locally to check your local database")
    print("2. Check your production database (Supabase) manually")
    print("3. Verify backend deployment has latest code")
