from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.app import db, celery
from backend.app.models import User, Patient, MedicalDocument, AuditLog
from backend.app.schemas import medical_document_schema, medical_documents_schema
from backend.app.utils.decorators import patient_required, admin_required
from backend.app.utils.storage import upload_file_to_s3, delete_file_from_s3, get_file_from_s3
from backend.app.services.medical_ai_service import MedicalAIService, DocumentType
import os
import uuid

bp = Blueprint('documents', __name__)

@bp.route('/upload', methods=['POST'])
@jwt_required()
@patient_required
def upload_document():
    """Upload a medical document"""
    if 'file' not in request.files:
        return jsonify({"msg": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"msg": "File type not allowed"}), 400
    
    current_user_id = get_jwt_identity()
    patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    if not patient:
        return jsonify({"msg": "Patient profile not found"}), 404
    
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
            "filename": filename
        }
    )
    
    db.session.add(document)
    db.session.add(log)
    db.session.commit()
    
    # Trigger async document summarization
    generate_document_summary.delay(str(document.id))
    
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
    
    return jsonify(medical_document_schema.dump(document)), 200

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
    
    # Check access permissions
    if user.role == 'Patient' and str(user.patient.id) != str(patient_id):
        return jsonify({"msg": "Access denied"}), 403
    
    documents = MedicalDocument.query.filter_by(patient_id=patient_id).all()
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Retrieved patient documents",
        details={"patient_id": str(patient_id)}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(medical_documents_schema.dump(documents)), 200

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

@bp.route('/<uuid:id>/analyze', methods=['POST'])
@jwt_required()
async def analyze_document(id):
    """Analyze a medical document using AI"""
    document = MedicalDocument.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check access permissions
    if user.role == 'Patient' and document.patient.user_id != current_user_id:
        return jsonify({"msg": "Access denied"}), 403
    
    try:
        # Get file content from S3
        file_obj = get_file_from_s3(document.file_path)
        text_content = file_obj.read().decode('utf-8')
        
        # Initialize AI service
        ai_service = MedicalAIService()
        
        # Detect document type if not provided
        doc_type = request.json.get('document_type', None)
        if doc_type:
            try:
                doc_type = DocumentType(doc_type)
            except ValueError:
                doc_type = ai_service.detect_document_type(text_content)
        else:
            doc_type = ai_service.detect_document_type(text_content)
        
        # Process document
        result = await ai_service.process_document(text_content, doc_type)
        
        if result["success"]:
            # Generate human-readable summary
            summary = ai_service.generate_summary(result["data"], doc_type)
            
            # Update document with structured data and summary
            document.summary = summary
            db.session.commit()
            
            # Log the action
            log = AuditLog(
                user_id=current_user_id,
                action="Analyzed medical document",
                details={
                    "document_id": str(id),
                    "document_type": doc_type.value,
                    "analysis_success": True
                }
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                "msg": "Document analyzed successfully",
                "document_type": doc_type.value,
                "structured_data": result["data"],
                "summary": summary
            }), 200
        else:
            # Log the failure
            log = AuditLog(
                user_id=current_user_id,
                action="Failed to analyze medical document",
                details={
                    "document_id": str(id),
                    "error": result.get("error", "Unknown error")
                }
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                "msg": "Failed to analyze document",
                "error": result.get("error", "Unknown error")
            }), 500
            
    except Exception as e:
        # Log the error
        log = AuditLog(
            user_id=current_user_id,
            action="Error analyzing medical document",
            details={
                "document_id": str(id),
                "error": str(e)
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "msg": "Error analyzing document",
            "error": str(e)
        }), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['UPLOAD_EXTENSIONS'] 