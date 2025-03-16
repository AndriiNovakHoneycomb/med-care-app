from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from celery import Celery
from backend.config import Config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
celery = Celery()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS properly
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Configure Celery
    celery.conf.update(app.config)

    # Configure Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Medical Document Management System API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Register blueprints with /api prefix
    from backend.app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from backend.app.api.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from backend.app.api.admins import bp as admins_bp
    app.register_blueprint(admins_bp, url_prefix='/api/admins')

    from backend.app.api.patients import bp as patients_bp
    app.register_blueprint(patients_bp, url_prefix='/api/patients')

    @app.route('/')
    def main_route():
        return {'status': 'healthy'}, 200

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    from .cli import register_commands
    register_commands(app)

    return app
