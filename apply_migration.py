#!/usr/bin/env python3
"""
Script to apply the simplified_summary migration to Railway database
Run this script on Railway to add the missing column
"""

import os
import sys
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def apply_migration():
    """Apply the simplified_summary migration manually"""
    print("🔄 Applying simplified_summary migration to Railway database...")
    
    try:
        with connection.cursor() as cursor:
            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name='ai_insights' 
                AND column_name='simplified_summary'
            """)
            
            column_exists = cursor.fetchone()[0] > 0
            
            if column_exists:
                print("✅ Column 'simplified_summary' already exists!")
                return True
            
            # Add the column
            print("➕ Adding simplified_summary column...")
            cursor.execute("""
                ALTER TABLE ai_insights 
                ADD COLUMN simplified_summary TEXT
            """)
            
            print("✅ Successfully added simplified_summary column!")
            return True
            
    except Exception as e:
        print(f"❌ Error applying migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    if success:
        print("\n🎉 Migration applied successfully!")
        print("🚀 AI Analysis should now work with Simplified Summary!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
