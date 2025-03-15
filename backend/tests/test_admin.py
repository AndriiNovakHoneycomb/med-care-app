def test_get_stats(client, admin_headers):
    """Test getting system statistics"""
    response = client.get('/admin/stats', headers=admin_headers)
    assert response.status_code == 200
    assert 'total_stats' in response.json
    assert 'last_30_days' in response.json
    assert 'role_distribution' in response.json

def test_get_audit_logs(client, admin_headers):
    """Test getting audit logs"""
    response = client.get('/admin/logs', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_search_audit_logs(client, admin_headers):
    """Test searching audit logs"""
    response = client.get(
        '/admin/logs/search?action=login&start_date=2024-01-01',
        headers=admin_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_unauthorized_admin_access(client, auth_headers):
    """Test accessing admin endpoints with non-admin user"""
    response = client.get('/admin/stats', headers=auth_headers)
    assert response.status_code == 403

def test_admin_user_management(client, admin_headers):
    """Test admin user management capabilities"""
    # Create a test user
    response = client.post('/auth/register', json={
        'email': 'testuser@example.com',
        'password': 'password123',
        'role': 'Patient'
    })
    user_id = response.json['user']['id']
    
    # Get user details
    response = client.get(f'/users/{user_id}', headers=admin_headers)
    assert response.status_code == 200
    assert response.json['email'] == 'testuser@example.com'
    
    # Delete user
    response = client.delete(f'/users/{user_id}', headers=admin_headers)
    assert response.status_code == 200
    
    # Verify user is deleted
    response = client.get(f'/users/{user_id}', headers=admin_headers)
    assert response.status_code == 404 