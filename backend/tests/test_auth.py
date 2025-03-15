def test_register(client):
    """Test user registration"""
    response = client.post('/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'password123',
        'role': 'Patient'
    })
    assert response.status_code == 201
    assert 'user' in response.json
    assert response.json['user']['email'] == 'newuser@example.com'

def test_register_duplicate_email(client, auth_headers):
    """Test registration with existing email"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'Patient'
    })
    assert response.status_code == 409

def test_login_success(client):
    """Test successful login"""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    assert 'user' in response.json

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_refresh_token(client, auth_headers):
    """Test token refresh"""
    response = client.post('/auth/refresh', headers=auth_headers)
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_logout(client, auth_headers):
    """Test logout"""
    response = client.post('/auth/logout', headers=auth_headers)
    assert response.status_code == 200

def test_unauthorized_access(client):
    """Test accessing protected endpoint without token"""
    response = client.get('/users/me')
    assert response.status_code == 401 