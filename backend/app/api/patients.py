from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.constants import UsersRoles, UsersStatus
from backend.app.models import User, Patient, AuditLog, MedicalDocument
from backend.app.schemas import users_schema, patients_schema
from backend.app.utils.decorators import admin_required

bp = Blueprint('patients', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    patients_list = User.query.filter_by(role=UsersRoles.PATIENT)

    return jsonify(users_schema.dump(patients_list)), 200

@bp.route('/<uuid:user_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(user_id):
    current_user = User.query.filter_by(id=user_id).one_or_none()
    if current_user is not None:
        audit_logs = AuditLog.query.filter_by(user_id=user_id).all()
        for log in audit_logs:
            db.session.delete(log)
        current_patient = Patient.query.filter_by(user_id=user_id).one_or_none()
        med_docs = MedicalDocument.query.filter_by(patient_id=current_patient.id).all()
        for doc in med_docs:
            db.session.delete(doc)

        db.session.delete(current_patient)
        db.session.delete(current_user)
        db.session.commit()
        return jsonify({"msg": "Patient deleted successfully"}), 200

@bp.route('/<uuid:user_id>/status', methods=['PATCH'])
@jwt_required()
def change_patient_status(user_id):
    current_user = User.query.filter_by(id=user_id).one_or_none()
    if current_user is not None:
        current_user.status = UsersStatus.APPROVED if current_user.status == UsersStatus.UNAPPROVED else UsersStatus.UNAPPROVED
        db.session.add(current_user)
        db.session.commit()

        return jsonify({"msg": "Patient status changed successfully"}), 200
