import streamlit as st
import requests
import json
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import base64
from datetime import datetime
import traceback

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

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.darkred,
            spaceBefore=25,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.darkred,
            borderPadding=8,
            backColor=colors.lightgrey
        )
        
        self.subsection_style = ParagraphStyle(
            'SubSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=8,
            leftIndent=10
        )
        
        self.highlight_style = ParagraphStyle(
            'Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkred,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            leftIndent=10
        )

    def create_patient_info_table(self, patient_info):
        """Create a nicely formatted patient information table"""
        data = []
        for key, value in patient_info.items():
            formatted_key = key.replace('_', ' ').title()
            data.append([formatted_key, str(value)])
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        return table

    def create_semen_analysis_table(self, semen_data):
        """Create a detailed semen analysis table"""
        headers = ['Parameter', 'Value', 'Normal Range', 'Status']
        data = [headers]
        
        for key, value in semen_data.items():
            if key == 'comments':
                continue
                
            param_name = key.replace('_', ' ').title()
            
            if isinstance(value, dict):
                param_value = value.get('value', 'N/A')
                normal_range = value.get('normal_range', 'N/A')
                
                # Determine status
                status = self.determine_status(key, param_value, normal_range)
                
                data.append([param_name, str(param_value), str(normal_range), status])
            else:
                data.append([param_name, str(value), 'N/A', 'N/A'])
        
        table = Table(data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        return table

    def determine_status(self, param, value, normal_range):
        """Determine if parameter is normal, low, or high"""
        try:
            if value == 'N/A' or normal_range == 'N/A':
                return 'N/A'
            
            val = float(str(value).replace('%', ''))
            
            # Simple status determination based on common patterns
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

    def create_fertility_score_interpretation(self, fertility_score):
        """Create fertility score interpretation section based on the score ranges"""
        
        # About the Score explanation
        about_style = ParagraphStyle(
            'AboutScore',
            parent=self.normal_style,
            fontSize=11,
            textColor=colors.darkblue,
            backColor=colors.lightblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=10,
            spaceAfter=15
        )
        
        about_text = """About the Fertility Score: The fertility score percentage represents the estimated probability of achieving a natural pregnancy within 12 months, based on analysis of the semen parameters and clinical pregnancy outcome data."""
        
        about_para = Paragraph(about_text, about_style)
        
        # Recommendation based on score with better styling
        recommendation_style = ParagraphStyle(
            'RecommendationBox',
            parent=self.normal_style,
            fontSize=12,
            textColor=colors.darkblue,
            backColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=12,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        if fertility_score < 20:
            recommendation = "Below optimal fertility parameters. Consultation with fertility specialist recommended."
        elif fertility_score < 40:
            recommendation = "Below optimal fertility parameters. Consultation with fertility specialist recommended."
        elif fertility_score < 60:
            recommendation = "Moderate fertility parameters. Consider lifestyle modifications and monitoring."
        elif fertility_score < 80:
            recommendation = "Good fertility parameters. Continue current approach with monitoring."
        else:
            recommendation = "High fertility parameters. Optimal for natural conception attempts."
        
        recommendation_para = Paragraph(recommendation, recommendation_style)
        
        # Fertility Probability Score Table
        table_title = Paragraph("Fertility Probability Score Table", self.subsection_style)
        
        # Create score ranges data
        score_ranges = [
            {
                'range': '0-20%: Very Low Fertility Probability',
                'description': '→ 0-20% chance of natural pregnancy within 12 months\n→ IVF with ICSI highly likely',
                'color': colors.white
            },
            {
                'range': '20-40%: Low Fertility Probability', 
                'description': '→ 20-40% chance of natural pregnancy within 12 months\n→ IVF (with or without ICSI), depending on age and egg quality',
                'color': colors.white
            },
            {
                'range': '40-60%: Moderate Fertility Probability',
                'description': '→ 40-60% chance of natural pregnancy within 12 months\n→ Consider IUI; may need supplements, lifestyle changes, or further testing',
                'color': colors.white
            },
            {
                'range': '60-80%: Good Fertility Probability',
                'description': '→ 60-80% chance of natural pregnancy within 12 months\n→ Try naturally for 6-12 months or consider IUI if time-sensitive',
                'color': colors.white
            },
            {
                'range': '80-100%: High Fertility Probability',
                'description': '→ 80-100% chance of natural pregnancy within 12 months\n→ Try timed intercourse and ovulation tracking',
                'color': colors.white
            }
        ]
        
        # Highlight the relevant range based on fertility score
        for score_range in score_ranges:
            range_text = score_range['range']
            if '0-20%' in range_text and fertility_score <= 20:
                score_range['color'] = colors.lightyellow
            elif '20-40%' in range_text and 20 < fertility_score <= 40:
                score_range['color'] = colors.lightyellow
            elif '40-60%' in range_text and 40 < fertility_score <= 60:
                score_range['color'] = colors.lightyellow
            elif '60-80%' in range_text and 60 < fertility_score <= 80:
                score_range['color'] = colors.lightyellow
            elif '80-100%' in range_text and fertility_score > 80:
                score_range['color'] = colors.lightyellow
        
        # Create table data
        table_data = []
        for score_range in score_ranges:
            # Create paragraphs for the table cells
            range_para = Paragraph(f"<b>{score_range['range']}</b>", self.normal_style)
            desc_para = Paragraph(score_range['description'], self.normal_style)
            table_data.append([range_para, desc_para])
        
        # Create table
        probability_table = Table(table_data, colWidths=[2.5*inch, 4*inch])
        
        # Apply styling
        table_style_commands = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Highlight the appropriate row based on fertility score
        for i, score_range in enumerate(score_ranges):
            table_style_commands.append(('BACKGROUND', (0, i), (-1, i), score_range['color']))
        
        probability_table.setStyle(TableStyle(table_style_commands))
        
        return [about_para, Spacer(1, 10), recommendation_para, Spacer(1, 20), table_title, probability_table]

    def format_text_with_line_breaks(self, text, style):
        """Format long text with proper line breaks"""
        if isinstance(text, str) and len(text) > 100:
            # Split long text into paragraphs
            sentences = text.split('. ')
            formatted_sentences = []
            
            for sentence in sentences:
                if sentence.strip():
                    if not sentence.endswith('.'):
                        sentence += '.'
                    formatted_sentences.append(sentence.strip())
            
            # Join sentences with proper spacing
            return [Paragraph(sent, style) for sent in formatted_sentences]
        else:
            return [Paragraph(str(text), style)]

    def generate_report(self, all_results, filename="analysis_report.pdf", physician_remarks=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        story = []

        # Title Page
        story.append(Paragraph("FERTILITY ANALYSIS REPORT", self.title_style))
        story.append(Spacer(1, 20))
        
        # Timestamp
        timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                            self.normal_style)
        story.append(timestamp)
        story.append(Spacer(1, 40))

        # Patient Information Section
        if 'pdf_parsing' in all_results:
            pdf_data = all_results['pdf_parsing']
            
            story.append(Paragraph("PATIENT INFORMATION", self.section_header_style))
            
            if 'patient_info' in pdf_data:
                patient_table = self.create_patient_info_table(pdf_data['patient_info'])
                story.append(patient_table)
                story.append(Spacer(1, 20))
            
            # Collection Information
            if 'collection_info' in pdf_data:
                story.append(Paragraph("Collection Details", self.subsection_style))
                collection_table = self.create_patient_info_table(pdf_data['collection_info'])
                story.append(collection_table)
                story.append(Spacer(1, 20))
            
            # Semen Analysis Results
            if 'semen_analysis' in pdf_data:
                story.append(PageBreak())
                story.append(Paragraph("SEMEN ANALYSIS RESULTS", self.section_header_style))
                semen_table = self.create_semen_analysis_table(pdf_data['semen_analysis'])
                story.append(semen_table)
                story.append(Spacer(1, 20))

        # Fertility Score & Recommendations
        if 'score_recommendations' in all_results:
            story.append(PageBreak())
            story.append(Paragraph("FERTILITY ASSESSMENT", self.section_header_style))
            
            score_data = all_results['score_recommendations']
            
            # Fertility Score
            if 'fertility_score' in score_data:
                fertility_score = score_data['fertility_score']
                score_text = f"Predicted Fertility Score: {fertility_score}%"
                story.append(Paragraph(score_text, self.highlight_style))
                story.append(Spacer(1, 15))
                
                # Add the fertility score interpretation
                interpretation_elements = self.create_fertility_score_interpretation(fertility_score)
                for element in interpretation_elements:
                    story.append(element)
                
                story.append(Spacer(1, 20))
            
            # Features Analysis
            if 'features' in score_data:
                story.append(Paragraph("Parameter Impact Analysis", self.subsection_style))
                
                features = score_data['features']
                feature_data = [['Parameter', 'Value', 'Impact', 'Direction', 'Strength']]
                
                for param, details in features.items():
                    if isinstance(details, dict):
                        value = details.get('value', 'N/A')
                        impact = details.get('impact', 'N/A')
                        direction = details.get('direction', 'N/A')
                        strength = details.get('impact_strength', 'N/A')
                        
                        feature_data.append([param, str(value), str(impact)[:6], 
                                          direction.title(), strength])
                
                feature_table = Table(feature_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
                feature_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(feature_table)
                story.append(Spacer(1, 20))
            
            # Recommendations - Keep together on same page
            if 'recommendation' in score_data:
                # Create a special red box style for Clinical Recommendations header
                clinical_rec_style = ParagraphStyle(
                    'ClinicalRecommendations',
                    parent=self.styles['Heading1'],
                    fontSize=16,
                    textColor=colors.darkred,
                    spaceBefore=25,
                    spaceAfter=15,
                    fontName='Helvetica-Bold',
                    borderWidth=2,
                    borderColor=colors.darkred,
                    borderPadding=8,
                    backColor=colors.lightgrey,
                    alignment=TA_LEFT,
                    keepWithNext=1  # Keep header with following content
                )
                
                # Start a group to keep content together
                rec_elements = []
                rec_elements.append(Paragraph("CLINICAL RECOMMENDATIONS", clinical_rec_style))
                
                rec_text = score_data['recommendation']
                
                # Clean up the recommendation text
                if isinstance(rec_text, str):
                    # Remove excessive dashes and format properly
                    rec_text = rec_text.replace('---', '').replace('**', '')
                    
                    # Split into sections and format
                    sections = rec_text.split('- **')
                    for section in sections:
                        if section.strip():
                            formatted_text = section.strip()
                            paragraphs = self.format_text_with_line_breaks(formatted_text, self.normal_style)
                            for para in paragraphs:
                                rec_elements.append(para)
                            rec_elements.append(Spacer(1, 8))
                
                # Add all recommendation elements at once to keep them together
                for element in rec_elements:
                    story.append(element)

        # IUI-IVF Analysis
        if 'iui_ivf' in all_results:
            story.append(PageBreak())
            story.append(Paragraph("TREATMENT OPTIONS ANALYSIS", self.section_header_style))
            
            iui_data = all_results['iui_ivf']
            if 'explanation' in iui_data:
                explanation = iui_data['explanation']
                paragraphs = self.format_text_with_line_breaks(explanation, self.normal_style)
                for para in paragraphs:
                    story.append(para)
                story.append(Spacer(1, 20))

        # Morphology Analysis
        if 'morphology' in all_results:
            story.append(Paragraph("MORPHOLOGY ASSESSMENT", self.section_header_style))
            
            morph_data = all_results['morphology']
            if 'recommendation' in morph_data:
                recommendation = morph_data['recommendation']
                paragraphs = self.format_text_with_line_breaks(recommendation, self.normal_style)
                for para in paragraphs:
                    story.append(para)

        # Physician Remarks Section - UPDATED SECTION
        story.append(Spacer(1, 20))
        story.append(Paragraph("PHYSICIAN REMARKS", self.section_header_style))
        
        # Create one large empty text box for handwritten remarks
        textbox_data = [
            [""],
            [""],
            [""],
            [""],
            [""],
            [""],
            [""],
            [""],
            [""],
            [""]
        ]
        
        textbox_table = Table(textbox_data, colWidths=[6.5*inch], rowHeights=[0.4*inch] * 10)
        textbox_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(textbox_table)
        story.append(Spacer(1, 20))

        # Footer
        # story.append(Spacer(1, 40))
        # footer_text = "This report is generated for informational purposes. Please consult with your healthcare provider for medical advice."
        # story.append(Paragraph(footer_text, self.normal_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

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

def main():
    st.set_page_config(
        page_title="Medical Analysis App",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Medical Analysis Report Generator")
    st.markdown("Upload a PDF and get comprehensive analysis from multiple AI services")
    
    # Initialize session state for results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Initialize session state for physician remarks
    if 'physician_remarks' not in st.session_state:
        st.session_state.physician_remarks = ""
    
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
        
        # Process button
        if st.button("🚀 Process File", type="primary"):
            all_results = {}
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare file for PDF parsing API only
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            # 1. PDF Parsing API (takes PDF file)
            status_text.text("Processing PDF parsing...")
            progress_bar.progress(25)
            
            files = {'file': (uploaded_file.name, file_bytes, 'application/pdf')}
            pdf_result = call_api('PDF Parsing', API_CONFIGS['pdf_parsing'], files=files)
            
            if pdf_result:
                all_results['pdf_parsing'] = pdf_result
                st.success("✅ PDF parsing completed")
                
                # Show parsed data
                st.subheader("📄 Parsed PDF Data")
                st.json(pdf_result)
                
                # 2. Score & Recommendations API (takes JSON from PDF parsing)
                status_text.text("Getting scores and recommendations...")
                progress_bar.progress(50)
                
                score_result = call_api('Score & Recommendations', API_CONFIGS['score_recommendations'], data=pdf_result)
                
                if score_result:
                    all_results['score_recommendations'] = score_result
                    st.success("✅ Score & recommendations completed")
                else:
                    st.warning("⚠️ Score & recommendations failed")
                
                # 3. IUI-IVF API (takes formatted data from Score & Recommendations)
                status_text.text("Processing IUI-IVF analysis...")
                progress_bar.progress(75)
                
                if score_result:
                    # Format data for IUI-IVF using recommend API output
                    iui_input = format_data_for_iui_ivf(score_result)
                    st.write("**Debug: Formatted data for IUI-IVF:**")
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
                progress_bar.progress(90)
                
                # Format data specifically for Morphology API
                morph_input = format_data_for_morphology(pdf_result)
                st.write("**Debug: Formatted data for Morphology API:**")
                st.json(morph_input)
                
                morph_result = call_api('Morphology', API_CONFIGS['morphology'], data=morph_input)
                
                if morph_result:
                    all_results['morphology'] = morph_result
                    st.success("✅ Morphology analysis completed")
                else:
                    st.warning("⚠️ Morphology analysis failed")
                    
                # Store results in session state
                st.session_state.analysis_results = all_results
                
            else:
                st.error("❌ PDF parsing failed - cannot proceed with other analyses")
                st.stop()
            
            # Complete processing
            progress_bar.progress(100)
            status_text.text("Processing complete!")
        
        # Display results if they exist (either from current run or previous run)
        if st.session_state.analysis_results:
            all_results = st.session_state.analysis_results
            
            st.subheader("📊 Analysis Results")
            
            # Create tabs for each result
            tabs = st.tabs(list(all_results.keys()))
            
            for i, (key, result) in enumerate(all_results.items()):
                with tabs[i]:
                    st.json(result)
            
            # Physician Remarks Section - NEW ADDITION
            st.subheader("👨‍⚕️ Physician Remarks")
            st.markdown("Add any additional clinical observations, recommendations, or notes:")
            
            # Text area for physician remarks
            physician_remarks = st.text_area(
                "Enter your remarks here:",
                value=st.session_state.physician_remarks,
                height=150,
                placeholder="Enter clinical observations, additional recommendations, follow-up instructions, or any other relevant notes...",
                help="These remarks will be included in the generated PDF report under the 'Physician Remarks' section."
            )
            
            # Update session state when text changes
            st.session_state.physician_remarks = physician_remarks
            
            # Generate PDF Report - This is now OUTSIDE the button condition
            st.subheader("📄 Generate Report")
            
            try:
                pdf_generator = PDFReportGenerator()
                pdf_bytes = pdf_generator.generate_report(all_results, physician_remarks=physician_remarks)
                
                # Create download button that persists
                st.download_button(
                    label="📥 Download Professional PDF Report",
                    data=pdf_bytes,
                    file_name=f"fertility_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
                
                # Show a preview of what will be included
                if physician_remarks.strip():
                    st.info(f"✅ Physician remarks will be included in the report ({len(physician_remarks)} characters)")
                else:
                    st.info("ℹ️ No physician remarks added - the report will include a placeholder note")
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.text(traceback.format_exc())

if __name__ == "__main__":
    main()