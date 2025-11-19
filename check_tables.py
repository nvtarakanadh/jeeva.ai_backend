#!/usr/bin/env python3
"""
Script to check what tables exist in Render PostgreSQL database
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Your Render PostgreSQL connection string
DATABASE_URL = "postgresql://jeeva_user:8ZPRmehSIzBJLwctTd6s66oEz6ZVqLjb@dpg-d3suic1r0fns738ppog0-a.oregon-postgres.render.com/jeeva_db"

def check_tables():
    """Check what tables exist in the Render PostgreSQL database"""
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
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            
            print(f"\n📋 Found {len(tables)} tables in the database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check if ai_insights exists
            ai_insights_exists = any(table[0] == 'ai_insights' for table in tables)
            
            if ai_insights_exists:
                print("\n✅ Table 'ai_insights' exists!")
                
                # Check columns in ai_insights
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='ai_insights'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                print(f"\n📊 Columns in 'ai_insights' table:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Check if simplified_summary exists
                simplified_exists = any(col[0] == 'simplified_summary' for col in columns)
                if simplified_exists:
                    print("\n✅ Column 'simplified_summary' already exists!")
                else:
                    print("\n❌ Column 'simplified_summary' does NOT exist!")
                    
            else:
                print("\n❌ Table 'ai_insights' does NOT exist!")
                
                # Check for similar table names
                similar_tables = [table[0] for table in tables if 'ai' in table[0].lower() or 'analysis' in table[0].lower()]
                if similar_tables:
                    print(f"\n🔍 Similar tables found: {similar_tables}")
            
            return tables
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()
            print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    print("🔍 Checking tables in Render PostgreSQL database...")
    tables = check_tables()
