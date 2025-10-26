#!/usr/bin/env python3
"""
Script to check which columns in ai_insights table are unused or have minimal data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

from django.db import connection

def check_column_usage():
    """Check which columns have data and which are mostly empty"""
    print("🔍 CHECKING COLUMN USAGE IN ai_insights TABLE")
    print("=" * 50)
    
    try:
        with connection.cursor() as cursor:
            # Get total record count
            cursor.execute("SELECT COUNT(*) FROM ai_insights")
            total_records = cursor.fetchone()[0]
            print(f"📊 Total records: {total_records}")
            
            # Check each column for non-null, non-empty values
            columns_to_check = [
                'record_id',
                'summary', 
                'key_findings',
                'risk_warnings',
                'recommendations',
                'confidence',
                'analysis_type',
                'processed_at',
                'record_title',
                'disclaimer',
                'simplified_summary'
            ]
            
            print(f"\n📋 COLUMN USAGE ANALYSIS:")
            print("-" * 50)
            
            for column in columns_to_check:
                try:
                    # Check for non-null values
                    cursor.execute(f"SELECT COUNT(*) FROM ai_insights WHERE {column} IS NOT NULL")
                    non_null_count = cursor.fetchone()[0]
                    
                    # Check for non-empty values (for text fields)
                    cursor.execute(f"SELECT COUNT(*) FROM ai_insights WHERE {column} IS NOT NULL AND {column} != ''")
                    non_empty_count = cursor.fetchone()[0]
                    
                    usage_percentage = (non_empty_count / total_records * 100) if total_records > 0 else 0
                    
                    print(f"{column:20} | Non-null: {non_null_count:3} | Non-empty: {non_empty_count:3} | Usage: {usage_percentage:5.1f}%")
                    
                    # Mark columns that are mostly unused
                    if usage_percentage < 10:
                        print(f"{'':20} | ⚠️  LOW USAGE - Good candidate for simplified summary")
                    elif usage_percentage < 50:
                        print(f"{'':20} | ⚡ MODERATE USAGE - Could be used with caution")
                    else:
                        print(f"{'':20} | ✅ HIGH USAGE - Not recommended")
                        
                except Exception as e:
                    print(f"{column:20} | ❌ Error checking: {str(e)}")
            
            print(f"\n💡 RECOMMENDATIONS:")
            print("-" * 50)
            print("Based on usage analysis, here are the best candidates:")
            print("1. simplified_summary - Already exists, mostly empty")
            print("2. disclaimer - Check if it's actually used")
            print("3. analysis_type - Might have repetitive values")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_column_usage()
