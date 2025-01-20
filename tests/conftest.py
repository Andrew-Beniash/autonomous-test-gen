import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests."""
    load_dotenv()
    
@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "mongodb_url": os.getenv("MONGODB_URL"),
        "secret_key": os.getenv("SECRET_KEY"),
    }