import io
import json
from backend.app.models import MedicalDocument

def test_upload_document(client, auth_headers, test_patient):
    """Test document upload"""
    data = {
        'file': (io.BytesIO(b'test file content'), 'test.pdf'),
        'title': 'Test Document'
    }
    response = client.post(
        '/documents/upload',
        data=data,
        headers={**auth_headers, 'Content-Type': 'multipart/form-data'}
    )
    assert response.status_code == 201
    assert 'document' in response.json
    assert response.json['document']['title'] == 'Test Document'

def test_get_document(client, auth_headers, test_document):
    """Test getting document details"""
    response = client.get(
        f'/documents/{test_document.id}',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['id'] == str(test_document.id)
    assert response.json['title'] == test_document.title

def test_delete_document(client, auth_headers, test_document, app):
    """Test document deletion"""
    response = client.delete(
        f'/documents/{test_document.id}',
        headers=auth_headers
    )
    assert response.status_code == 200
    
    with app.app_context():
        assert MedicalDocument.query.get(test_document.id) is None

def test_analyze_document(client, auth_headers, test_document):
    """Test document analysis"""
    response = client.post(
        f'/documents/{test_document.id}/analyze',
        headers=auth_headers,
        json={'document_type': 'medical_history'}
    )
    assert response.status_code == 200
    assert 'structured_data' in response.json
    assert 'summary' in response.json

def test_summarize_document(client, auth_headers, test_document):
    """Test document summarization"""
    response = client.post(
        f'/documents/{test_document.id}/summarize',
        headers=auth_headers
    )
    assert response.status_code == 202
    assert 'task_id' in response.json

def test_get_patient_documents(client, auth_headers, test_patient, test_document):
    """Test getting all documents for a patient"""
    response = client.get(
        f'/patients/{test_patient.id}/documents',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['id'] == str(test_document.id)

def test_unauthorized_document_access(client, auth_headers, test_document):
    """Test accessing document without proper permissions"""
    # Create another user's headers
    response = client.post('/auth/register', json={
        'email': 'other@example.com',
        'password': 'password123',
        'role': 'Patient'
    })
    other_response = client.post('/auth/login', json={
        'email': 'other@example.com',
        'password': 'password123'
    })
    other_headers = {'Authorization': f'Bearer {other_response.json["access_token"]}'}
    
    # Try to access document
    response = client.get(
        f'/documents/{test_document.id}',
        headers=other_headers
    )
    assert response.status_code == 403 