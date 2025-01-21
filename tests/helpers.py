from typing import Dict, Any, Optional
import json
from datetime import datetime
import pytest
from bson import ObjectId
import jwt
import os

class TestDataGenerator:
    """Helper class to generate test data for integration tests."""
    
    @staticmethod
    def generate_test_code_snippet() -> Dict[str, Any]:
        """Generate a test code snippet for analysis."""
        return {
            "code": """
                def add_numbers(a: int, b: int) -> int:
                    return a + b
            """,
            "language": "python",
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def generate_test_pattern() -> Dict[str, Any]:
        """Generate a test pattern for ML model."""
        return {
            "pattern_name": "basic_arithmetic",
            "code_pattern": "function_with_two_params",
            "test_template": """
                def test_{func_name}():
                    assert {func_name}(1, 2) == 3
                    assert {func_name}(-1, 1) == 0
            """
        }

class DatabaseTestHelper:
    """Helper class for database operations in tests."""
    
    @staticmethod
    async def clear_test_collections(mongo_client: Any) -> None:
        """Clear all test collections in MongoDB."""
        db = mongo_client.test_db
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})
    
    @staticmethod
    def setup_postgres_tables(pg_conn: Any) -> None:
        """Set up necessary tables in PostgreSQL test database."""
        with pg_conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            pg_conn.commit()

class AuthTestHelper:
    """Helper class for authentication in tests."""
    
    @staticmethod
    def generate_test_token(user_id: str = "test_user") -> str:
        """Generate a test JWT token."""
        secret_key = os.getenv("SECRET_KEY", "test-secret-key")
        token = jwt.encode(
            {"user_id": user_id, "exp": datetime.utcnow().timestamp() + 3600},
            secret_key,
            algorithm="HS256"
        )
        return token
    
    @staticmethod
    def get_auth_headers(token: Optional[str] = None) -> Dict[str, str]:
        """
        Get headers with authentication token.
        
        Args:
            token: Optional JWT token. If None, a new token will be generated.
            
        Returns:
            Dict containing Authorization header with Bearer token.
        """
        if token is None:
            token = AuthTestHelper.generate_test_token()
        return {"Authorization": f"Bearer {token}"}

def async_test(coro):
    """Decorator for async test functions."""
    def wrapper(*args, **kwargs):
        import asyncio
        return asyncio.run(coro(*args, **kwargs))
    return wrapper