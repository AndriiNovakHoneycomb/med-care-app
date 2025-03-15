from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app import db
from app.models import User, TokenBlocklist
from app.schemas import user_schema, login_schema
from datetime import datetime
from app.constants import UsersRoles

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    data["role"] = UsersRoles.ADMIN
    name = data.pop('name')
    first_name, *last_part = name.split(' ')
    data["first_name"] = first_name
    data["last_name"] = ' '.join(last_part)

    
    errors = user_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 422
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered"}), 409
    
    user = User(
        email=data['email'],
        password=data['password'],
        role=data['role'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "msg": "User created successfully",
        "user": user_schema.dump(user)
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "No input data provided"}), 400
    
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 422
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_schema.dump(user)
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "access_token": access_token
    }), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Revoke access token"""
    jti = get_jwt()["jti"]
    now = datetime.utcnow()
    
    token_block = TokenBlocklist(jti=jti, created_at=now)
    db.session.add(token_block)
    db.session.commit()
    
    return jsonify({"msg": "Successfully logged out"}), 200

# Callback function to check if a JWT exists in the database blocklist
# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token = TokenBlocklist.query.filter_by(jti=jti).first()
#     return token is not None