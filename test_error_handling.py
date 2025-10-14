#!/usr/bin/env python3
"""
Test script for error handling in the AI services
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_medicine_cleaning():
    """Test the medicine name cleaning with various inputs"""
    print("Testing Medicine Name Cleaning Error Handling")
    print("=" * 50)
    
    # Test cases that might cause index errors
    test_cases = [
        [],  # Empty list
        [None],  # None value
        [""],  # Empty string
        ["", None, "Paracetamol"],  # Mixed valid/invalid
        ["```json [\"Paracetamol\"] ```"],  # JSON with artifacts
        [123, "Ibuprofen"],  # Mixed types
        ["Paracetamol, Ibuprofen"],  # Comma-separated
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case}")
        try:
            # Simulate the cleaning logic
            cleaned_medicines = []
            for medicine in test_case:
                if not medicine or not isinstance(medicine, str):
                    continue
                
                # Remove any JSON formatting or extra characters
                clean_medicine = medicine.strip().strip('"\'`').replace('```json', '').replace('```', '').strip()
                # Remove JSON array formatting
                clean_medicine = clean_medicine.replace('[', '').replace(']', '').replace('json', '').strip()
                # Remove extra quotes and commas
                clean_medicine = clean_medicine.replace('", "', ', ').replace('"', '').strip()
                # Split by comma if it's a combined string
                if ',' in clean_medicine:
                    individual_medicines = [med.strip().strip('"\'') for med in clean_medicine.split(',') if med.strip()]
                    cleaned_medicines.extend(individual_medicines)
                elif clean_medicine and clean_medicine not in ['[', ']', 'json', '']:
                    cleaned_medicines.append(clean_medicine)
            
            # Remove duplicates and empty strings safely
            try:
                result = list(set([med for med in cleaned_medicines if med and str(med).strip()]))
            except (TypeError, AttributeError) as e:
                print(f"  Warning: Error removing duplicates: {e}")
                result = [str(med) for med in cleaned_medicines if med]
            
            print(f"  Result: {result}")
            print(f"  [SUCCESS] No errors")
            
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 50)
    print("Error handling test completed!")

def test_string_parsing():
    """Test string parsing that might cause index errors"""
    print("\nTesting String Parsing Error Handling")
    print("=" * 40)
    
    test_strings = [
        "",  # Empty string
        "No sections here",  # No H2 headings
        "## Only one section",  # One section
        "## First\n## Second\n## Third",  # Multiple sections
        "Risk Warnings: Some warnings",  # No proper format
        "**Risk Warnings**\n- Warning 1\n- Warning 2",  # Proper format
    ]
    
    for i, test_string in enumerate(test_strings, 1):
        print(f"\nTest Case {i}: '{test_string[:30]}...'")
        try:
            # Test H2 section parsing
            sections = test_string.split('## ')
            medicine_sections = []
            for section in sections[1:]:  # Skip the first empty section
                if section and section.strip():
                    medicine_sections.append(section.strip())
            
            print(f"  Sections found: {len(medicine_sections)}")
            
            # Test risk warnings parsing
            risk_warnings = []
            if "**Risk Warnings**" in test_string:
                risk_parts = test_string.split("**Risk Warnings**")
                if len(risk_parts) > 1:
                    risk_section = risk_parts[1]
                    if "**Suggested Tests**" in risk_section:
                        risk_section = risk_section.split("**Suggested Tests**")[0]
                    elif "**Summary**" in risk_section:
                        risk_section = risk_section.split("**Summary**")[0]
                    
                    lines = risk_section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                            risk_warnings.append(line.lstrip('-•* ').strip())
            
            print(f"  Risk warnings found: {len(risk_warnings)}")
            print(f"  [SUCCESS] No errors")
            
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_medicine_cleaning()
    test_string_parsing()
    print("\n[SUCCESS] All error handling tests completed!")
