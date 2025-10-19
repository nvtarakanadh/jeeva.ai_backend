import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
from pathlib import Path
import io

# Third-party imports
import google.generativeai as genai
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# PDF processing imports
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalReportScanner:
    """AI-powered medical report analysis system using Gemini AI"""
    
    def __init__(self, api_key: str):
        """Initialize the scanner with Gemini API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.analysis_history = []
        
        # Medical reference ranges for common tests
        self.reference_ranges = {
            'hemoglobin': {'male': (13.0, 17.0), 'female': (12.0, 15.5)},
            'glucose_fasting': (70, 100),
            'hba1c': (4.0, 5.6),
            'cholesterol_total': (0, 200),
            'ldl_cholesterol': (0, 100),
            'hdl_cholesterol': {'male': 40, 'female': 50},
            'triglycerides': (0, 150),
            'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1)},
            'tsh': (0.55, 4.78),
            'vitamin_d': (75, 250),
            'vitamin_b12': (211, 911)
        }
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file using multiple methods"""
        if not PDF_AVAILABLE:
            return "PDF processing libraries not available. Please install PyPDF2 and pdfplumber."
        
        extracted_text = ""
        
        try:
            # Method 1: Try pdfplumber first (better for complex layouts)
            pdf_file.seek(0)  # Reset file pointer
            with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += f"\n--- Page {page_num + 1} ---\n"
                            extracted_text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
            
            # If pdfplumber got good results, return it
            if len(extracted_text.strip()) > 50:
                logger.info(f"Successfully extracted {len(extracted_text)} characters using pdfplumber")
                return extracted_text.strip()
            
            # Method 2: Fallback to PyPDF2
            pdf_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1} with PyPDF2: {e}")
                    continue
            
            if extracted_text.strip():
                logger.info(f"Successfully extracted {len(extracted_text)} characters using PyPDF2")
                return extracted_text.strip()
            else:
                return "No text could be extracted from the PDF. The PDF might contain only images or be password-protected."
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"Error processing PDF: {str(e)}"
    
    def extract_text_from_image(self, image_bytes) -> str:
        """Extract text from medical report image using Google Vision API via Gemini"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            prompt = """
            Extract all text from this medical report image. 
            Maintain the structure and formatting as much as possible.
            Include all test names, values, reference ranges, and any notes.
            Focus on numerical values and their associated test names.
            """
            
            response = self.model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def process_uploaded_file(self, uploaded_file) -> str:
        """Process uploaded file (PDF, Image, or Text) and extract text"""
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            logger.info("📄 Processing PDF file...")
            extracted_text = self.extract_text_from_pdf(uploaded_file)
            return extracted_text
            
        elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']:
            logger.info("🖼️ Processing image file...")
            
            # Read file bytes
            file_bytes = uploaded_file.read()
            extracted_text = self.extract_text_from_image(file_bytes)
            return extracted_text
            
        elif file_extension in ['txt', 'text']:
            logger.info("📝 Processing text file...")
            try:
                # Reset file pointer and read as text
                uploaded_file.seek(0)
                file_content = uploaded_file.read()
                
                # Try to decode as UTF-8, fallback to other encodings if needed
                try:
                    extracted_text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        extracted_text = file_content.decode('latin-1')
                    except UnicodeDecodeError:
                        extracted_text = file_content.decode('utf-8', errors='ignore')
                
                logger.info(f"Successfully extracted {len(extracted_text)} characters from text file")
                return extracted_text
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                return f"Error reading text file: {str(e)}"
        
        else:
            return f"Unsupported file format: {file_extension}. Please upload PDF, PNG, JPG, JPEG, or TXT files."
    
    def clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from AI response"""
        # Remove markdown code blocks
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.rfind('```')
            if end > start:
                response_text = response_text[start:end]
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.rfind('```')
            if end > start:
                response_text = response_text[start:end]
        
        # Remove any leading/trailing whitespace
        response_text = response_text.strip()
        
        # Try to find JSON-like content if not already clean
        if not response_text.startswith('{'):
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
        
        return response_text
    
    def parse_medical_data(self, text: str) -> Dict:
        """Parse extracted text to identify medical parameters"""
        prompt = f"""
        Analyze this medical report text and extract structured information. This appears to be a comprehensive lab report.
        
        Text to analyze:
        {text}
        
        Please provide a JSON response with exactly this structure:
        {{
            "patient_info": {{
                "name": "patient name if available, otherwise 'Not specified'",
                "age": "age if available, otherwise 'Not specified'",
                "gender": "gender if available, otherwise 'Not specified'",
                "report_date": "date if available, otherwise 'Not specified'",
                "lab_number": "lab number if available, otherwise 'Not specified'"
            }},
            "test_categories": [
                {{
                    "category": "test category name (e.g., 'Complete Blood Count', 'Liver Function', 'Lipid Profile')",
                    "tests": [
                        {{
                            "test_name": "name of test",
                            "value": "measured value",
                            "unit": "unit of measurement",
                            "reference_range": "normal range",
                            "status": "normal/abnormal/high/low/borderline"
                        }}
                    ]
                }}
            ],
            "abnormal_findings": [
                "list of abnormal test results with brief description"
            ],
            "critical_values": [
                "list of any critical or extremely abnormal values"
            ]
        }}
        
        Important guidelines:
        - Look for common lab categories like CBC, Liver Panel, Kidney Panel, Lipid Screen, Thyroid Profile, HbA1c, Vitamins
        - Pay attention to numerical values and their units
        - Compare values to reference ranges when provided
        - If no test results are found, include an empty array for test_categories
        - Always include all required fields even if empty or "Not specified"
        - Only return valid JSON, no additional text or explanations
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                json_text = self.clean_json_response(response.text)
                
                # Log the raw response for debugging
                logger.info(f"Attempt {attempt + 1} - Parsing medical data...")
                
                # Parse JSON
                parsed_data = json.loads(json_text)
                
                # Validate structure
                if self.validate_parsed_data(parsed_data):
                    logger.info("Successfully parsed and validated medical data")
                    # Enhance with status analysis
                    parsed_data = self.enhance_test_status(parsed_data)
                    return parsed_data
                else:
                    logger.warning(f"Attempt {attempt + 1} - Invalid data structure, retrying...")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Attempt {attempt + 1} - JSON decode error: {e}")
                if attempt == max_retries - 1:
                    return self.create_fallback_structure(text)
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} - Error parsing medical data: {e}")
                if attempt == max_retries - 1:
                    return self.create_fallback_structure(text)
        
        return self.create_fallback_structure(text)
    
    def enhance_test_status(self, parsed_data: Dict) -> Dict:
        """Enhance test results with improved status analysis"""
        for category in parsed_data.get('test_categories', []):
            for test in category.get('tests', []):
                test_name = test.get('test_name', '').lower()
                value_str = test.get('value', '')
                
                # Try to extract numeric value
                try:
                    if isinstance(value_str, (int, float)):
                        value = float(value_str)
                    else:
                        # Extract first number from string
                        numbers = re.findall(r'[\d.]+', str(value_str))
                        if numbers:
                            value = float(numbers[0])
                        else:
                            continue
                    
                    # Enhanced status determination based on known ranges
                    if 'hba1c' in test_name or 'glycosylated hemoglobin' in test_name:
                        if value >= 6.5:
                            test['status'] = 'high'
                            test['clinical_significance'] = 'Suggests diabetes'
                        elif value >= 5.7:
                            test['status'] = 'borderline'
                            test['clinical_significance'] = 'Prediabetic range'
                        else:
                            test['status'] = 'normal'
                    
                    elif 'glucose' in test_name and 'fasting' in test_name:
                        if value >= 126:
                            test['status'] = 'high'
                            test['clinical_significance'] = 'Diabetic range'
                        elif value >= 100:
                            test['status'] = 'borderline'
                            test['clinical_significance'] = 'Impaired fasting glucose'
                        else:
                            test['status'] = 'normal'
                    
                    elif 'cholesterol' in test_name and 'total' in test_name:
                        if value >= 240:
                            test['status'] = 'high'
                            test['clinical_significance'] = 'High cardiovascular risk'
                        elif value >= 200:
                            test['status'] = 'borderline'
                            test['clinical_significance'] = 'Borderline high'
                        else:
                            test['status'] = 'normal'
                    
                except (ValueError, TypeError):
                    continue
        
        return parsed_data
    
    def validate_parsed_data(self, data: Dict) -> bool:
        """Validate the structure of parsed medical data"""
        required_keys = ['patient_info', 'test_categories', 'abnormal_findings']
        
        # Check if all required keys exist
        if not all(key in data for key in required_keys):
            return False
        
        # Check patient_info structure
        if not isinstance(data['patient_info'], dict):
            return False
        
        # Check test_categories structure
        if not isinstance(data['test_categories'], list):
            return False
        
        # Check abnormal_findings structure
        if not isinstance(data['abnormal_findings'], list):
            return False
        
        return True
    
    def create_fallback_structure(self, original_text: str) -> Dict:
        """Create a basic fallback structure when parsing fails"""
        logger.info("Creating fallback structure for medical data")
        
        # Try to extract some basic information using simple regex
        lines = original_text.split('\n')
        potential_tests = []
        patient_name = "Not specified"
        patient_age = "Not specified"
        patient_gender = "Not specified"
        
        # Try to extract patient info
        for line in lines[:20]:  # Check first 20 lines
            if 'Mr.' in line or 'Mrs.' in line or 'Ms.' in line:
                name_match = re.search(r'(Mr\.|Mrs\.|Ms\.)\s+([A-Za-z\s]+)', line)
                if name_match:
                    patient_name = name_match.group(0).strip()
            
            if 'Years' in line or 'years' in line:
                age_match = re.search(r'(\d+)\s+[Yy]ears', line)
                if age_match:
                    patient_age = age_match.group(1) + " years"
            
            if 'Male' in line or 'Female' in line:
                gender_match = re.search(r'(Male|Female)', line)
                if gender_match:
                    patient_gender = gender_match.group(1)
        
        # Extract test results
        for line in lines:
            # Look for patterns like "TestName: value unit (range)"
            test_pattern = r'([A-Za-z\s]+):\s*([0-9.]+)\s*([A-Za-z/%]*)\s*\(?([0-9.-]+\s*[-–]\s*[0-9.-]+)?\)?'
            match = re.search(test_pattern, line)
            if match:
                test_name, value, unit, ref_range = match.groups()
                potential_tests.append({
                    "test_name": test_name.strip(),
                    "value": value,
                    "unit": unit or "",
                    "reference_range": ref_range or "Not specified",
                    "status": "unknown"
                })
        
        return {
            "patient_info": {
                "name": patient_name,
                "age": patient_age, 
                "gender": patient_gender,
                "report_date": "Not specified",
                "lab_number": "Not specified"
            },
            "test_categories": [{
                "category": "General Tests",
                "tests": potential_tests[:15]  # Limit to first 15 found tests
            }] if potential_tests else [],
            "abnormal_findings": ["Unable to automatically detect abnormal findings - manual review recommended"],
            "critical_values": []
        }
    
    def analyze_diagnosis(self, parsed_data: Dict) -> Dict:
        """Generate AI-powered diagnosis insights"""
        prompt = f"""
        As a medical AI assistant, analyze these comprehensive lab results and provide detailed insights:
        
        {json.dumps(parsed_data, indent=2)}
        
        Provide analysis in the following JSON format:
        {{
            "risk_assessment": {{
                "overall_risk": "low/moderate/high",
                "cardiovascular_risk": "low/moderate/high",
                "diabetes_risk": "low/moderate/high",
                "risk_factors": ["list identified risk factors"]
            }},
            "potential_conditions": [
                {{
                    "condition": "condition name",
                    "probability": "low/moderate/high",
                    "supporting_evidence": ["specific test results that support this"],
                    "description": "brief clinical explanation"
                }}
            ],
            "recommendations": [
                {{
                    "category": "lifestyle/dietary/medical/follow-up",
                    "recommendation": "specific actionable recommendation",
                    "priority": "low/medium/high",
                    "rationale": "why this recommendation is important"
                }}
            ],
            "follow_up_tests": [
                "suggested additional tests with rationale"
            ],
            "red_flags": [
                "critical findings requiring immediate medical attention"
            ],
            "positive_findings": [
                "normal or good results worth highlighting"
            ],
            "summary": "A comprehensive overall assessment summary including key findings and next steps"
        }}
        
        Consider:
        - HbA1c levels for diabetes assessment
        - Lipid profile for cardiovascular risk
        - Liver and kidney function markers
        - Vitamin levels and deficiencies
        - Blood count abnormalities
        - Thyroid function
        
        Important: Only return valid JSON, include disclaimer about professional medical consultation
        """
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                json_text = self.clean_json_response(response.text)
                
                logger.info(f"Diagnosis attempt {attempt + 1} - Analyzing comprehensive report...")
                
                diagnosis = json.loads(json_text)
                
                # Validate diagnosis structure
                if self.validate_diagnosis_data(diagnosis):
                    return diagnosis
                else:
                    logger.warning(f"Diagnosis attempt {attempt + 1} - Invalid structure, retrying...")
                    
            except Exception as e:
                logger.error(f"Diagnosis attempt {attempt + 1} - Error: {e}")
                if attempt == max_retries - 1:
                    return self.create_fallback_diagnosis()
        
        return self.create_fallback_diagnosis()
    
    def validate_diagnosis_data(self, data: Dict) -> bool:
        """Validate diagnosis data structure"""
        required_keys = ['risk_assessment', 'potential_conditions', 'recommendations', 
                        'follow_up_tests', 'red_flags', 'summary']
        return all(key in data for key in required_keys)
    
    def create_fallback_diagnosis(self) -> Dict:
        """Create fallback diagnosis when AI analysis fails"""
        return {
            "risk_assessment": {
                "overall_risk": "moderate",
                "cardiovascular_risk": "moderate",
                "diabetes_risk": "moderate",
                "risk_factors": ["Unable to complete automated risk assessment"]
            },
            "potential_conditions": [],
            "recommendations": [{
                "category": "medical",
                "recommendation": "Consult with healthcare provider for proper interpretation",
                "priority": "high",
                "rationale": "Professional medical interpretation required"
            }],
            "follow_up_tests": [],
            "red_flags": [],
            "positive_findings": [],
            "summary": "Automated analysis could not be completed. Please consult with a qualified healthcare professional for proper interpretation of these comprehensive lab results."
        }
    
    def generate_comprehensive_report(self, parsed_data: Dict, diagnosis: Dict) -> str:
        """Generate comprehensive medical report with enhanced formatting"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# 🏥 COMPREHENSIVE MEDICAL REPORT ANALYSIS
