from typing import Dict, Any, List
import openai
from flask import current_app
import json
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime

class MedicalAIService:
    def __init__(self):
        self.api_key = current_app.config['AI_API_KEY']
        openai.api_key = self.api_key

    async def process_medical_documents(self, patient_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process medical documents and generate a comprehensive summary PDF
        
        Args:
            patient_id: The unique identifier for the patient
            documents: List of dictionaries containing:
                      - content: str (text content of the document)
                      - date: str (document date)
                      - title: str (document title/description)
        
        Returns:
            Dict containing:
            - success: bool
            - pdf_data: bytes (if successful)
            - error: str (if unsuccessful)
        """
        if not documents:
            return {
                "success": False,
                "error": f"No medical documents provided for patient ID: {patient_id}"
            }

        try:
            # Combine all documents with metadata
            combined_text = "\n\n".join([
                f"Document: {doc.get('title', 'Untitled')}\n"
                f"Date: {doc.get('date', 'Unknown')}\n"
                f"Content:\n{doc['content']}\n"
                f"{'='*50}"
                for doc in documents
            ])

            # Generate comprehensive analysis using GPT-4
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert medical document analyzer.
                        Create a comprehensive medical summary from the provided documents.
                        Structure your response in the following sections:

                        1. Patient Overview
                           - Demographics and Basic Information
                           - Primary Medical Conditions
                           - Significant Medical History

                        2. Current Health Status
                           - Active Medical Conditions
                           - Current Medications
                           - Recent Test Results
                           - Vital Signs and Trends

                        3. Medical History Timeline
                           - Chronological list of significant medical events
                           - Procedures and Surgeries
                           - Major Diagnoses and Changes in Treatment

                        4. Risk Assessment
                           - Current Health Risks
                           - Family History Concerns
                           - Lifestyle Factors
                           - Allergies and Adverse Reactions

                        5. Treatment Plan
                           - Current Treatment Regimens
                           - Medication Schedule
                           - Ongoing Monitoring Requirements
                           - Lifestyle Recommendations

                        6. Critical Information
                           - Urgent Concerns
                           - Required Follow-ups
                           - Warning Signs to Monitor
                           - Emergency Response Instructions

                        Format the response as a JSON object with these sections as keys.
                        For each section, provide detailed information while highlighting any critical or abnormal findings.
                        Include specific dates where available and relevant."""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze these medical documents for patient ID {patient_id} and create a comprehensive summary:\n\n{combined_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={ "type": "json_object" }
            )

            summary_data = json.loads(response.choices[0].message.content)
            
            # Generate PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Custom styles
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading1'],
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=20,
                fontSize=14,
                leading=16
            )

            subheader_style = ParagraphStyle(
                'CustomSubHeader',
                parent=styles['Heading2'],
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12,
                fontSize=12,
                leading=14
            )

            # Add title and metadata
            story.append(Paragraph(f"Comprehensive Medical Summary", header_style))
            story.append(Paragraph(f"Patient ID: {patient_id}", subheader_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            story.append(Paragraph(f"Based on {len(documents)} medical documents", styles['Normal']))
            story.append(Spacer(1, 20))

            # Add each section
            for section, content in summary_data.items():
                section_title = section.replace('_', ' ').title()
                story.append(Paragraph(section_title, header_style))
                
                if isinstance(content, dict):
                    for key, value in content.items():
                        subsection_title = key.replace('_', ' ').title()
                        story.append(Paragraph(subsection_title, subheader_style))
                        if isinstance(value, list):
                            for item in value:
                                story.append(Paragraph(f"• {item}", styles['Normal']))
                        else:
                            story.append(Paragraph(str(value), styles['Normal']))
                elif isinstance(content, list):
                    for item in content:
                        story.append(Paragraph(f"• {item}", styles['Normal']))
                else:
                    story.append(Paragraph(str(content), styles['Normal']))
                
                story.append(Spacer(1, 15))

            doc.build(story)
            pdf_data = pdf_buffer.getvalue()

            return {
                "success": True,
                "patient_id": patient_id,
                "pdf_data": pdf_data,
                "summary_data": summary_data,
                "document_count": len(documents)
            }

        except Exception as e:
            logging.error(f"Error processing medical documents: {e}")
            return {
                "success": False,
                "error": f"Failed to process documents: {str(e)}",
                "patient_id": patient_id
            } 