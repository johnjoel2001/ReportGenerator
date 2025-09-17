# import streamlit as st
# import requests
# import json
# import pandas as pd
# import io
# import base64
# from datetime import datetime
# import traceback
# import re

# # Using fpdf2 for better PDF generation (easier installation)
# try:
#     from fpdf import FPDF
#     FPDF_AVAILABLE = True
# except ImportError:
#     FPDF_AVAILABLE = False
#     st.error("FPDF2 not available. Please install with: pip install fpdf2")

# # API URLs with correct endpoints
# API_CONFIGS = {
#     'pdf_parsing': {
#         'base_url': 'https://web-production-7060.up.railway.app',
#         'endpoint': '/pdf-parse',
#         'method': 'POST'
#     },
#     'score_recommendations': {
#         'base_url': 'https://web-production-1abf.up.railway.app',
#         'endpoint': '/recommend',
#         'method': 'POST'
#     },
#     'iui_ivf': {
#         'base_url': 'https://web-production-91c09.up.railway.app',
#         'endpoint': '/iui-ivf-explain',
#         'method': 'POST'
#     },
#     'morphology': {
#         'base_url': 'https://web-production-d106c.up.railway.app',
#         'endpoint': '/recommend-morphology',
#         'method': 'POST'
#     }
# }

# class CleanPDFReportGenerator:
#     def __init__(self):
#         self.pdf = FPDF()
#         self.pdf.set_auto_page_break(auto=True, margin=15)
        
#         # Colors
#         self.blue = (44, 90, 160)
#         self.red = (220, 53, 69)
#         self.green = (40, 167, 69)
#         self.gray = (108, 117, 125)
#         self.light_gray = (248, 249, 250)
        
#     def clean_text(self, text):
#         """Clean and format text, handling asterisks and special characters"""
#         if not isinstance(text, str):
#             return str(text)
        
#         # Remove problematic characters
#         text = text.encode('ascii', 'ignore').decode('ascii')
        
#         # Handle asterisks - convert to bullet points or emphasis
#         text = re.sub(r'\*\*\*+', '• ', text)
#         text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove double asterisks but keep content
#         text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove single asterisks but keep content
        
#         # Add line breaks after numbered items (1., 2., 3., etc.)
#         text = re.sub(r'(\d+\.\s)', r'\n\1', text)
        
#         # Clean up multiple spaces but preserve line breaks
#         text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
#         text = re.sub(r'\n\s+', '\n', text)  # Remove spaces at beginning of new lines
#         text = text.strip()
        
#         return text
    
#     def add_header(self):
#         """Add report header"""
#         self.pdf.add_page()
        
#         # Title
#         self.pdf.set_font('Arial', 'B', 24)
#         self.pdf.set_text_color(*self.blue)
#         self.pdf.cell(0, 15, 'FERTILITY ANALYSIS REPORT', 0, 1, 'C')
        
#         # Line under title
#         self.pdf.set_draw_color(*self.blue)
#         self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
#         self.pdf.ln(10)
        
#         # Timestamp
#         self.pdf.set_font('Arial', '', 10)
#         self.pdf.set_text_color(*self.gray)
#         timestamp = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
#         self.pdf.cell(0, 5, timestamp, 0, 1, 'C')
#         self.pdf.ln(15)
    
#     def add_section_header(self, title):
#         """Add a section header with colored background"""
#         self.pdf.ln(10)
        
#         # Background rectangle
#         self.pdf.set_fill_color(*self.light_gray)
#         self.pdf.rect(10, self.pdf.get_y(), 190, 12, 'F')
        
#         # Left border
#         self.pdf.set_fill_color(*self.red)
#         self.pdf.rect(10, self.pdf.get_y(), 3, 12, 'F')
        
#         # Text
#         self.pdf.set_font('Arial', 'B', 14)
#         self.pdf.set_text_color(*self.red)
#         self.pdf.cell(0, 12, f"  {title}", 0, 1, 'L')
#         self.pdf.ln(5)
    
#     def add_subsection_header(self, title):
#         """Add a subsection header"""
#         self.pdf.ln(5)
#         self.pdf.set_font('Arial', 'B', 12)
#         self.pdf.set_text_color(*self.blue)
#         self.pdf.cell(0, 8, title, 0, 1, 'L')
        
#         # Underline
#         self.pdf.set_draw_color(*self.blue)
#         self.pdf.line(10, self.pdf.get_y(), 100, self.pdf.get_y())
#         self.pdf.ln(5)
    
#     def add_info_table(self, data_dict, title=None):
#         """Add a two-column information table"""
#         if title:
#             self.add_subsection_header(title)
        
#         self.pdf.set_font('Arial', '', 10)
        
#         for key, value in data_dict.items():
#             # Clean the data
#             clean_key = self.clean_text(key.replace('_', ' ').title())
#             clean_value = self.clean_text(str(value))
            
#             # Key column (bold)
#             self.pdf.set_font('Arial', 'B', 10)
#             self.pdf.set_text_color(0, 0, 0)
#             self.pdf.cell(60, 8, clean_key + ":", 1, 0, 'L')
            
#             # Value column
#             self.pdf.set_font('Arial', '', 10)
#             self.pdf.cell(120, 8, clean_value, 1, 1, 'L')
        
#         self.pdf.ln(5)
    
#     def add_analysis_table(self, headers, data):
#         """Add analysis table with headers"""
#         # Table headers
#         self.pdf.set_font('Arial', 'B', 10)
#         self.pdf.set_fill_color(*self.blue)
#         self.pdf.set_text_color(255, 255, 255)
        
#         col_widths = [50, 30, 40, 30] if len(headers) == 4 else [40, 30, 30, 30, 30]
        
#         for i, header in enumerate(headers):
#             self.pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
#         self.pdf.ln()
        
#         # Table data
#         self.pdf.set_font('Arial', '', 9)
#         self.pdf.set_text_color(0, 0, 0)
        
#         for row in data:
#             for i, cell in enumerate(row):
#                 clean_cell = self.clean_text(str(cell))
                
#                 # Color code status
#                 if i == len(row) - 1 and clean_cell in ['Low', 'High']:
#                     self.pdf.set_text_color(*self.red)
#                 elif i == len(row) - 1 and clean_cell == 'Normal':
#                     self.pdf.set_text_color(*self.green)
#                 else:
#                     self.pdf.set_text_color(0, 0, 0)
                
#                 self.pdf.cell(col_widths[i], 8, clean_cell, 1, 0, 'C')
#             self.pdf.ln()
        
#         self.pdf.ln(5)
    
#     def add_fertility_score_box(self, score):
#         """Add highlighted fertility score box"""
#         self.pdf.ln(5)
        
#         # Score box
#         self.pdf.set_fill_color(255, 243, 205)  # Light yellow
#         self.pdf.set_draw_color(*self.red)
#         self.pdf.rect(10, self.pdf.get_y(), 190, 20, 'DF')
        
#         # Score text
#         self.pdf.set_font('Arial', 'B', 16)
#         self.pdf.set_text_color(*self.red)
#         self.pdf.cell(0, 20, f"Predicted Fertility Score: {score}%", 0, 1, 'C')
#         self.pdf.ln(5)
    
#     def add_interpretation_box(self):
#         """Add fertility score interpretation"""
#         self.pdf.set_fill_color(231, 243, 255)  # Light blue
#         self.pdf.set_draw_color(*self.blue)
#         self.pdf.rect(10, self.pdf.get_y(), 190, 25, 'DF')
        
#         self.pdf.set_font('Arial', 'B', 10)
#         self.pdf.set_text_color(*self.blue)
#         self.pdf.cell(0, 8, "About the Fertility Score:", 0, 1, 'L')
        
#         self.pdf.set_font('Arial', '', 9)
#         self.pdf.set_text_color(0, 0, 0)
#         text = "The fertility score percentage represents the estimated probability of achieving"
#         self.pdf.cell(0, 6, text, 0, 1, 'L')
#         text2 = "a natural pregnancy within 12 months, based on semen parameter analysis."
#         self.pdf.cell(0, 6, text2, 0, 1, 'L')
#         self.pdf.ln(10)
    
#     def add_text_content(self, text, max_width=180):
#         """Add formatted text content with proper line breaks"""
#         if not text:
#             return
            
#         clean_text = self.clean_text(text)
        
#         # Split into paragraphs
#         paragraphs = clean_text.split('\n')
        
#         self.pdf.set_font('Arial', '', 10)
#         self.pdf.set_text_color(0, 0, 0)
        
#         for paragraph in paragraphs:
#             if not paragraph.strip():
#                 continue
                
#             # Handle bullet points
#             if paragraph.strip().startswith('•'):
#                 self.pdf.cell(5, 6, '•', 0, 0, 'L')
#                 paragraph = paragraph.strip()[1:].strip()
            
#             # Word wrap
#             words = paragraph.split()
#             line = ""
            
#             for word in words:
#                 test_line = f"{line} {word}".strip()
#                 if self.pdf.get_string_width(test_line) <= max_width:
#                     line = test_line
#                 else:
#                     if line:
#                         self.pdf.cell(0, 6, line, 0, 1, 'L')
#                     line = word
            
