from flask import Blueprint, request, jsonify, send_file
from medical_ai_service import MedicalAIService
from models.document import Document  # Assuming you have a Document model
from io import BytesIO
import logging

bp = Blueprint('medical_documents', __name__)
medical_ai_service = MedicalAIService()

@bp.route('/api/patients/<patient_id>/summary', methods=['GET'])
async def get_patient_summary(patient_id):
    """
    Generate a comprehensive medical summary for a patient
    Returns a PDF containing an AI-generated summary of all patient's medical documents
    """
    try:
        # Fetch all documents for the patient
        documents = Document.query.filter_by(patient_id=patient_id).all()
        
        # Process documents and generate summary
        result = await medical_ai_service.generate_patient_summary(
            patient_id=patient_id,
            documents=[{
                'content': doc.content,
                'date': doc.created_at.isoformat(),
                'type': doc.document_type
            } for doc in documents]
        )
        
        if not result['success']:
            return jsonify(result), 404 if "No medical documents found" in result['error'] else 500
            
        # Return PDF file
        pdf_buffer = BytesIO(result['pdf_summary'])
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'patient_{patient_id}_medical_summary.pdf'
        )
        
    except Exception as e:
        logging.error(f"Error generating patient summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate patient summary'
        }), 500 