#!/usr/bin/env python3
"""
Script to apply the simplified_summary migration to Supabase database
Run this script to add the missing column to your Supabase production database
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Supabase database connection details
SUPABASE_URL = "https://wgcmusjsuziqjkzuaqkd.supabase.co"
# You'll need to get the database password from Supabase dashboard
# Go to Settings > Database > Connection string
# Format: postgresql://postgres:[PASSWORD]@db.wgcmusjsuziqjkzuaqkd.supabase.co:5432/postgres

# For now, let's try to connect using the Supabase connection string
# You'll need to replace [PASSWORD] with your actual database password
DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.wgcmusjsuziqjkzuaqkd.supabase.co:5432/postgres"

def apply_migration_to_supabase():
    """Apply the simplified_summary migration to Supabase database"""
    print("🔄 Connecting to Supabase database...")
    print("⚠️  Note: You need to replace [PASSWORD] with your actual Supabase database password")
    print("📋 Get it from: Supabase Dashboard > Settings > Database > Connection string")
    
    # Check if password is still placeholder
    if "[PASSWORD]" in DATABASE_URL:
        print("\n❌ Please update the DATABASE_URL with your actual Supabase database password!")
        print("🔗 Go to: https://supabase.com/dashboard/project/wgcmusjsuziqjkzuaqkd/settings/database")
        print("📋 Copy the connection string and replace [PASSWORD] in this script")
        return False
    
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
        
        print("✅ Connected to Supabase database!")
        
        with conn.cursor() as cursor:
            # Check if ai_insights table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name='ai_insights'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                print("❌ Table 'ai_insights' does not exist!")
                print("🔍 This means Django migrations haven't been applied to Supabase yet.")
                print("💡 You need to run Django migrations first:")
                print("   python manage.py migrate")
                return False
            
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
    print("🚀 Applying migration to Supabase database...")
    print(f"🔗 Supabase Project: {SUPABASE_URL}")
    
    success = apply_migration_to_supabase()
    if success:
        print("\n🎉 Migration applied successfully!")
        print("🚀 AI Analysis should now work with Simplified Summary!")
        print("📱 Test by uploading a health record on your deployed app!")
    else:
        print("\n💥 Migration failed!")
        print("\n📋 Next steps:")
        print("1. Get your Supabase database password from the dashboard")
        print("2. Update the DATABASE_URL in this script")
        print("3. Run the script again")
        sys.exit(1)
