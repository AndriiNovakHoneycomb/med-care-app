from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from backend.app.constants import UsersRoles
from backend.app.models import User
from backend.app.schemas import users_schema
from sqlalchemy import or_

bp = Blueprint('admins', __name__)


@bp.route('/all', methods=['GET'])
@jwt_required()
def get_admins():
    search = request.args.get('search')
    admin_users_query = User.query.filter(User.role == UsersRoles.ADMIN)

    if search:
        admin_users_query = admin_users_query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    admins_list = admin_users_query.all()

    return jsonify(users_schema.dump(admins_list)), 200
