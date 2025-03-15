from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.app import db
from backend.app.models import User, Patient, MedicalDocument, AuditLog
from backend.app.schemas import audit_logs_schema
from backend.app.utils.decorators import admin_required
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

@bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_stats():
    """Get system analytics"""
    # Get total counts
    total_users = User.query.count()
    total_patients = Patient.query.count()
    total_documents = MedicalDocument.query.count()
    
    # Get counts for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    new_documents = MedicalDocument.query.filter(
        MedicalDocument.uploaded_at >= thirty_days_ago
    ).count()
    
    # Get user distribution by role
    role_distribution = db.session.query(
        User.role, func.count(User.id)
    ).group_by(User.role).all()
    
    # Format role distribution
    role_stats = {role: count for role, count in role_distribution}
    
    return jsonify({
        "total_stats": {
            "users": total_users,
            "patients": total_patients,
            "documents": total_documents
        },
        "last_30_days": {
            "new_users": new_users,
            "new_documents": new_documents
        },
        "role_distribution": role_stats
    }), 200

@bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    """Get audit logs"""
    # Get the last 100 logs by default
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    return jsonify(audit_logs_schema.dump(logs)), 200

@bp.route('/logs/search', methods=['GET'])
@jwt_required()
@admin_required
def search_logs():
    """Search audit logs with filters"""
    # Get query parameters
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = AuditLog.query
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f'%{action}%'))
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Get results
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    
    return jsonify(audit_logs_schema.dump(logs)), 200 