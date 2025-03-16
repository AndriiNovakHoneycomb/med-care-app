from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.constants import UsersRoles
from backend.app.models import User, Patient, AuditLog
from backend.app.schemas import users_schema, patients_schema
from backend.app.utils.decorators import admin_required

bp = Blueprint('patients', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    patients_list = User.query.filter_by(role=UsersRoles.PATIENT)

    return jsonify(users_schema.dump(patients_list)), 200

@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_patient():
    current_patient = User.query.filter_by(id=id).one_or_none()
    if current_patient is not None:
        db.session.delete(current_patient)
        db.session.commit()
        return jsonify({"msg": "Patient deleted successfully"}), 200
