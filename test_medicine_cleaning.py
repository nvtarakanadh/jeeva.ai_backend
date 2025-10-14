#!/usr/bin/env python3
"""
Test script for medicine name cleaning functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeva_ai_backend.settings')
django.setup()

def test_medicine_cleaning():
    """Test the medicine name cleaning functionality"""
    print("Testing Medicine Name Cleaning")
    print("=" * 40)
    
    # Test cases with various formatting issues
    test_cases = [
        '```json ["Paracetamol", "Ibuprofen"] ```',
        '```json ["Paracetamol, Ibuprofen"] ```',
        '["Paracetamol", "Ibuprofen"]',
        '```json\n["Paracetamol", "Ibuprofen"]\n```',
        'Paracetamol, Ibuprofen',
        '```json ["Metformin", "Lisinopril", "Atorvastatin"] ```',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case}")
        
        # Simulate the cleaning logic
        medicine_names_text = test_case.strip()
        
        # Clean up the response to extract JSON
        if '```json' in medicine_names_text:
            medicine_names_text = medicine_names_text.split('```json')[1].split('```')[0].strip()
        elif '```' in medicine_names_text:
            medicine_names_text = medicine_names_text.split('```')[1].split('```')[0].strip()
        
        try:
            # Try to parse as JSON
            if medicine_names_text.startswith('[') and medicine_names_text.endswith(']'):
                medicine_names = json.loads(medicine_names_text)
            else:
                # Fallback: extract medicine names from text
                medicine_names = [name.strip().strip('"\'') for name in medicine_names_text.split(',')]
                medicine_names = [name for name in medicine_names if name]
        except:
            # If parsing fails, try to extract medicine names from the text
            medicine_names = [medicine_names_text]

        # Clean up medicine names - remove any JSON formatting artifacts
        cleaned_medicines = []
        for medicine in medicine_names:
            # Remove any JSON formatting or extra characters
            clean_medicine = medicine.strip().strip('"\'`').replace('```json', '').replace('```', '').strip()
            # Remove JSON array formatting
            clean_medicine = clean_medicine.replace('[', '').replace(']', '').replace('json', '').strip()
            # Remove extra quotes and commas
            clean_medicine = clean_medicine.replace('", "', ', ').replace('"', '').strip()
            # Split by comma if it's a combined string
            if ',' in clean_medicine:
                individual_medicines = [med.strip().strip('"\'') for med in clean_medicine.split(',')]
                cleaned_medicines.extend(individual_medicines)
            elif clean_medicine and clean_medicine not in ['[', ']', 'json', '']:
                cleaned_medicines.append(clean_medicine)
        
        # Remove duplicates and empty strings
        final_medicines = list(set([med for med in cleaned_medicines if med and med.strip()]))
        
        print(f"  Cleaned result: {final_medicines}")
        print(f"  Count: {len(final_medicines)}")
        
        # Check if we got clean medicine names
        if all(med and not any(char in med for char in ['[', ']', '`', 'json']) for med in final_medicines):
            print("  [PASS] Clean medicine names")
        else:
            print("  [FAIL] Still contains formatting artifacts")

if __name__ == "__main__":
    import json
    test_medicine_cleaning()
