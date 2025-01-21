import pytest
from flask import url_for
from http import HTTPStatus
from src.app import create_app

@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test_key'
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

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json == {'status': 'healthy'}

def test_not_found_error(client):
    """Test 404 error handler."""
    response = client.get('/nonexistent')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'error' in response.json