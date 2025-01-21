import pytest
from http import HTTPStatus
from src.app import create_app

@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test_key',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db'
    })
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

def test_app_creation(app):
    """Test that the app is created with testing config."""
    assert app.config['TESTING']
    assert app.config['SECRET_KEY'] == 'test_key'
    assert 'DATABASE_URL' in app.config

def test_health_check_success(client):
    """Test successful health check endpoint response."""
    response = client.get('/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json == {'status': 'healthy'}
    assert response.headers['Content-Type'] == 'application/json'

def test_health_check_method_not_allowed(client):
    """Test health check endpoint with invalid HTTP methods."""
    invalid_methods = ['POST', 'PUT', 'DELETE', 'PATCH']
    for method in invalid_methods:
        response = client.open('/health', method=method)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

def test_not_found_error_response(client):
    """Test 404 error handler response format."""
    response = client.get('/nonexistent')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json['error'] == 'Not Found'
    assert 'message' in response.json
    assert response.headers['Content-Type'] == 'application/json'

def test_not_found_error_different_paths(client):
    """Test 404 error handler with various nonexistent paths."""
    test_paths = ['/api', '/health/', '/api/v1', '/invalid']
    for path in test_paths:
        response = client.get(path)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json['error'] == 'Not Found'