**Generated on:** {timestamp}  
**Analysis System:** AI Medical Report Scanner v2.0  
**Report Type:** Comprehensive Lab Panel Analysis

---

## ⚠️ MEDICAL DISCLAIMER
This analysis is generated by AI for educational and informational purposes only. 
**ALWAYS consult with qualified healthcare professionals for medical decisions and treatment.**

---

## 👤 PATIENT INFORMATION
"""
        
        if 'patient_info' in parsed_data:
            patient = parsed_data['patient_info']
            for key, value in patient.items():
                if value and value != "Not specified":
                    icon = {"name": "👤", "age": "📅", "gender": "⚧", "report_date": "📋", "lab_number": "🆔"}.get(key, "📌")
                    report += f"{icon} **{key.replace('_', ' ').title()}:** {value}\n"
        
        # Risk Assessment Summary
        if diagnosis and 'risk_assessment' in diagnosis:
            risk = diagnosis['risk_assessment']
            report += f"\n## 🎯 RISK ASSESSMENT SUMMARY\n"
            
            overall_risk = risk.get('overall_risk', 'moderate')
            risk_colors = {"low": "🟢", "moderate": "🟡", "high": "🔴"}
            report += f"**Overall Health Risk:** {risk_colors.get(overall_risk, '🟡')} **{overall_risk.upper()}**\n\n"
            
            # Specific risk categories
            if 'cardiovascular_risk' in risk:
                cv_risk = risk['cardiovascular_risk']
                report += f"**Cardiovascular Risk:** {risk_colors.get(cv_risk, '🟡')} {cv_risk.title()}\n"
            
            if 'diabetes_risk' in risk:
                dm_risk = risk['diabetes_risk']
                report += f"**Diabetes Risk:** {risk_colors.get(dm_risk, '🟡')} {dm_risk.title()}\n"
        
        # Test Results by Category
        report += "\n## 📊 DETAILED TEST RESULTS\n"
        
        if 'test_categories' in parsed_data and parsed_data['test_categories']:
            for category in parsed_data['test_categories']:
                if category.get('tests'):
                    report += f"\n### 🔬 {category.get('category', 'Unknown Category')}\n"
                    
                    # Create a table-like format
                    report += "| Test | Value | Reference Range | Status |\n"
                    report += "|------|-------|-----------------|--------|\n"
                    
                    for test in category['tests']:
                        test_name = test.get('test_name', 'Unknown Test')
                        value = f"{test.get('value', 'N/A')} {test.get('unit', '')}"
                        ref_range = test.get('reference_range', 'N/A')
                        status = test.get('status', 'unknown')
                        
                        status_icons = {
                            'normal': '🟢 Normal',
                            'abnormal': '🔴 Abnormal', 
                            'high': '🔺 High',
                            'low': '🔻 Low',
                            'borderline': '🟡 Borderline',
                            'unknown': '⚪ Unknown'
                        }
                        status_display = status_icons.get(status, '⚪ Unknown')
                        
                        report += f"| {test_name} | {value} | {ref_range} | {status_display} |\n"
                    
                    report += "\n"
        else:
            report += "No structured test results could be extracted from the report.\n"
        
        # Critical and Abnormal Findings
        if diagnosis and diagnosis.get('red_flags'):
            report += "\n## 🚨 CRITICAL FINDINGS - IMMEDIATE ATTENTION REQUIRED\n"
            for flag in diagnosis['red_flags']:
                report += f"- ⚠️ **{flag}**\n"
            report += "\n**🚑 ACTION REQUIRED:** Contact your healthcare provider immediately.\n"
        
        if 'abnormal_findings' in parsed_data and parsed_data['abnormal_findings']:
            report += "\n## ⚠️ ABNORMAL FINDINGS\n"
            for finding in parsed_data['abnormal_findings']:
                report += f"- 🔴 {finding}\n"
        
        # Positive Findings
        if diagnosis and diagnosis.get('positive_findings'):
            report += "\n## ✅ POSITIVE FINDINGS\n"
            for finding in diagnosis['positive_findings']:
                report += f"- 🟢 {finding}\n"
        
        # AI Analysis and Insights
        if diagnosis:
            if diagnosis.get('potential_conditions'):
                report += "\n## 🔍 POTENTIAL CONDITIONS TO DISCUSS WITH YOUR DOCTOR\n"
                for condition in diagnosis['potential_conditions']:
                    prob_icons = {"low": "🟢 Low", "moderate": "🟡 Moderate", "high": "🔴 High"}
                    prob_display = prob_icons.get(condition.get('probability', 'moderate'), '🟡 Moderate')
                    
                    report += f"\n**{condition.get('condition', 'Unknown')}** - Probability: {prob_display}\n"
                    report += f"- **Description:** {condition.get('description', 'No description available')}\n"
                    if condition.get('supporting_evidence'):
                        report += f"- **Supporting Evidence:** {', '.join(condition['supporting_evidence'])}\n"
            
            # Comprehensive Recommendations
            if diagnosis.get('recommendations'):
                report += "\n## 💡 PERSONALIZED RECOMMENDATIONS\n"
                categories = {}
                for rec in diagnosis['recommendations']:
                    cat = rec.get('category', 'general').title()
                    if cat not in categories:
                        categories[cat] = []
                    
                    priority_icons = {"low": "🔵", "medium": "🟡", "high": "🔴"}
                    priority = rec.get('priority', 'medium')
                    priority_display = priority_icons.get(priority, '🟡')
                    
                    rec_text = f"{priority_display} **{rec.get('recommendation', '')}**"
                    if rec.get('rationale'):
                        rec_text += f"\n  - *Rationale:* {rec['rationale']}"
                    
                    categories[cat].append(rec_text)
                
                category_icons = {
                    'Lifestyle': '🏃‍♂️',
                    'Dietary': '🥗',
                    'Medical': '⚕️',
                    'Follow-Up': '📅',
                    'General': '📌'
                }
                
                for cat, recs in categories.items():
                    icon = category_icons.get(cat, '📌')
                    report += f"\n### {icon} {cat} Recommendations\n"
                    for rec in recs:
                        report += f"- {rec}\n"
            
            # Follow-up Tests
            if diagnosis.get('follow_up_tests'):
                report += "\n## 🧪 SUGGESTED FOLLOW-UP TESTS\n"
                for test in diagnosis['follow_up_tests']:
                    report += f"- 📋 {test}\n"
            
            # Executive Summary
            if diagnosis.get('summary'):
                report += f"\n## 📋 EXECUTIVE SUMMARY\n"
                report += f"{diagnosis['summary']}\n"
        
        # Footer
        report += "\n---\n"
        report += "## 📞 NEXT STEPS\n"
        report += "1. **Schedule an appointment** with your healthcare provider to discuss these results\n"
        report += "2. **Bring this report** to your medical consultation\n"
        report += "3. **Ask questions** about any findings you don't understand\n"
        report += "4. **Follow recommended** lifestyle modifications and follow-up tests\n\n"
        
        report += "**🔒 Privacy Note:** Keep this report confidential and share only with authorized healthcare providers.\n"
        report += "**⚕️ Remember:** This AI analysis supports but does not replace professional medical advice.\n"
        
        return report