#             if line:
#                 self.pdf.cell(0, 6, line, 0, 1, 'L')
            
#             self.pdf.ln(2)
    
#     def add_recommendation_box(self, title, content):
#         """Add recommendation box with border"""
#         self.pdf.ln(5)
        
#         # Box background
#         self.pdf.set_fill_color(*self.light_gray)
#         self.pdf.set_draw_color(*self.red)
        
#         # Calculate box height based on content
#         y_start = self.pdf.get_y()
        
#         # Title
#         self.pdf.set_font('Arial', 'B', 12)
#         self.pdf.set_text_color(*self.red)
#         self.pdf.cell(0, 10, title, 0, 1, 'L')
        
#         # Content
#         self.pdf.set_x(15)
#         self.add_text_content(content, 175)
        
#         y_end = self.pdf.get_y()
        
#         # Draw box around content
#         self.pdf.rect(10, y_start, 190, y_end - y_start + 5, 'D')
#         self.pdf.ln(10)
    
#     def add_physician_remarks_box(self):
#         """Add empty boxes for physician remarks - Internal and External"""
#         self.add_section_header("PHYSICIAN REMARKS")
        
#         # Internal Remarks
#         self.add_subsection_header("Internal Remarks")
        
#         # Internal remarks box
#         box_height = 60
#         self.pdf.set_draw_color(0, 0, 0)
#         self.pdf.rect(10, self.pdf.get_y(), 190, box_height, 'D')
        
#         # Add lines for writing in internal box
#         y_start = self.pdf.get_y() + 8
#         for i in range(6):
#             y_pos = y_start + (i * 8)
#             if y_pos < self.pdf.get_y() + box_height - 8:
#                 self.pdf.line(15, y_pos, 195, y_pos)
        
#         self.pdf.ln(box_height + 10)
        
#         # External Remarks
#         self.add_subsection_header("External Remarks")
        
#         # External remarks box
#         self.pdf.set_draw_color(0, 0, 0)
#         self.pdf.rect(10, self.pdf.get_y(), 190, box_height, 'D')
        
#         # Add lines for writing in external box
#         y_start = self.pdf.get_y() + 8
#         for i in range(6):
#             y_pos = y_start + (i * 8)
#             if y_pos < self.pdf.get_y() + box_height - 8:
#                 self.pdf.line(15, y_pos, 195, y_pos)
        
#         self.pdf.ln(box_height + 10)
    
#     def determine_status(self, param, value, normal_range):
#         """Determine if parameter is normal, low, or high"""
#         try:
#             if value == 'N/A' or normal_range == 'N/A':
#                 return 'N/A'
            
#             val = float(str(value).replace('%', ''))
            
#             if 'motility' in param.lower() and val < 42:
#                 return 'Low'
#             elif 'concentration' in param.lower() and val < 16:
#                 return 'Low'
#             elif 'volume' in param.lower() and val < 1.4:
#                 return 'Low'
#             elif 'morphology' in param.lower() and val < 4:
#                 return 'Low'
#             else:
#                 return 'Normal'
#         except:
#             return 'N/A'
    
#     def generate_report(self, all_results, filename="analysis_report.pdf"):
#         """Generate the complete PDF report"""
        
#         # Header
#         self.add_header()
        
#         # Patient Information Section
#         if 'pdf_parsing' in all_results:
#             pdf_data = all_results['pdf_parsing']
            
#             self.add_section_header("PATIENT INFORMATION")
            
#             if 'patient_info' in pdf_data:
#                 self.add_info_table(pdf_data['patient_info'])
            
#             if 'collection_info' in pdf_data:
#                 self.add_info_table(pdf_data['collection_info'], "Collection Details")
            
#             # Semen Analysis Results
#             if 'semen_analysis' in pdf_data:
#                 self.pdf.add_page()
#                 self.add_section_header("SEMEN ANALYSIS RESULTS")
                
#                 # Prepare table data
#                 headers = ['Parameter', 'Value', 'Normal Range', 'Status']
#                 table_data = []
                
#                 for key, value in pdf_data['semen_analysis'].items():
#                     if key == 'comments':
#                         continue
                    
#                     param_name = key.replace('_', ' ').title()
                    
#                     if isinstance(value, dict):
#                         param_value = str(value.get('value', 'N/A'))
#                         normal_range = str(value.get('normal_range', 'N/A'))
#                         status = self.determine_status(key, param_value, normal_range)
#                         table_data.append([param_name, param_value, normal_range, status])
#                     else:
#                         table_data.append([param_name, str(value), 'N/A', 'N/A'])
                
#                 self.add_analysis_table(headers, table_data)
        
#         # Fertility Score & Recommendations
#         if 'score_recommendations' in all_results:
#             self.pdf.add_page()
#             self.add_section_header("FERTILITY ASSESSMENT")
            
#             score_data = all_results['score_recommendations']
            
#             # Fertility Score
#             if 'fertility_score' in score_data:
#                 fertility_score = score_data['fertility_score']
#                 self.add_fertility_score_box(fertility_score)
#                 self.add_interpretation_box()
            
#             # Features Analysis
#             if 'features' in score_data:
#                 self.add_subsection_header("Parameter Impact Analysis")
                
#                 headers = ['Parameter', 'Value', 'Impact', 'Direction', 'Strength']
#                 table_data = []
                
#                 for param, details in score_data['features'].items():
#                     if isinstance(details, dict):
#                         value = str(details.get('value', 'N/A'))
#                         impact = str(details.get('impact', 'N/A'))[:6]
#                         direction = str(details.get('direction', 'N/A')).title()
#                         strength = str(details.get('impact_strength', 'N/A'))
#                         table_data.append([param, value, impact, direction, strength])
                
#                 self.add_analysis_table(headers, table_data)
            
#             # Recommendations
#             if 'recommendation' in score_data:
#                 self.add_recommendation_box("CLINICAL RECOMMENDATIONS", score_data['recommendation'])
        
#         # IUI-IVF Analysis
#         if 'iui_ivf' in all_results:
#             self.pdf.add_page()
#             self.add_section_header("TREATMENT OPTIONS ANALYSIS")
            
#             iui_data = all_results['iui_ivf']
#             if 'explanation' in iui_data:
#                 self.add_text_content(iui_data['explanation'])
        
#         # Morphology Analysis
#         if 'morphology' in all_results:
#             self.add_section_header("MORPHOLOGY ASSESSMENT")
            
#             morph_data = all_results['morphology']
#             if 'recommendation' in morph_data:
#                 self.add_text_content(morph_data['recommendation'])
        
#         # Physician Remarks
#         self.add_physician_remarks_box()
        
#         # Return PDF as bytes
#         return bytes(self.pdf.output())

# # Keep all the existing helper functions unchanged
# def test_api_endpoint(api_name, config):
#     """Test API endpoint with different methods"""
#     base_url = config['base_url']
#     endpoint = config.get('endpoint', '')
#     full_url = f"{base_url}{endpoint}"
    
#     st.write(f"Testing {api_name} at: {full_url}")
    
#     # Test different endpoints and methods
#     test_endpoints = ['', '/health', '/status', '/ping', '/docs', '/']
#     test_methods = ['GET', 'POST']
    
#     results = []
    
#     for endpoint in test_endpoints:
#         test_url = f"{base_url}{endpoint}"
#         for method in test_methods:
#             try:
#                 if method == 'GET':
#                     response = requests.get(test_url, timeout=10)
#                 else:
#                     response = requests.post(test_url, timeout=10)
                
#                 results.append({
#                     'URL': test_url,
#                     'Method': method,
#                     'Status': response.status_code,
#                     'Response': response.text[:200] + '...' if len(response.text) > 200 else response.text
#                 })
                
#             except Exception as e:
#                 results.append({
#                     'URL': test_url,
#                     'Method': method,
#                     'Status': 'Error',
#                     'Response': str(e)
#                 })
    
#     return results

# def format_data_for_morphology(pdf_result):
#     """Format PDF parsing result for Morphology API"""
#     try:
#         # Look for morphology value in the PDF parsing result
#         morphology_value = None
        
#         def find_morphology_value(data):
#             """Recursively search for morphology-related values"""
#             if isinstance(data, dict):
#                 for key, value in data.items():
#                     # Look for morphology-related keys
#                     if any(term in key.lower() for term in ['morphology', 'morph', 'normal_forms', 'normal forms']):
#                         if isinstance(value, (int, float)):
#                             return float(value)
#                         elif isinstance(value, str):
#                             try:
#                                 return float(value)
#                             except:
#                                 pass
#                         elif isinstance(value, dict) and 'value' in value:
#                             try:
#                                 return float(value['value'])
#                             except:
#                                 pass
                    
#                     # Recursively search in nested objects
#                     if isinstance(value, dict):
#                         result = find_morphology_value(value)
#                         if result is not None:
#                             return result
            
#             elif isinstance(data, list):
#                 for item in data:
#                     result = find_morphology_value(item)
#                     if result is not None:
#                         return result
            
#             return None
        
#         morphology_value = find_morphology_value(pdf_result)
        
#         # If no morphology value found, use a default
#         if morphology_value is None:
#             morphology_value = 4.0  # Default normal morphology percentage
        
