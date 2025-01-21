import pytest
from src.app import create_app
from http import HTTPStatus

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

def test_health_check_integration(client):
    """Test the health check endpoint with integration setup."""
    response = client.get('/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json['status'] == 'healthy'
    # Additional integration checks can be added here

def test_error_handling_integration(client):
    """Test error handling in integration environment."""
    response = client.get('/nonexistent')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'error' in response.json
    assert 'message' in response.json