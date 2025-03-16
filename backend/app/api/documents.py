from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.app import db, celery
from backend.app.models import User, Patient, MedicalDocument, AuditLog
from backend.app.schemas import medical_document_schema, medical_documents_schema
from backend.app.utils.decorators import patient_required, admin_required
from backend.app.utils.storage import upload_file_to_s3, delete_file_from_s3, get_file_from_s3, generate_presigned_url
from backend.app.services.medical_ai_service import MedicalAIService
from io import BytesIO
import os
import uuid
import logging
from pypdf import PdfReader

bp = Blueprint('documents', __name__)

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a medical document"""
    if 'file' not in request.files:
        return jsonify({"msg": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400
    
    # Get user_id from request
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({"msg": "No user_id provided"}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"msg": "File type not allowed"}), 400
    
    # Get current user for permission check
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Find patient by user_id
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404
    
    # Check permissions
    if current_user.role == 'Patient' and str(current_user_id) != str(user_id):
        return jsonify({"msg": "Access denied"}), 403
    
    # Secure filename and generate unique name
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Upload to S3
    try:
        file_path = upload_file_to_s3(file, unique_filename)
    except Exception as e:
        return jsonify({"msg": "Error uploading file", "error": str(e)}), 500
    
    # Create document record
    document = MedicalDocument(
        patient_id=patient.id,
        title=request.form.get('title', filename),
        file_path=file_path
    )
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Uploaded medical document",
        details={
            "document_id": str(document.id),
            "filename": filename,
            "patient_id": str(patient.id)
        }
    )
    
    db.session.add(document)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        "msg": "Document uploaded successfully",
        "document": medical_document_schema.dump(document)
    }), 201

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_document(id):
    """Get document details"""
    document = MedicalDocument.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check access permissions
    if user.role == 'Patient' and document.patient.user_id != current_user_id:
        return jsonify({"msg": "Access denied"}), 403
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Retrieved document details",
        details={"document_id": str(id)}
    )
    db.session.add(log)
    db.session.commit()

    doc_link = generate_presigned_url(document.file_path)

    return jsonify({"link": doc_link}), 200

@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_document(id):
    """Delete document"""
    document = MedicalDocument.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check access permissions
    if user.role == 'Patient' and document.patient.user_id != current_user_id:
        return jsonify({"msg": "Access denied"}), 403
    
    # Delete from S3
    try:
        delete_file_from_s3(document.file_path)
    except Exception as e:
        return jsonify({"msg": "Error deleting file", "error": str(e)}), 500
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Deleted medical document",
        details={
            "document_id": str(id),
            "patient_id": str(document.patient_id)
        }
    )
    
    db.session.delete(document)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"msg": "Document deleted successfully"}), 200

@bp.route('/patients/<uuid:patient_id>/documents', methods=['GET'])
@jwt_required()
def get_patient_documents(patient_id):
    """Get all documents for a patient"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    print(user)
    
    # First fetch the patient by user_id
    patient = Patient.query.filter_by(user_id=patient_id).first()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404
    
    # Check access permissions
    if user.role == 'Patient' and str(user.patient.id) != str(patient.id):
        return jsonify({"msg": "Access denied"}), 403
    
    documents = MedicalDocument.query.filter_by(patient_id=patient.id).all()
    print(documents)
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Retrieved patient documents",
        details={"patient_id": str(patient.id)}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(medical_documents_schema.dump(documents)), 200

@bp.route('/patients/agreement', methods=['GET'])
@jwt_required()
def get_patient_agreement():
    doc_link = generate_presigned_url('patient-treatment-agreement.pdf')
    return jsonify({"link": doc_link}), 200

@bp.route('/<uuid:id>/summarize', methods=['POST'])
@jwt_required()
def summarize_document(id):
    """Trigger document summarization"""
    document = MedicalDocument.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check access permissions
    if user.role == 'Patient' and document.patient.user_id != current_user_id:
        return jsonify({"msg": "Access denied"}), 403
    
    # Trigger async summarization task
    task = generate_document_summary.delay(str(id))
    
    return jsonify({
        "msg": "Document summarization started",
        "task_id": task.id
    }), 202

@bp.route('/patients/<uuid:patient_id>/analyze', methods=['POST'])
@jwt_required()
async def analyze_patient_documents(patient_id):
    """Analyze all medical documents for a patient and generate a comprehensive summary PDF"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # First fetch the patient by user_id
    patient = Patient.query.filter_by(user_id=patient_id).first()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404
    
    # Check access permissions
    if user.role == 'Patient' and str(user.patient.id) != str(patient.id):
        return jsonify({"msg": "Access denied"}), 403
    
    try:
        # Fetch all documents for the patient using patient.id
        documents = MedicalDocument.query.filter_by(patient_id=patient.id).all()
        
        if not documents:
            return jsonify({
                "success": False,
                "error": "No documents found for this patient"
            }), 404
        
        # Prepare documents for analysis
        doc_list = []
        for doc in documents:
            try:
                # Get file content from S3
                file_obj = get_file_from_s3(doc.file_path)
                file_bytes = file_obj.read()
                
                # Check if it's a PDF file
                if doc.file_path.lower().endswith('.pdf'):
                    # Create a BytesIO object from the file bytes
                    pdf_file = BytesIO(file_bytes)
                    # Create PDF reader object
                    reader = PdfReader(pdf_file)
                    # Extract text from all pages
                    content = ""
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
                else:
                    # For non-PDF files, try UTF-8 decoding
                    content = file_bytes.decode('utf-8')
                
                doc_list.append({
                    'content': content,
                    'date': doc.uploaded_at.isoformat(),
                    'title': doc.title
                })
            except Exception as e:
                logging.error(f"Error reading document {doc.id}: {str(e)}")
                continue
        
        if not doc_list:
            return jsonify({
                "success": False,
                "error": "Could not process any documents"
            }), 500
        
        # Initialize AI service and process documents
        ai_service = MedicalAIService()
        result = await ai_service.process_medical_documents(
            patient_id=str(patient.id),
            documents=doc_list
        )
        
        if not result['success']:
            return jsonify(result), 500
            
        # Create PDF response
        pdf_buffer = BytesIO(result['pdf_data'])
        pdf_buffer.seek(0)
        
        # Log the action
        log = AuditLog(
            user_id=current_user_id,
            action="Generated patient document summary",
            details={
                "patient_id": str(patient.id),
                "document_count": result['document_count']
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'patient_{patient.id}_medical_summary.pdf'
        )
        
    except Exception as e:
        logging.error(f"Error analyzing patient documents: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to analyze documents: {str(e)}"
        }), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['pdf', 'doc', 'docx']