#         # Format data as expected by the API
#         morphology_input = {
#             "semen_analysis": {
#                 "morphology": {
#                     "value": morphology_value
#                 }
#             }
#         }
        
#         return morphology_input
        
#     except Exception as e:
#         # Fallback with default value
#         return {
#             "semen_analysis": {
#                 "morphology": {
#                     "value": 4.0
#                 }
#             }
#         }

# def format_data_for_iui_ivf(recommend_result):
#     """Format recommend API output for IUI-IVF API"""
#     try:
#         # Extract fertility_score from recommend result
#         fertility_score = None
        
#         # Look for fertility_score in various possible locations
#         if isinstance(recommend_result, dict):
#             # Direct fertility_score
#             if 'fertility_score' in recommend_result:
#                 fertility_score = recommend_result['fertility_score']
#             # In scores object
#             elif 'scores' in recommend_result and isinstance(recommend_result['scores'], dict):
#                 fertility_score = recommend_result['scores'].get('fertility_score')
#             # Look for any field with 'fertility' and 'score'
#             else:
#                 for key, value in recommend_result.items():
#                     if 'fertility' in key.lower() and 'score' in key.lower():
#                         fertility_score = value
#                         break
#                     elif isinstance(value, dict):
#                         for sub_key, sub_value in value.items():
#                             if 'fertility' in sub_key.lower() and 'score' in sub_key.lower():
#                                 fertility_score = sub_value
#                                 break
        
#         # Default fertility score if not found
#         if fertility_score is None:
#             fertility_score = 50.0  # Default value
        
#         # Extract features (Volume, Concentration, Motility)
#         features = {}
        
#         # Function to search for feature data
#         def find_feature_data(data, feature_names):
#             """Find value and impact for a feature"""
#             result = {"value": 0.0, "impact": 0.0}
            
#             if isinstance(data, dict):
#                 for key, value in data.items():
#                     # Check if key matches any feature name
#                     for feature_name in feature_names:
#                         if feature_name.lower() in key.lower():
#                             if isinstance(value, dict):
#                                 # If value is a dict, look for 'value' and 'impact'
#                                 if 'value' in value:
#                                     result['value'] = float(value['value'])
#                                 if 'impact' in value:
#                                     result['impact'] = float(value['impact'])
#                             elif isinstance(value, (int, float)):
#                                 # If value is a number, use it as value
#                                 result['value'] = float(value)
#                             break
                    
#                     # Recursively search in nested objects
#                     if isinstance(value, dict):
#                         nested_result = find_feature_data(value, feature_names)
#                         if nested_result['value'] != 0.0 or nested_result['impact'] != 0.0:
#                             result = nested_result
#                             break
            
#             return result
        
#         # Search for Volume data
#         volume_names = ['volume', 'vol']
#         features['Volume'] = find_feature_data(recommend_result, volume_names)
        
#         # Search for Concentration data
#         concentration_names = ['concentration', 'conc', 'density']
#         features['Concentration'] = find_feature_data(recommend_result, concentration_names)
        
#         # Search for Motility data
#         motility_names = ['motility', 'mobility', 'movement']
#         features['Motility'] = find_feature_data(recommend_result, motility_names)
        
#         # If no features found, use defaults based on fertility score
#         if all(f['value'] == 0.0 and f['impact'] == 0.0 for f in features.values()):
#             # Generate reasonable defaults based on fertility score
#             base_impact = (fertility_score - 50) / 100  # Normalize around 50
            
#             features = {
#                 'Volume': {
#                     'value': max(1.0, fertility_score / 20),  # 1-5 range
#                     'impact': base_impact * 0.1
#                 },
#                 'Concentration': {
#                     'value': max(5.0, fertility_score / 3),  # 5-33 range
#                     'impact': base_impact * 0.6
#                 },
#                 'Motility': {
#                     'value': max(10.0, fertility_score * 0.8),  # 10-80 range
#                     'impact': base_impact * 0.8
#                 }
#             }
        
#         # Format final result
#         iui_input = {
#             "fertility_score": float(fertility_score),
#             "features": features
#         }
        
#         return iui_input
        
#     except Exception as e:
#         # Fallback with default values
#         return {
#             "fertility_score": 50.0,
#             "features": {
#                 "Volume": {"value": 3.0, "impact": 0.1},
#                 "Concentration": {"value": 15.0, "impact": 0.3},
#                 "Motility": {"value": 40.0, "impact": 0.5}
#             }
#         }

# def preprocess_data_for_api(data, api_name):
#     """Preprocess data to ensure correct types for each API"""
#     if not isinstance(data, dict):
#         return data
    
#     processed_data = data.copy()
    
#     # Common preprocessing - convert numeric strings to numbers
#     def convert_numeric_strings(obj):
#         if isinstance(obj, dict):
#             result = {}
#             for key, value in obj.items():
#                 result[key] = convert_numeric_strings(value)
#             return result
#         elif isinstance(obj, list):
#             return [convert_numeric_strings(item) for item in obj]
#         elif isinstance(obj, str):
#             # Try to convert string to number
#             try:
#                 # First try integer
#                 if obj.isdigit() or (obj.startswith('-') and obj[1:].isdigit()):
#                     return int(obj)
#                 # Try float (including decimal numbers)
#                 if '.' in obj or 'e' in obj.lower():
#                     return float(obj)
#                 # Try float anyway for safety
#                 return float(obj)
#             except (ValueError, AttributeError):
#                 return obj
#         else:
#             return obj
    
#     processed_data = convert_numeric_strings(processed_data)
#     return processed_data

# def call_api(api_name, config, files=None, data=None, custom_endpoint=None):
#     """Make API call with error handling and flexible configuration"""
#     base_url = config['base_url']
#     endpoint = custom_endpoint or config.get('endpoint', '')
#     method = config.get('method', 'POST')
#     full_url = f"{base_url}{endpoint}"
    
#     try:
#         st.write(f"Calling {api_name} API: {method} {full_url}")
        
#         # Preprocess data if it's JSON
#         if data and not files:
#             data = preprocess_data_for_api(data, api_name)
#             st.write(f"Preprocessed data sample: {str(data)[:200]}...")
        
#         if method.upper() == 'GET':
#             response = requests.get(full_url, timeout=30)
#         else:  # POST
#             if files:
#                 # Try different file parameter names and content types
#                 file_variations = [
#                     {'file': files['file']},  # Standard 'file'
#                     {'pdf': files['file']},   # Some APIs use 'pdf'
#                     {'document': files['file']}, # Some use 'document'
#                     {'upload': files['file']},   # Some use 'upload'
#                 ]
                
#                 # Try different approaches for 415 errors
#                 for i, file_data in enumerate(file_variations):
#                     try:
#                         if i > 0:  # Only show retry attempts
#                             st.write(f"Retry {i}: Trying different file parameter...")
                        
#                         response = requests.post(full_url, files=file_data, data=data, timeout=30)
                        
#                         if response.status_code != 415:  # If not unsupported media type, break
#                             break
                            
#                     except Exception as retry_error:
#                         continue
                        
#                 # If still 415, try with different content type headers
#                 if response.status_code == 415:
#                     st.write("Trying with explicit content-type headers...")
#                     headers = {'Content-Type': 'multipart/form-data'}
#                     try:
#                         response = requests.post(full_url, files=files, data=data, headers=headers, timeout=30)
#                     except:
#                         pass
#             else:
#                 response = requests.post(full_url, json=data, timeout=30)
        
#         st.write(f"Response status: {response.status_code}")
        
#         if response.status_code == 404:
#             st.warning(f"404 Error - Endpoint not found. Try testing different endpoints for {api_name}")
#             return None
#         elif response.status_code == 405:
#             st.warning(f"405 Error - Method not allowed. Try different HTTP method for {api_name}")
#             return None
#         elif response.status_code == 415:
#             st.warning(f"415 Error - Unsupported Media Type. The {api_name} API expects a different file format or parameter name")
#             st.write("Response:", response.text[:500])
#             return None
#         elif response.status_code == 500:
#             st.warning(f"500 Error - Internal Server Error. The {api_name} service has an internal issue")
#             st.write("Response:", response.text[:500])
#             return None
#         elif response.status_code == 502:
#             st.warning(f"502 Error - Bad Gateway. The {api_name} service might be down")
#             return None
        
#         response.raise_for_status()
        
#         # Try to parse JSON response
#         try:
#             return response.json()
#         except json.JSONDecodeError:
#             # If not JSON, return text response
#             return {"response": response.text}
    
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error calling {api_name} API: {str(e)}")
#         st.write("Full response text:", getattr(e.response, 'text', 'No response text')[:500] if hasattr(e, 'response') else 'No response')
#         return None
#     except Exception as e:
#         st.error(f"Unexpected error with {api_name} API: {str(e)}")
#         return None

# def main():
#     st.set_page_config(
#         page_title="Medical Analysis App",
#         page_icon="🔬",
#         layout="wide"
#     )
    
#     st.title("🔬 Medical Analysis Report Generator")
#     st.markdown("Upload a PDF and get comprehensive analysis from multiple AI services")
    
