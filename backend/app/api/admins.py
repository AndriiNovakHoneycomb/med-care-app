from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.app.constants import UsersRoles
from backend.app.models import User, Patient, AuditLog
from backend.app.schemas import users_schema, patient_schema
from backend.app.utils.decorators import admin_required

bp = Blueprint('admins', __name__)


@bp.route('/all', methods=['GET'])
@jwt_required()
def get_admins():
    admin_users = User.query.filter_by(role=UsersRoles.ADMIN)

    return jsonify(users_schema.dump(admin_users)), 200
