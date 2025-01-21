# Standard library imports
import os
import asyncio
from typing import Dict, Any

# Third-party imports
import pytest
import mongomock
import psycopg2
from dotenv import load_dotenv
from pymongo import MongoClient

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests."""
    load_dotenv()
    
@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration."""
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "mongodb_url": os.getenv("MONGODB_URL"),
        "secret_key": os.getenv("SECRET_KEY"),
        "environment": "testing"
    }

@pytest.fixture(scope="function")
def mock_mongodb():
    """Provide a mock MongoDB client for testing."""
    return mongomock.MongoClient()

@pytest.fixture(scope="function")
def test_db():
    """Provide a test PostgreSQL database."""
    # Connect to default postgres database to create test database
    conn = psycopg2.connect(
        dbname="postgres",
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost")
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create test database
    test_db_name = f"test_db_{os.getpid()}"
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cursor.execute(f"CREATE DATABASE {test_db_name}")
    
    # Close connection to postgres database
    cursor.close()
    conn.close()
    
    # Connect to test database
    test_conn = psycopg2.connect(
        dbname=test_db_name,
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost")
    )
    
    yield test_conn
    
    # Cleanup
    test_conn.close()
    
    # Reconnect to postgres to drop test database
    conn = psycopg2.connect(
        dbname="postgres",
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost")
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cursor.close()
    conn.close()

@pytest.fixture(scope="function")
def client(test_config):
    """Create a test client for the Flask application."""
    from src.app import create_app
    app = create_app(test_config)
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def setup_test_db(test_db):
    """Set up test database tables and initial data."""
    from tests.helpers import DatabaseTestHelper
    DatabaseTestHelper.setup_postgres_tables(test_db)
    yield test_db

@pytest.fixture(scope="function")
def mock_ml_model():
    """Mock ML model for testing."""
    class MockModel:
        def predict(self, input_data):
            return ["test_pattern_1", "test_pattern_2"]
        
        def analyze(self, code):
            return {
                "patterns": ["function", "arithmetic"],
                "complexity": "low"
            }
    
    return MockModel()

@pytest.fixture(scope="function")
async def clean_mongodb(mock_mongodb):
    """Provide a clean MongoDB instance for each test."""
    from tests.helpers import DatabaseTestHelper
    await DatabaseTestHelper.clear_test_collections(mock_mongodb)
    yield mock_mongodb