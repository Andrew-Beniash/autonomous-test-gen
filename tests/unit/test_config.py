import os
import pytest
from src.core.config import Config

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Setup mock environment variables for testing."""
    monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
    monkeypatch.setenv('MONGODB_URL', 'mongodb://test:test@localhost:27017/test_db')
    monkeypatch.setenv('SECRET_KEY', 'test_secret')
    monkeypatch.setenv('DEBUG', 'true')

def test_config_loads_environment_variables(mock_env_vars):
    """Test that configuration loads from environment variables."""
    config = Config()
    assert config.database_url == 'postgresql://test:test@localhost:5432/test_db'
    assert config.mongodb_url == 'mongodb://test:test@localhost:27017/test_db'
    assert config.secret_key == 'test_secret'
    assert config.debug is True

def test_config_uses_defaults_when_env_vars_missing(monkeypatch):
    """Test that configuration uses defaults when environment variables are not set."""
    # Clear any existing environment variables
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.delenv('MONGODB_URL', raising=False)
    monkeypatch.delenv('SECRET_KEY', raising=False)
    monkeypatch.delenv('DEBUG', raising=False)
    
    config = Config()
    assert config.database_url == 'postgresql://test:test@localhost:5432/test_db'
    assert config.mongodb_url == 'mongodb://test:test@localhost:27017/test_db'
    assert config.secret_key == 'dev'
    assert config.debug is False

def test_config_validates_required_variables():
    """Test that configuration validates required variables."""
    with pytest.raises(ValueError, match="DATABASE_URL must be set"):
        Config(database_url='')
    
    with pytest.raises(ValueError, match="MONGODB_URL must be set"):
        Config(mongodb_url='')
    
    with pytest.raises(ValueError, match="SECRET_KEY must be set"):
        Config(secret_key='')

def test_config_validates_url_formats():
    """Test that configuration validates URL formats."""
    with pytest.raises(ValueError, match="DATABASE_URL must be a PostgreSQL URL"):
        Config(database_url='mysql://localhost/db')
    
    with pytest.raises(ValueError, match="MONGODB_URL must be a MongoDB URL"):
        Config(mongodb_url='redis://localhost/0')

def test_config_as_dict():
    """Test conversion of configuration to dictionary."""
    config = Config()
    config_dict = config.as_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['DATABASE_URL'] == config.database_url
    assert config_dict['MONGODB_URL'] == config.mongodb_url
    assert config_dict['SECRET_KEY'] == config.secret_key
    assert config_dict['DEBUG'] == config.debug
    assert config_dict['TESTING'] == config.testing

def test_config_from_env():
    """Test creating configuration from environment variables."""
    config = Config.from_env()
    assert isinstance(config, Config)
    assert config.database_url.startswith('postgresql://')
    assert config.mongodb_url.startswith('mongodb://')