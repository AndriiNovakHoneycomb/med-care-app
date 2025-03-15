import pytest
from backend.app import create_app, db
from backend.app.models import User, Patient, MedicalDocument
from config import Config
import os
import tempfile
import uuid

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    UPLOAD_FOLDER = tempfile.mkdtemp()
    S3_BUCKET = 'test-bucket'
    AI_API_KEY = 'test-api-key'

@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    app = create_app(TestConfig)
    
    # Create test database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create authentication headers with a test token"""
    # Create a test user
    with client.application.app_context():
        user = User(email='test@example.com', password='testpass123', role='Patient')
        db.session.add(user)
        db.session.commit()
        
        # Login to get tokens
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        token = response.json['access_token']
        
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_headers(client):
    """Create authentication headers for an admin user"""
    with client.application.app_context():
        admin = User(email='admin@example.com', password='adminpass123', role='Admin')
        db.session.add(admin)
        db.session.commit()
        
        response = client.post('/auth/login', json={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })
        token = response.json['access_token']
        
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_patient(app):
    """Create a test patient"""
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        patient = Patient(
            user_id=user.id,
            first_name='Test',
            last_name='Patient',
            dob='1990-01-01'
        )
        db.session.add(patient)
        db.session.commit()
        return patient

@pytest.fixture
def test_document(app, test_patient):
    """Create a test medical document"""
    with app.app_context():
        document = MedicalDocument(
            patient_id=test_patient.id,
            title='Test Document',
            file_path=f'documents/{uuid.uuid4()}.pdf',
            summary='Test summary'
        )
        db.session.add(document)
        db.session.commit()
        return document 