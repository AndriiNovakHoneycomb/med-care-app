from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Patient, AuditLog
from app.schemas import user_schema, patient_schema
from app.utils.decorators import admin_required
from datetime import datetime

bp = Blueprint('users', __name__)

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user details"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Retrieved user profile",
        details={"user_id": str(current_user_id)}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(user_schema.dump(user)), 200

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(id):
    """Get user details (Admin only)"""
    user = User.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Retrieved user details",
        details={"target_user_id": str(id)}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(user_schema.dump(user)), 200

@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(id):
    """Delete user (Admin only)"""
    user = User.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    if str(user.id) == current_user_id:
        return jsonify({"msg": "Cannot delete yourself"}), 400
    
    # Log the action before deletion
    log = AuditLog(
        user_id=current_user_id,
        action="Deleted user",
        details={
            "deleted_user_id": str(id),
            "deleted_user_email": user.email,
            "deleted_user_role": user.role
        }
    )
    
    db.session.delete(user)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"msg": "User deleted successfully"}), 200

@bp.route('/patient-profile', methods=['POST'])
@jwt_required()
def create_patient_profile():
    """Create patient profile for current user"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    if user.role != 'Patient':
        return jsonify({"msg": "Only patients can create patient profiles"}), 403
    
    if user.patient:
        return jsonify({"msg": "Patient profile already exists"}), 409
    
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No input data provided"}), 400
    
    errors = patient_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 422
    
    patient = Patient(
        user_id=current_user_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        dob=data['dob']
    )
    
    # Log the action
    log = AuditLog(
        user_id=current_user_id,
        action="Created patient profile",
        details={"patient_id": str(patient.id)}
    )
    
    db.session.add(patient)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        "msg": "Patient profile created successfully",
        "patient": patient_schema.dump(patient)
    }), 201 