#!/usr/bin/env python3
"""
Script to apply migration to Render PostgreSQL database
Run this locally to add the simplified_summary column to your production database
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Your Render PostgreSQL connection string
DATABASE_URL = "postgresql://jeeva_user:8ZPRmehSIzBJLwctTd6s66oEz6ZVqLjb@dpg-d3suic1r0fns738ppog0-a.oregon-postgres.render.com/jeeva_db"

def apply_migration_to_render():
    """Apply the simplified_summary migration to Render PostgreSQL database"""
    print("🔄 Connecting to Render PostgreSQL database...")
    
    try:
        # Parse the database URL
        parsed_url = urlparse(DATABASE_URL)
        
        # Connect to the database
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port,
            database=parsed_url.path[1:],  # Remove leading slash
            user=parsed_url.username,
            password=parsed_url.password
        )
        
        print("✅ Connected to Render PostgreSQL database!")
        
        with conn.cursor() as cursor:
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
            print("➕ Adding simplified_summary column to ai_insights table...")
            cursor.execute("""
                ALTER TABLE ai_insights 
                ADD COLUMN simplified_summary TEXT
            """)
            
            # Commit the changes
            conn.commit()
            
            print("✅ Successfully added simplified_summary column!")
            
            # Verify the column was added
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='ai_insights' 
                AND column_name='simplified_summary'
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"✅ Verification: Column '{result[0]}' with type '{result[1]}' confirmed!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error applying migration: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Database connection closed.")

if __name__ == "__main__":
    print("🚀 Applying migration to Render PostgreSQL database...")
    print(f"🔗 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Render PostgreSQL'}")
    
    success = apply_migration_to_render()
    if success:
        print("\n🎉 Migration applied successfully!")
        print("🚀 AI Analysis should now work with Simplified Summary!")
        print("📱 Test by uploading a health record on your deployed app!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
