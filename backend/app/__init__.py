from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from celery import Celery
from config import Config
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
    CORS(app)

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

    # Register blueprints
    # from backend.app.api import bp as api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    from app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app

def init_celery(app=None):
    app = app or create_app()
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery 