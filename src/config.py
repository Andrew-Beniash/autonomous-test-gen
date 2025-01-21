import os
from typing import Dict, Any

class Config:
    """Base configuration."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/test_gen_db')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DATABASE_URL = 'postgresql://localhost:5432/test_gen_db_test'

class ProductionConfig(Config):
    """Production configuration."""
    
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY must be set in production!")