#     # Check if FPDF2 is available
#     if not FPDF_AVAILABLE:
#         st.error("""
#         **FPDF2 is required for PDF generation but is not installed.**
        
#         Please install it using:
#         ```
#         pip install fpdf2
#         ```
        
#         This is much simpler than WeasyPrint and has no system dependencies!
#         """)
#         return
    
#     # Initialize session state for results
#     if 'analysis_results' not in st.session_state:
#         st.session_state.analysis_results = None
    
#     # Initialize session state for physician remarks
#     if 'physician_remarks' not in st.session_state:
#         st.session_state.physician_remarks = ""
    
#     # Debug section
#     with st.sidebar:
#         st.subheader("🔧 Debug Tools")
        
#         if st.button("Test All APIs"):
#             st.subheader("API Testing Results")
#             for api_name, config in API_CONFIGS.items():
#                 st.write(f"### {api_name}")
#                 results = test_api_endpoint(api_name, config)
#                 df = pd.DataFrame(results)
#                 st.dataframe(df)
#                 st.write("---")
        
#         st.subheader("📝 API Configuration")
        
#         # Allow users to modify endpoints
#         for api_name, config in API_CONFIGS.items():
#             st.write(f"**{api_name}:**")
#             new_endpoint = st.text_input(
#                 f"Endpoint for {api_name}", 
#                 value=config.get('endpoint', ''),
#                 key=f"endpoint_{api_name}",
#                 placeholder="e.g., /api/parse, /upload, /analyze"
#             )
#             API_CONFIGS[api_name]['endpoint'] = new_endpoint
            
#             new_method = st.selectbox(
#                 f"Method for {api_name}",
#                 ['POST', 'GET'],
#                 index=0 if config.get('method', 'POST') == 'POST' else 1,
#                 key=f"method_{api_name}"
#             )
#             API_CONFIGS[api_name]['method'] = new_method
        
#         st.subheader("🧪 Test File Upload Parameters")
#         if st.button("Test File Parameters"):
#             st.write("Testing what file parameter names your APIs expect...")
            
#             # Create a small test file
#             test_content = b"Test PDF content"
#             test_files = {'file': ('test.pdf', test_content, 'application/pdf')}
            
#             for api_name, config in API_CONFIGS.items():
#                 if config['endpoint']:  # Only test if endpoint is configured
#                     st.write(f"Testing {api_name}...")
#                     base_url = config['base_url']
#                     endpoint = config['endpoint']
#                     full_url = f"{base_url}{endpoint}"
                    
#                     # Test different parameter names
#                     param_names = ['file', 'pdf', 'document', 'upload', 'data']
#                     for param_name in param_names:
#                         try:
#                             test_file = {param_name: ('test.pdf', test_content, 'application/pdf')}
#                             response = requests.post(full_url, files=test_file, timeout=10)
#                             st.write(f"  - {param_name}: Status {response.status_code}")
#                             if response.status_code not in [415, 400]:  # If not media type error
#                                 st.success(f"  ✅ {param_name} might be the correct parameter!")
#                                 break
#                         except Exception as e:
#                             st.write(f"  - {param_name}: Error - {str(e)[:100]}")
#                     st.write("---")
    
#     # File uploader
#     uploaded_file = st.file_uploader(
#         "Choose a PDF file",
#         type="pdf",
#         help="Upload a medical report PDF for analysis"
#     )
    
#     if uploaded_file is not None:
#         st.success(f"File uploaded: {uploaded_file.name}")
        
#         # Display file details
#         file_details = {
#             "Filename": uploaded_file.name,
#             "File size": f"{uploaded_file.size} bytes",
#             "File type": uploaded_file.type
#         }
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("File Details")
#             for key, value in file_details.items():
#                 st.write(f"**{key}:** {value}")
        
#         # Process button
#         if st.button("🚀 Process File", type="primary"):
#             all_results = {}
            
#             # Progress tracking
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             # Prepare file for PDF parsing API only
#             file_bytes = uploaded_file.read()
#             uploaded_file.seek(0)  # Reset file pointer
            
#             # 1. PDF Parsing API (takes PDF file)
#             status_text.text("Processing PDF parsing...")
#             progress_bar.progress(25)
            
#             files = {'file': (uploaded_file.name, file_bytes, 'application/pdf')}
#             pdf_result = call_api('PDF Parsing', API_CONFIGS['pdf_parsing'], files=files)
            
#             if pdf_result:
#                 all_results['pdf_parsing'] = pdf_result
#                 st.success("✅ PDF parsing completed")
                
#                 # Show parsed data
#                 st.subheader("📄 Parsed PDF Data")
#                 st.json(pdf_result)
                
#                 # 2. Score & Recommendations API (takes JSON from PDF parsing)
#                 status_text.text("Getting scores and recommendations...")
#                 progress_bar.progress(50)
                
#                 score_result = call_api('Score & Recommendations', API_CONFIGS['score_recommendations'], data=pdf_result)
                
#                 if score_result:
#                     all_results['score_recommendations'] = score_result
#                     st.success("✅ Score & recommendations completed")
#                 else:
#                     st.warning("⚠️ Score & recommendations failed")
                
#                 # 3. IUI-IVF API (takes formatted data from Score & Recommendations)
#                 status_text.text("Processing IUI-IVF analysis...")
#                 progress_bar.progress(75)
                
#                 if score_result:
#                     # Format data for IUI-IVF using recommend API output
#                     iui_input = format_data_for_iui_ivf(score_result)
#                     st.write("**Debug: Formatted data for IUI-IVF:**")
#                     st.json(iui_input)
                    
#                     iui_result = call_api('IUI-IVF', API_CONFIGS['iui_ivf'], data=iui_input)
                    
#                     if iui_result:
#                         all_results['iui_ivf'] = iui_result
#                         st.success("✅ IUI-IVF analysis completed")
#                     else:
#                         st.warning("⚠️ IUI-IVF analysis failed")
#                 else:
#                     st.warning("⚠️ IUI-IVF skipped - Score & Recommendations needed first")
                
#                 # 4. Morphology API (takes JSON from PDF parsing)
#                 status_text.text("Processing morphology analysis...")
#                 progress_bar.progress(90)
                
#                 # Format data specifically for Morphology API
#                 morph_input = format_data_for_morphology(pdf_result)
#                 st.write("**Debug: Formatted data for Morphology API:**")
#                 st.json(morph_input)
                
#                 morph_result = call_api('Morphology', API_CONFIGS['morphology'], data=morph_input)
                
#                 if morph_result:
#                     all_results['morphology'] = morph_result
#                     st.success("✅ Morphology analysis completed")
#                 else:
#                     st.warning("⚠️ Morphology analysis failed")
                    
#                 # Store results in session state
#                 st.session_state.analysis_results = all_results
                
#             else:
#                 st.error("❌ PDF parsing failed - cannot proceed with other analyses")
#                 st.stop()
            
#             # Complete processing
#             progress_bar.progress(100)
#             status_text.text("Processing complete!")
        
#         # Display results if they exist (either from current run or previous run)
#         if st.session_state.analysis_results:
#             all_results = st.session_state.analysis_results
            
#             st.subheader("📊 Analysis Results")
            
#             # Create tabs for each result
#             tabs = st.tabs(list(all_results.keys()))
            
#             for i, (key, result) in enumerate(all_results.items()):
#                 with tabs[i]:
#                     st.json(result)
            
#             # Generate PDF Report
#             st.subheader("📄 Generate Report")
            
#             try:
#                 pdf_generator = CleanPDFReportGenerator()
#                 pdf_bytes = pdf_generator.generate_report(all_results)
                
#                 if pdf_bytes:
#                     # Create download button
#                     st.download_button(
#                         label="📥 Download Clean PDF Report",
#                         data=pdf_bytes,
#                         file_name=f"fertility_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
#                         mime="application/pdf",
#                         key="download_pdf"
#                     )
                    
#                     st.success("✅ PDF report generated successfully!")
#                     st.info("""
#                     **PDF Features:**
#                     - Clean, professional medical report layout
#                     - Properly formatted text (asterisks converted to bullet points)
#                     - Color-coded status indicators (Normal/Low/High)
#                     - Highlighted fertility scores and interpretations
#                     - Empty physician remarks box for handwritten notes
#                     - Easy to read tables and sections
#                     """)
                
#             except Exception as e:
#                 st.error(f"Error generating PDF: {str(e)}")
#                 st.text(traceback.format_exc())

# if __name__ == "__main__":
#     main()





import streamlit as st
import requests
import json
import pandas as pd
import io
import base64
from datetime import datetime
import traceback
import re

# Using fpdf2 for better PDF generation (easier installation)
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    st.error("FPDF2 not available. Please install with: pip install fpdf2")

# API URLs with correct endpoints
API_CONFIGS = {
    'pdf_parsing': {
        'base_url': 'https://web-production-7060.up.railway.app',
        'endpoint': '/pdf-parse',
        'method': 'POST'
    },
    'score_recommendations': {
        'base_url': 'https://web-production-1abf.up.railway.app',
        'endpoint': '/recommend',
        'method': 'POST'
    },
    'iui_ivf': {
        'base_url': 'https://web-production-91c09.up.railway.app',
        'endpoint': '/iui-ivf-explain',
        'method': 'POST'
    },
    'morphology': {
        'base_url': 'https://web-production-d106c.up.railway.app',
        'endpoint': '/recommend-morphology',
        'method': 'POST'
    }
}

class CleanPDFReportGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Colors
        self.blue = (44, 90, 160)
        self.red = (220, 53, 69)
        self.green = (40, 167, 69)
        self.gray = (108, 117, 125)
        self.light_gray = (248, 249, 250)
        
    def clean_text(self, text):
        """Clean and format text, handling asterisks and special characters"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove problematic characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Handle asterisks - convert to bullet points or emphasis
        text = re.sub(r'\*\*\*+', '• ', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove double asterisks but keep content
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove single asterisks but keep content
        
        # Add line breaks after numbered items (1., 2., 3., etc.)
        text = re.sub(r'(\d+\.\s)', r'\n\1', text)
        
        # Clean up multiple spaces but preserve line breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
        text = re.sub(r'\n\s+', '\n', text)  # Remove spaces at beginning of new lines
        text = text.strip()
        
        return text
    
    def add_header(self):
        """Add report header"""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.set_text_color(*self.blue)
        self.pdf.cell(0, 15, 'FERTILITY ANALYSIS REPORT', 0, 1, 'C')
        
        # Line under title
        self.pdf.set_draw_color(*self.blue)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(10)
        
        # Timestamp
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.gray)
        timestamp = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        self.pdf.cell(0, 5, timestamp, 0, 1, 'C')
        self.pdf.ln(15)
    
    def add_section_header(self, title):
        """Add a section header with colored background"""
        self.pdf.ln(10)
        
        # Background rectangle
        self.pdf.set_fill_color(*self.light_gray)
        self.pdf.rect(10, self.pdf.get_y(), 190, 12, 'F')
        
        # Left border
        self.pdf.set_fill_color(*self.red)
        self.pdf.rect(10, self.pdf.get_y(), 3, 12, 'F')
        
        # Text
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.set_text_color(*self.red)
        self.pdf.cell(0, 12, f"  {title}", 0, 1, 'L')
        self.pdf.ln(5)
    
    def add_subsection_header(self, title):
        """Add a subsection header"""
        self.pdf.ln(5)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_text_color(*self.blue)
        self.pdf.cell(0, 8, title, 0, 1, 'L')
        
        # Underline
        self.pdf.set_draw_color(*self.blue)
        self.pdf.line(10, self.pdf.get_y(), 100, self.pdf.get_y())
        self.pdf.ln(5)
    
    def add_info_table(self, data_dict, title=None):
        """Add a two-column information table"""
        if title:
            self.add_subsection_header(title)
        
        self.pdf.set_font('Arial', '', 10)
        
        for key, value in data_dict.items():
            # Clean the data
            clean_key = self.clean_text(key.replace('_', ' ').title())
            clean_value = self.clean_text(str(value))
            
            # Key column (bold)
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.cell(60, 8, clean_key + ":", 1, 0, 'L')
            
            # Value column
            self.pdf.set_font('Arial', '', 10)
            self.pdf.cell(120, 8, clean_value, 1, 1, 'L')
        
        self.pdf.ln(5)
    
    def add_analysis_table(self, headers, data):
        """Add analysis table with headers"""
        # Table headers
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_fill_color(*self.blue)
        self.pdf.set_text_color(255, 255, 255)
        
        col_widths = [50, 30, 40, 30] if len(headers) == 4 else [40, 30, 30, 30, 30]
        
        for i, header in enumerate(headers):
            self.pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
        self.pdf.ln()
        
        # Table data
        self.pdf.set_font('Arial', '', 9)
        self.pdf.set_text_color(0, 0, 0)
        
        for row in data:
            for i, cell in enumerate(row):
                clean_cell = self.clean_text(str(cell))
                
                # Color code status
                if i == len(row) - 1 and clean_cell in ['Low', 'High']:
                    self.pdf.set_text_color(*self.red)
                elif i == len(row) - 1 and clean_cell == 'Normal':
                    self.pdf.set_text_color(*self.green)
                else:
                    self.pdf.set_text_color(0, 0, 0)
                
                self.pdf.cell(col_widths[i], 8, clean_cell, 1, 0, 'C')
            self.pdf.ln()
        
        self.pdf.ln(5)
    
    def add_fertility_score_box(self, score):
        """Add highlighted fertility score box"""
        self.pdf.ln(5)
        
        # Score box
        self.pdf.set_fill_color(255, 243, 205)  # Light yellow
        self.pdf.set_draw_color(*self.red)
        self.pdf.rect(10, self.pdf.get_y(), 190, 20, 'DF')
        
        # Score text
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.set_text_color(*self.red)
        self.pdf.cell(0, 20, f"Predicted Fertility Score: {score}%", 0, 1, 'C')
        self.pdf.ln(5)
    
    def add_interpretation_box(self):
        """Add fertility score interpretation"""
        self.pdf.set_fill_color(231, 243, 255)  # Light blue
        self.pdf.set_draw_color(*self.blue)
        self.pdf.rect(10, self.pdf.get_y(), 190, 25, 'DF')
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(*self.blue)
        self.pdf.cell(0, 8, "About the Fertility Score:", 0, 1, 'L')
        
        self.pdf.set_font('Arial', '', 9)
        self.pdf.set_text_color(0, 0, 0)
        text = "The fertility score percentage represents the estimated probability of achieving"
        self.pdf.cell(0, 6, text, 0, 1, 'L')
        text2 = "a natural pregnancy within 12 months, based on semen parameter analysis."
        self.pdf.cell(0, 6, text2, 0, 1, 'L')
        self.pdf.ln(10)
    
    def add_text_content(self, text, max_width=180):
        """Add formatted text content with proper line breaks"""
        if not text:
            return
            
        clean_text = self.clean_text(text)
        
        # Split into paragraphs
        paragraphs = clean_text.split('\n')
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(0, 0, 0)
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Handle bullet points
            if paragraph.strip().startswith('•'):
                self.pdf.cell(5, 6, '•', 0, 0, 'L')
                paragraph = paragraph.strip()[1:].strip()
            
            # Word wrap
            words = paragraph.split()
            line = ""
            
            for word in words:
                test_line = f"{line} {word}".strip()
                if self.pdf.get_string_width(test_line) <= max_width:
                    line = test_line
                else:
                    if line:
                        self.pdf.cell(0, 6, line, 0, 1, 'L')
                    line = word
            
            if line:
                self.pdf.cell(0, 6, line, 0, 1, 'L')
            
            self.pdf.ln(2)
    
    def add_recommendation_box(self, title, content):
        """Add recommendation box with border"""
        self.pdf.ln(5)
        
        # Box background
        self.pdf.set_fill_color(*self.light_gray)
        self.pdf.set_draw_color(*self.red)
        
        # Calculate box height based on content
        y_start = self.pdf.get_y()
        
        # Title
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_text_color(*self.red)
        self.pdf.cell(0, 10, title, 0, 1, 'L')
        
        # Content
        self.pdf.set_x(15)
        self.add_text_content(content, 175)
        
        y_end = self.pdf.get_y()
        
        # Draw box around content
        self.pdf.rect(10, y_start, 190, y_end - y_start + 5, 'D')
        self.pdf.ln(10)
    
    def add_physician_remarks_box(self):
        """Add empty boxes for physician remarks - Internal and External"""
        self.add_section_header("PHYSICIAN REMARKS")
        
        # Internal Remarks
        self.add_subsection_header("Internal Remarks")
        
        # Internal remarks box
        box_height = 60
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.rect(10, self.pdf.get_y(), 190, box_height, 'D')
        
        # Add lines for writing in internal box
        y_start = self.pdf.get_y() + 8
        for i in range(6):
            y_pos = y_start + (i * 8)
            if y_pos < self.pdf.get_y() + box_height - 8:
                self.pdf.line(15, y_pos, 195, y_pos)
        
        self.pdf.ln(box_height + 10)
        
        # External Remarks
        self.add_subsection_header("External Remarks")
        
        # External remarks box
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.rect(10, self.pdf.get_y(), 190, box_height, 'D')
        
        # Add lines for writing in external box
        y_start = self.pdf.get_y() + 8
        for i in range(6):
            y_pos = y_start + (i * 8)
            if y_pos < self.pdf.get_y() + box_height - 8:
                self.pdf.line(15, y_pos, 195, y_pos)
        
        self.pdf.ln(box_height + 10)
    
    def determine_status(self, param, value, normal_range):
        """Determine if parameter is normal, low, or high"""
        try:
            if value == 'N/A' or normal_range == 'N/A':
                return 'N/A'
            
            val = float(str(value).replace('%', ''))
            
            if 'motility' in param.lower() and val < 42:
                return 'Low'
            elif 'concentration' in param.lower() and val < 16:
                return 'Low'
            elif 'volume' in param.lower() and val < 1.4:
                return 'Low'
            elif 'morphology' in param.lower() and val < 4:
                return 'Low'
            else:
                return 'Normal'
        except:
            return 'N/A'
    
    def generate_report(self, all_results, filename="analysis_report.pdf"):
        """Generate the complete PDF report"""
        
        # Header
        self.add_header()
        
        # Patient Information Section
        if 'pdf_parsing' in all_results:
            pdf_data = all_results['pdf_parsing']
            
            self.add_section_header("PATIENT INFORMATION")
            
            if 'patient_info' in pdf_data:
                self.add_info_table(pdf_data['patient_info'])
            
            if 'collection_info' in pdf_data:
                self.add_info_table(pdf_data['collection_info'], "Collection Details")
            
            # Semen Analysis Results
            if 'semen_analysis' in pdf_data:
                self.pdf.add_page()
                self.add_section_header("SEMEN ANALYSIS RESULTS")
                
                # Prepare table data
                headers = ['Parameter', 'Value', 'Normal Range', 'Status']
                table_data = []
                
                for key, value in pdf_data['semen_analysis'].items():
                    if key == 'comments':
                        continue
                    
                    param_name = key.replace('_', ' ').title()
                    
                    if isinstance(value, dict):
                        param_value = str(value.get('value', 'N/A'))
                        normal_range = str(value.get('normal_range', 'N/A'))
                        status = self.determine_status(key, param_value, normal_range)
                        table_data.append([param_name, param_value, normal_range, status])
                    else:
                        table_data.append([param_name, str(value), 'N/A', 'N/A'])
                
                self.add_analysis_table(headers, table_data)
        
        # Fertility Score & Recommendations
        if 'score_recommendations' in all_results:
            self.pdf.add_page()
            self.add_section_header("FERTILITY ASSESSMENT")
            
            score_data = all_results['score_recommendations']
            
            # Fertility Score
            if 'fertility_score' in score_data:
                fertility_score = score_data['fertility_score']
                self.add_fertility_score_box(fertility_score)
                self.add_interpretation_box()
            
            # Features Analysis
            if 'features' in score_data:
                self.add_subsection_header("Parameter Impact Analysis")
                
                headers = ['Parameter', 'Value', 'Impact', 'Direction', 'Strength']
                table_data = []
                
                for param, details in score_data['features'].items():
                    if isinstance(details, dict):
                        value = str(details.get('value', 'N/A'))
                        impact = str(details.get('impact', 'N/A'))[:6]
                        direction = str(details.get('direction', 'N/A')).title()
                        strength = str(details.get('impact_strength', 'N/A'))
                        table_data.append([param, value, impact, direction, strength])
                
                self.add_analysis_table(headers, table_data)
            
            # Recommendations
            if 'recommendation' in score_data:
                self.add_recommendation_box("CLINICAL RECOMMENDATIONS", score_data['recommendation'])
        
        # IUI-IVF Analysis
        if 'iui_ivf' in all_results:
            self.pdf.add_page()
            self.add_section_header("TREATMENT OPTIONS ANALYSIS")
            
            iui_data = all_results['iui_ivf']
            if 'explanation' in iui_data:
                self.add_text_content(iui_data['explanation'])
        
        # Morphology Analysis
        if 'morphology' in all_results:
            self.add_section_header("MORPHOLOGY ASSESSMENT")
            
            morph_data = all_results['morphology']
            if 'recommendation' in morph_data:
                self.add_text_content(morph_data['recommendation'])
        
        # Physician Remarks
        self.add_physician_remarks_box()
        
        # Return PDF as bytes
        return bytes(self.pdf.output())

# Keep all the existing helper functions unchanged
def test_api_endpoint(api_name, config):
    """Test API endpoint with different methods"""
    base_url = config['base_url']
    endpoint = config.get('endpoint', '')
    full_url = f"{base_url}{endpoint}"
    
    st.write(f"Testing {api_name} at: {full_url}")
    
    # Test different endpoints and methods
    test_endpoints = ['', '/health', '/status', '/ping', '/docs', '/']
    test_methods = ['GET', 'POST']
    
    results = []
    
    for endpoint in test_endpoints:
        test_url = f"{base_url}{endpoint}"
        for method in test_methods:
            try:
                if method == 'GET':
                    response = requests.get(test_url, timeout=10)
                else:
                    response = requests.post(test_url, timeout=10)
                
                results.append({
                    'URL': test_url,
                    'Method': method,
                    'Status': response.status_code,
                    'Response': response.text[:200] + '...' if len(response.text) > 200 else response.text
                })
                
            except Exception as e:
                results.append({
                    'URL': test_url,
                    'Method': method,
                    'Status': 'Error',
                    'Response': str(e)
                })
    
    return results

def format_data_for_morphology(pdf_result):
    """Format PDF parsing result for Morphology API"""
    try:
        # Look for morphology value in the PDF parsing result
        morphology_value = None
        
        def find_morphology_value(data):
            """Recursively search for morphology-related values"""
            if isinstance(data, dict):
                for key, value in data.items():
                    # Look for morphology-related keys
                    if any(term in key.lower() for term in ['morphology', 'morph', 'normal_forms', 'normal forms']):
                        if isinstance(value, (int, float)):
                            return float(value)
                        elif isinstance(value, str):
                            try:
                                return float(value)
                            except:
                                pass
                        elif isinstance(value, dict) and 'value' in value:
                            try:
                                return float(value['value'])
                            except:
                                pass
                    
                    # Recursively search in nested objects
                    if isinstance(value, dict):
                        result = find_morphology_value(value)
                        if result is not None:
                            return result
            
            elif isinstance(data, list):
                for item in data:
                    result = find_morphology_value(item)
                    if result is not None:
                        return result
            
            return None
        
        morphology_value = find_morphology_value(pdf_result)
        
        # If no morphology value found, use a default
        if morphology_value is None:
            morphology_value = 4.0  # Default normal morphology percentage
        
        # Format data as expected by the API
        morphology_input = {
            "semen_analysis": {
                "morphology": {
                    "value": morphology_value
                }
            }
        }
        
        return morphology_input
        
    except Exception as e:
        # Fallback with default value
        return {
            "semen_analysis": {
                "morphology": {
                    "value": 4.0
                }
            }
        }

def format_data_for_iui_ivf(recommend_result):
    """Format recommend API output for IUI-IVF API"""
    try:
        # Extract fertility_score from recommend result
        fertility_score = None
        
        # Look for fertility_score in various possible locations
        if isinstance(recommend_result, dict):
            # Direct fertility_score
            if 'fertility_score' in recommend_result:
                fertility_score = recommend_result['fertility_score']
            # In scores object
            elif 'scores' in recommend_result and isinstance(recommend_result['scores'], dict):
                fertility_score = recommend_result['scores'].get('fertility_score')
            # Look for any field with 'fertility' and 'score'
            else:
                for key, value in recommend_result.items():
                    if 'fertility' in key.lower() and 'score' in key.lower():
                        fertility_score = value
                        break
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if 'fertility' in sub_key.lower() and 'score' in sub_key.lower():
                                fertility_score = sub_value
                                break
        
        # Default fertility score if not found
        if fertility_score is None:
            fertility_score = 50.0  # Default value
        
        # Extract features (Volume, Concentration, Motility)
        features = {}
        
        # Function to search for feature data
        def find_feature_data(data, feature_names):
            """Find value and impact for a feature"""
            result = {"value": 0.0, "impact": 0.0}
            
            if isinstance(data, dict):
                for key, value in data.items():
                    # Check if key matches any feature name
                    for feature_name in feature_names:
                        if feature_name.lower() in key.lower():
                            if isinstance(value, dict):
                                # If value is a dict, look for 'value' and 'impact'
                                if 'value' in value:
                                    result['value'] = float(value['value'])
                                if 'impact' in value:
                                    result['impact'] = float(value['impact'])
                            elif isinstance(value, (int, float)):
                                # If value is a number, use it as value
                                result['value'] = float(value)
                            break
                    
                    # Recursively search in nested objects
                    if isinstance(value, dict):
                        nested_result = find_feature_data(value, feature_names)
                        if nested_result['value'] != 0.0 or nested_result['impact'] != 0.0:
                            result = nested_result
                            break
            
            return result
        
        # Search for Volume data
        volume_names = ['volume', 'vol']
        features['Volume'] = find_feature_data(recommend_result, volume_names)
        
        # Search for Concentration data
        concentration_names = ['concentration', 'conc', 'density']
        features['Concentration'] = find_feature_data(recommend_result, concentration_names)
        
        # Search for Motility data
        motility_names = ['motility', 'mobility', 'movement']
        features['Motility'] = find_feature_data(recommend_result, motility_names)
        
        # If no features found, use defaults based on fertility score
        if all(f['value'] == 0.0 and f['impact'] == 0.0 for f in features.values()):
            # Generate reasonable defaults based on fertility score
            base_impact = (fertility_score - 50) / 100  # Normalize around 50
            
            features = {
                'Volume': {
                    'value': max(1.0, fertility_score / 20),  # 1-5 range
                    'impact': base_impact * 0.1
                },
                'Concentration': {
                    'value': max(5.0, fertility_score / 3),  # 5-33 range
                    'impact': base_impact * 0.6
                },
                'Motility': {
                    'value': max(10.0, fertility_score * 0.8),  # 10-80 range
                    'impact': base_impact * 0.8
                }
            }
        
        # Format final result
        iui_input = {
            "fertility_score": float(fertility_score),
            "features": features
        }
        
        return iui_input
        
    except Exception as e:
        # Fallback with default values
        return {
            "fertility_score": 50.0,
            "features": {
                "Volume": {"value": 3.0, "impact": 0.1},
                "Concentration": {"value": 15.0, "impact": 0.3},
                "Motility": {"value": 40.0, "impact": 0.5}
            }
        }

def preprocess_data_for_api(data, api_name):
    """Preprocess data to ensure correct types for each API"""
    if not isinstance(data, dict):
        return data
    
    processed_data = data.copy()
    
    # Common preprocessing - convert numeric strings to numbers
    def convert_numeric_strings(obj):
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = convert_numeric_strings(value)
            return result
        elif isinstance(obj, list):
            return [convert_numeric_strings(item) for item in obj]
        elif isinstance(obj, str):
            # Try to convert string to number
            try:
                # First try integer
                if obj.isdigit() or (obj.startswith('-') and obj[1:].isdigit()):
                    return int(obj)
                # Try float (including decimal numbers)
                if '.' in obj or 'e' in obj.lower():
                    return float(obj)
                # Try float anyway for safety
                return float(obj)
            except (ValueError, AttributeError):
                return obj
        else:
            return obj
    
    processed_data = convert_numeric_strings(processed_data)
    return processed_data

def call_api(api_name, config, files=None, data=None, custom_endpoint=None):
    """Make API call with error handling and flexible configuration"""
    base_url = config['base_url']
    endpoint = custom_endpoint or config.get('endpoint', '')
    method = config.get('method', 'POST')
    full_url = f"{base_url}{endpoint}"
    
    try:
        st.write(f"Calling {api_name} API: {method} {full_url}")
        
        # Preprocess data if it's JSON
        if data and not files:
            data = preprocess_data_for_api(data, api_name)
            st.write(f"Preprocessed data sample: {str(data)[:200]}...")
        
        if method.upper() == 'GET':
            response = requests.get(full_url, timeout=30)
        else:  # POST
            if files:
                # Try different file parameter names and content types
                file_variations = [
                    {'file': files['file']},  # Standard 'file'
                    {'pdf': files['file']},   # Some APIs use 'pdf'
                    {'document': files['file']}, # Some use 'document'
                    {'upload': files['file']},   # Some use 'upload'
                ]
                
                # Try different approaches for 415 errors
                for i, file_data in enumerate(file_variations):
                    try:
                        if i > 0:  # Only show retry attempts
                            st.write(f"Retry {i}: Trying different file parameter...")
                        
                        response = requests.post(full_url, files=file_data, data=data, timeout=30)
                        
                        if response.status_code != 415:  # If not unsupported media type, break
                            break
                            
                    except Exception as retry_error:
                        continue
                        
                # If still 415, try with different content type headers
                if response.status_code == 415:
                    st.write("Trying with explicit content-type headers...")
                    headers = {'Content-Type': 'multipart/form-data'}
                    try:
                        response = requests.post(full_url, files=files, data=data, headers=headers, timeout=30)
                    except:
                        pass
            else:
                response = requests.post(full_url, json=data, timeout=30)
        
        st.write(f"Response status: {response.status_code}")
        
        if response.status_code == 404:
            st.warning(f"404 Error - Endpoint not found. Try testing different endpoints for {api_name}")
            return None
        elif response.status_code == 405:
            st.warning(f"405 Error - Method not allowed. Try different HTTP method for {api_name}")
            return None
        elif response.status_code == 415:
            st.warning(f"415 Error - Unsupported Media Type. The {api_name} API expects a different file format or parameter name")
            st.write("Response:", response.text[:500])
            return None
        elif response.status_code == 500:
            st.warning(f"500 Error - Internal Server Error. The {api_name} service has an internal issue")
            st.write("Response:", response.text[:500])
            return None
        elif response.status_code == 502:
            st.warning(f"502 Error - Bad Gateway. The {api_name} service might be down")
            return None
        
        response.raise_for_status()
        
        # Try to parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            # If not JSON, return text response
            return {"response": response.text}
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling {api_name} API: {str(e)}")
        st.write("Full response text:", getattr(e.response, 'text', 'No response text')[:500] if hasattr(e, 'response') else 'No response')
        return None
    except Exception as e:
        st.error(f"Unexpected error with {api_name} API: {str(e)}")
        return None

def display_editable_parameters(pdf_result):
    """Display extracted parameters in editable form and return updated data"""
    st.subheader("📝 Verify & Edit Extracted Parameters")
    st.markdown("Review the extracted values below and make corrections if needed:")
    
    # Create a copy of the original result to modify
    updated_result = pdf_result.copy()
    
    # Track if any changes were made
    changes_made = False
    
    # Handle patient information
    if 'patient_info' in pdf_result:
        st.markdown("**Patient Information:**")
        cols = st.columns(2)
        
        updated_patient_info = {}
        for i, (key, value) in enumerate(pdf_result['patient_info'].items()):
            with cols[i % 2]:
                new_value = st.text_input(
                    f"{key.replace('_', ' ').title()}:",
                    value=str(value) if value is not None else "",
                    key=f"patient_{key}"
                )
                updated_patient_info[key] = new_value
                if str(new_value) != str(value):
                    changes_made = True
        
        updated_result['patient_info'] = updated_patient_info
    
    # Handle collection information
    if 'collection_info' in pdf_result:
        st.markdown("**Collection Information:**")
        cols = st.columns(2)
        
        updated_collection_info = {}
        for i, (key, value) in enumerate(pdf_result['collection_info'].items()):
            with cols[i % 2]:
                new_value = st.text_input(
                    f"{key.replace('_', ' ').title()}:",
                    value=str(value) if value is not None else "",
                    key=f"collection_{key}"
                )
                updated_collection_info[key] = new_value
                if str(new_value) != str(value):
                    changes_made = True
        
        updated_result['collection_info'] = updated_collection_info
    
    # Handle semen analysis parameters - most important section
    if 'semen_analysis' in pdf_result:
        st.markdown("**Semen Analysis Parameters:**")
        
        updated_semen_analysis = {}
        
        # Create a more organized layout for semen parameters
        for param_key, param_value in pdf_result['semen_analysis'].items():
            if param_key == 'comments':
                # Handle comments separately
                new_comments = st.text_area(
                    "Comments:",
                    value=str(param_value) if param_value is not None else "",
                    key=f"semen_comments",
                    height=100
                )
                updated_semen_analysis[param_key] = new_comments
                if str(new_comments) != str(param_value):
                    changes_made = True
            else:
                # Handle regular parameters
                param_display_name = param_key.replace('_', ' ').title()
                
                # Create columns for value and normal range if it's a dict
                if isinstance(param_value, dict):
                    cols = st.columns([2, 1, 1])
                    
                    with cols[0]:
                        st.write(f"**{param_display_name}:**")
                    
                    with cols[1]:
                        original_value = param_value.get('value', '')
                        new_value = st.text_input(
                            "Value:",
                            value=str(original_value) if original_value is not None else "",
                            key=f"semen_{param_key}_value"
                        )
                        
                    with cols[2]:
                        original_range = param_value.get('normal_range', '')
                        new_range = st.text_input(
                            "Normal Range:",
                            value=str(original_range) if original_range is not None else "",
                            key=f"semen_{param_key}_range"
                        )
                    
                    updated_param = {
                        'value': new_value,
                        'normal_range': new_range
                    }
                    
                    # Check for changes
                    if (str(new_value) != str(original_value) or 
                        str(new_range) != str(original_range)):
                        changes_made = True
                    
                    updated_semen_analysis[param_key] = updated_param
                    
                else:
                    # Handle simple string/number values
                    new_value = st.text_input(
                        f"{param_display_name}:",
                        value=str(param_value) if param_value is not None else "",
                        key=f"semen_{param_key}"
                    )
                    updated_semen_analysis[param_key] = new_value
                    if str(new_value) != str(param_value):
                        changes_made = True
        
        updated_result['semen_analysis'] = updated_semen_analysis
    
    # Show change indicator
    if changes_made:
        st.info("✏️ Changes detected in the parameters above")
    
    return updated_result, changes_made

def main():
    st.set_page_config(
        page_title="Medical Analysis App",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Medical Analysis Report Generator")
    st.markdown("Upload a PDF and get comprehensive analysis from multiple AI services")
    
    # Check if FPDF2 is available
    if not FPDF_AVAILABLE:
        st.error("""
        **FPDF2 is required for PDF generation but is not installed.**
        
        Please install it using: This is much simpler than WeasyPrint and has no system dependencies!
        """)
        return
    
    # Initialize session state for results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Initialize session state for physician remarks
    if 'physician_remarks' not in st.session_state:
        st.session_state.physician_remarks = ""
    
    # Initialize session state for PDF parsing results
    if 'pdf_parsing_result' not in st.session_state:
        st.session_state.pdf_parsing_result = None
    
    # Initialize session state for processing step
    if 'processing_step' not in st.session_state:
        st.session_state.processing_step = 'upload'
    
    # Debug section
    with st.sidebar:
        st.subheader("🔧 Debug Tools")
        
        if st.button("Test All APIs"):
            st.subheader("API Testing Results")
            for api_name, config in API_CONFIGS.items():
                st.write(f"### {api_name}")
                results = test_api_endpoint(api_name, config)
                df = pd.DataFrame(results)
                st.dataframe(df)
                st.write("---")
        
        st.subheader("📝 API Configuration")
        
        # Allow users to modify endpoints
        for api_name, config in API_CONFIGS.items():
            st.write(f"**{api_name}:**")
            new_endpoint = st.text_input(
                f"Endpoint for {api_name}", 
                value=config.get('endpoint', ''),
                key=f"endpoint_{api_name}",
                placeholder="e.g., /api/parse, /upload, /analyze"
            )
            API_CONFIGS[api_name]['endpoint'] = new_endpoint
            
            new_method = st.selectbox(
                f"Method for {api_name}",
                ['POST', 'GET'],
                index=0 if config.get('method', 'POST') == 'POST' else 1,
                key=f"method_{api_name}"
            )
            API_CONFIGS[api_name]['method'] = new_method
        
        st.subheader("🧪 Test File Upload Parameters")
        if st.button("Test File Parameters"):
            st.write("Testing what file parameter names your APIs expect...")
            
            # Create a small test file
            test_content = b"Test PDF content"
            test_files = {'file': ('test.pdf', test_content, 'application/pdf')}
            
            for api_name, config in API_CONFIGS.items():
                if config['endpoint']:  # Only test if endpoint is configured
                    st.write(f"Testing {api_name}...")
                    base_url = config['base_url']
                    endpoint = config['endpoint']
                    full_url = f"{base_url}{endpoint}"
                    
                    # Test different parameter names
                    param_names = ['file', 'pdf', 'document', 'upload', 'data']
                    for param_name in param_names:
                        try:
                            test_file = {param_name: ('test.pdf', test_content, 'application/pdf')}
                            response = requests.post(full_url, files=test_file, timeout=10)
                            st.write(f"  - {param_name}: Status {response.status_code}")
                            if response.status_code not in [415, 400]:  # If not media type error
                                st.success(f"  ✅ {param_name} might be the correct parameter!")
                                break
                        except Exception as e:
                            st.write(f"  - {param_name}: Error - {str(e)[:100]}")
                    st.write("---")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a medical report PDF for analysis"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Display file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size} bytes",
            "File type": uploaded_file.type
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("File Details")
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        # Step 1: PDF Processing
        if st.session_state.processing_step == 'upload':
            if st.button("🚀 Parse PDF", type="primary"):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Prepare file for PDF parsing API only
                file_bytes = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                
                # 1. PDF Parsing API (takes PDF file)
                status_text.text("Processing PDF parsing...")
                progress_bar.progress(100)
                
                files = {'file': (uploaded_file.name, file_bytes, 'application/pdf')}
                pdf_result = call_api('PDF Parsing', API_CONFIGS['pdf_parsing'], files=files)
                
                if pdf_result:
                    st.session_state.pdf_parsing_result = pdf_result
                    st.session_state.processing_step = 'edit_parameters'
                    st.success("✅ PDF parsing completed")
                    st.rerun()
                else:
                    st.error("❌ PDF parsing failed - cannot proceed with analysis")
                    progress_bar.empty()
                    status_text.empty()
        
        # Step 2: Parameter Editing
        elif st.session_state.processing_step == 'edit_parameters':
            pdf_result = st.session_state.pdf_parsing_result
            
            # Show original parsed data in an expander
            with st.expander("🔍 View Original Parsed Data", expanded=False):
                st.json(pdf_result)
            
            # Display editable parameters
            updated_pdf_result, changes_made = display_editable_parameters(pdf_result)
            
            # Continue with analysis button
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🔄 Continue with Analysis Using Verified Data", type="primary"):
                    st.session_state.pdf_parsing_result = updated_pdf_result
                    st.session_state.processing_step = 'run_analysis'
                    st.rerun()
            
            with col2:
                if st.button("🔙 Upload New File"):
                    st.session_state.processing_step = 'upload'
                    st.session_state.pdf_parsing_result = None
                    st.session_state.analysis_results = None
                    st.rerun()
        
        # Step 3: Run Full Analysis
        elif st.session_state.processing_step == 'run_analysis':
            updated_pdf_result = st.session_state.pdf_parsing_result
            
            if st.button("▶️ Run Complete Analysis"):
                all_results = {}
                all_results['pdf_parsing'] = updated_pdf_result
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 2. Score & Recommendations API (takes JSON from PDF parsing)
                status_text.text("Getting scores and recommendations...")
                progress_bar.progress(25)
                
                # Use the updated/verified data instead of original
                score_result = call_api('Score & Recommendations', API_CONFIGS['score_recommendations'], data=updated_pdf_result)
                
                if score_result:
                    all_results['score_recommendations'] = score_result
                    st.success("✅ Score & recommendations completed")
                    
                    # Show the results
                    with st.expander("📊 View Score & Recommendations Results"):
                        st.json(score_result)
                        
                else:
                    st.warning("⚠️ Score & recommendations failed")
                
                # 3. IUI-IVF API (takes formatted data from Score & Recommendations)
                status_text.text("Processing IUI-IVF analysis...")
                progress_bar.progress(50)
                
                if score_result:
                    # Format data for IUI-IVF using recommend API output
                    iui_input = format_data_for_iui_ivf(score_result)
                    
                    with st.expander("🔍 Debug: Formatted data for IUI-IVF"):
                        st.json(iui_input)
                    
                    iui_result = call_api('IUI-IVF', API_CONFIGS['iui_ivf'], data=iui_input)
                    
                    if iui_result:
                        all_results['iui_ivf'] = iui_result
                        st.success("✅ IUI-IVF analysis completed")
                    else:
                        st.warning("⚠️ IUI-IVF analysis failed")
                else:
                    st.warning("⚠️ IUI-IVF skipped - Score & Recommendations needed first")
                
                # 4. Morphology API (takes JSON from PDF parsing)
                status_text.text("Processing morphology analysis...")
                progress_bar.progress(75)
                
                # Format data specifically for Morphology API using updated data
                morph_input = format_data_for_morphology(updated_pdf_result)
                
                with st.expander("🔍 Debug: Formatted data for Morphology API"):
                    st.json(morph_input)
                
                morph_result = call_api('Morphology', API_CONFIGS['morphology'], data=morph_input)
                
                if morph_result:
                    all_results['morphology'] = morph_result
                    st.success("✅ Morphology analysis completed")
                else:
                    st.warning("⚠️ Morphology analysis failed")
                    
                # Store final results in session state
                st.session_state.analysis_results = all_results
                st.session_state.processing_step = 'show_results'
                
                # Complete processing
                progress_bar.progress(100)
                status_text.text("Processing complete!")
                
                st.rerun()
            
            # Show parameter preview
            st.subheader("📋 Parameter Summary")
            with st.expander("Review final parameters that will be used"):
                st.json(updated_pdf_result)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔙 Edit Parameters Again"):
                    st.session_state.processing_step = 'edit_parameters'
                    st.rerun()
            
            with col2:
                if st.button("🏠 Start Over"):
                    st.session_state.processing_step = 'upload'
                    st.session_state.pdf_parsing_result = None
                    st.session_state.analysis_results = None
                    st.rerun()
        
        # Step 4: Show Results
        elif st.session_state.processing_step == 'show_results':
            if st.session_state.analysis_results:
                all_results = st.session_state.analysis_results
                
                st.subheader("📊 Analysis Results")
                
                # Create tabs for each result
                tabs = st.tabs(list(all_results.keys()))
                
                for i, (key, result) in enumerate(all_results.items()):
                    with tabs[i]:
                        st.json(result)
                
                # Generate PDF Report
                st.subheader("📄 Generate Report")
                
                try:
                    pdf_generator = CleanPDFReportGenerator()
                    pdf_bytes = pdf_generator.generate_report(all_results)
                    
                    if pdf_bytes:
                        # Create download button
                        st.download_button(
                            label="📥 Download Clean PDF Report",
                            data=pdf_bytes,
                            file_name=f"fertility_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key="download_pdf"
                        )
                        
                        st.success("✅ PDF report generated successfully!")
                        st.info("""
                        **PDF Features:**
                        - Clean, professional medical report layout
                        - Properly formatted text (asterisks converted to bullet points)
                        - Color-coded status indicators (Normal/Low/High)
                        - Highlighted fertility scores and interpretations
                        - Empty physician remarks box for handwritten notes
                        - Easy to read tables and sections
                        """)
                
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.text(traceback.format_exc())
                
                # Navigation buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔙 Edit Parameters"):
                        st.session_state.processing_step = 'edit_parameters'
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Re-run Analysis"):
                        st.session_state.processing_step = 'run_analysis'
                        st.rerun()
                
                with col3:
                    if st.button("🏠 Start Over"):
                        st.session_state.processing_step = 'upload'
                        st.session_state.pdf_parsing_result = None
                        st.session_state.analysis_results = None
                        st.rerun()

if __name__ == "__main__":
    main()
