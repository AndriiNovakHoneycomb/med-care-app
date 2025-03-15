from typing import Dict, Any, Optional
import openai
from flask import current_app
import json
import logging
from enum import Enum

class DocumentType(Enum):
    MEDICAL_HISTORY = "medical_history"
    LAB_REPORT = "lab_report"
    RADIOLOGY_REPORT = "radiology_report"
    PRESCRIPTION = "prescription"
    SURGICAL_REPORT = "surgical_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    PATHOLOGY_REPORT = "pathology_report"
    CONSULTATION_NOTE = "consultation_note"

class MedicalAIService:
    def __init__(self):
        self.api_key = current_app.config['AI_API_KEY']
        openai.api_key = self.api_key
        
    def _get_prompt_template(self, doc_type: DocumentType) -> Dict[str, Any]:
        """Get the appropriate prompt template for the document type"""
        prompts = {
            DocumentType.MEDICAL_HISTORY: {
                "system_prompt": """You are a medical document analyzer specialized in patient medical histories. 
                Extract and structure the following information into a clear JSON format:
                - Patient Demographics
                - Chief Complaints
                - Past Medical History
                - Family History
                - Social History
                - Current Medications
                - Allergies
                - Review of Systems
                Ensure all medical terms are preserved accurately.""",
                "output_schema": {
                    "demographics": {"age": "int", "gender": "str", "relevant_dates": "list"},
                    "chief_complaints": "list",
                    "medical_history": "dict",
                    "family_history": "dict",
                    "social_history": "dict",
                    "current_medications": "list",
                    "allergies": "list",
                    "review_of_systems": "dict"
                }
            },
            
            DocumentType.LAB_REPORT: {
                "system_prompt": """You are a medical laboratory report analyzer.
                Extract and structure the following information into a clear JSON format:
                - Test Names and Categories
                - Results with Units
                - Reference Ranges
                - Abnormal Values (flagged)
                - Collection Date/Time
                - Any Critical Values
                Highlight any values outside normal ranges.""",
                "output_schema": {
                    "test_date": "str",
                    "test_category": "str",
                    "tests": [{
                        "name": "str",
                        "value": "float",
                        "unit": "str",
                        "reference_range": "str",
                        "is_abnormal": "bool",
                        "is_critical": "bool"
                    }],
                    "summary": "str",
                    "recommendations": "list"
                }
            },
            
            DocumentType.RADIOLOGY_REPORT: {
                "system_prompt": """You are a radiology report analyzer.
                Extract and structure the following information into a clear JSON format:
                - Examination Type
                - Clinical History
                - Technique
                - Findings (by anatomical region)
                - Impressions
                - Recommendations
                Pay special attention to any critical findings or abnormalities.""",
                "output_schema": {
                    "exam_type": "str",
                    "clinical_history": "str",
                    "technique": "str",
                    "findings": {
                        "anatomical_regions": "dict",
                        "abnormalities": "list"
                    },
                    "impression": "str",
                    "recommendations": "list",
                    "critical_findings": "list"
                }
            },
            
            DocumentType.SURGICAL_REPORT: {
                "system_prompt": """You are a surgical report analyzer.
                Extract and structure the following information into a clear JSON format:
                - Procedure Name
                - Date and Duration
                - Surgeons and Assistants
                - Preoperative Diagnosis
                - Postoperative Diagnosis
                - Anesthesia Type
                - Complications
                - Estimated Blood Loss
                - Specimens Removed
                - Detailed Procedure Steps""",
                "output_schema": {
                    "procedure": {
                        "name": "str",
                        "date": "str",
                        "duration": "str"
                    },
                    "personnel": {
                        "surgeons": "list",
                        "assistants": "list"
                    },
                    "diagnosis": {
                        "preoperative": "str",
                        "postoperative": "str"
                    },
                    "details": {
                        "anesthesia": "str",
                        "complications": "list",
                        "blood_loss": "str",
                        "specimens": "list"
                    },
                    "procedure_steps": "list",
                    "key_findings": "list"
                }
            },
            
            DocumentType.DISCHARGE_SUMMARY: {
                "system_prompt": """You are a discharge summary analyzer.
                Extract and structure the following information into a clear JSON format:
                - Admission Details
                - Discharge Details
                - Principal Diagnosis
                - Secondary Diagnoses
                - Procedures Performed
                - Hospital Course
                - Discharge Medications
                - Follow-up Instructions
                - Warning Signs
                Pay special attention to care transition details.""",
                "output_schema": {
                    "admission": {
                        "date": "str",
                        "reason": "str",
                        "source": "str"
                    },
                    "discharge": {
                        "date": "str",
                        "disposition": "str"
                    },
                    "diagnoses": {
                        "principal": "str",
                        "secondary": "list"
                    },
                    "procedures": "list",
                    "hospital_course": "str",
                    "medications": {
                        "continued": "list",
                        "new": "list",
                        "discontinued": "list"
                    },
                    "follow_up": {
                        "appointments": "list",
                        "instructions": "list",
                        "warning_signs": "list"
                    }
                }
            }
        }
        
        return prompts.get(doc_type, prompts[DocumentType.MEDICAL_HISTORY])

    async def process_document(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Process a medical document and return structured data"""
        try:
            prompt_template = self._get_prompt_template(doc_type)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": prompt_template["system_prompt"]
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this {doc_type.value} and provide a structured JSON response following the specified format: \n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={ "type": "json_object" }
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "document_type": doc_type.value,
                    "data": result,
                    "schema": prompt_template["output_schema"]
                }
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON response: {e}")
                return {
                    "success": False,
                    "error": "Failed to parse AI response",
                    "document_type": doc_type.value
                }
                
        except Exception as e:
            logging.error(f"Error processing document: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_type": doc_type.value
            }

    def detect_document_type(self, text: str) -> DocumentType:
        """Detect the type of medical document based on content analysis"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical document classifier. 
                        Analyze the given text and determine if it's one of the following types:
                        - Medical History
                        - Lab Report
                        - Radiology Report
                        - Surgical Report
                        - Discharge Summary
                        Return ONLY the document type as a single string matching one of the above exactly."""
                    },
                    {
                        "role": "user",
                        "content": text[:1000]  # Use first 1000 chars for classification
                    }
                ],
                temperature=0.3,
                max_tokens=20
            )
            
            doc_type = response.choices[0].message.content.strip().lower().replace(" ", "_")
            return DocumentType(doc_type)
            
        except Exception as e:
            logging.error(f"Error detecting document type: {e}")
            return DocumentType.MEDICAL_HISTORY  # Default to medical history

    def generate_summary(self, structured_data: Dict[str, Any], doc_type: DocumentType) -> str:
        """Generate a human-readable summary from structured data"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical document summarizer.
                        Create a clear, concise summary of the structured medical data provided.
                        Focus on key findings, abnormalities, and actionable items.
                        Use professional medical terminology while maintaining readability."""
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this {doc_type.value} data:\n{json.dumps(structured_data, indent=2)}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return "Error generating summary" 