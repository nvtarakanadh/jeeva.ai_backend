-- SQL Script to add simplified_summary column to ai_insights table
-- Run this in Supabase SQL Editor

-- Check if the table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'ai_insights';

-- Check if the column already exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'ai_insights' 
AND column_name = 'simplified_summary';

-- Add the simplified_summary column if it doesn't exist
ALTER TABLE ai_insights 
ADD COLUMN IF NOT EXISTS simplified_summary TEXT;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'ai_insights' 
ORDER BY ordinal_position;
