import pytest
from pymongo import MongoClient
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def postgres_connection():
    """Create a PostgreSQL connection for testing."""
    conn = psycopg2.connect(
        dbname="test_gen_db",
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    yield conn
    conn.close()

@pytest.fixture
def mongo_connection():
    """Create a MongoDB connection for testing."""
    client = MongoClient(
        host=os.getenv("MONGODB_HOST", "localhost"),
        port=int(os.getenv("MONGODB_PORT", "27017")),
        username=os.getenv("MONGODB_USER"),
        password=os.getenv("MONGODB_PASSWORD")
    )
    yield client
    client.close()

def test_postgres_connection(postgres_connection):
    """Test PostgreSQL connection and basic operations."""
    cursor = postgres_connection.cursor()
    
    # Create a test table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("test_name",))
    
    # Query the data
    cursor.execute("SELECT name FROM test_table WHERE name = %s", ("test_name",))
    result = cursor.fetchone()
    
    # Cleanup
    cursor.execute("DROP TABLE test_table")
    cursor.close()
    
    assert result[0] == "test_name"

def test_mongo_connection(mongo_connection):
    """Test MongoDB connection and basic operations."""
    db = mongo_connection.test_gen_db
    collection = db.test_collection
    
    # Insert test document
    test_doc = {"name": "test_name"}
    collection.insert_one(test_doc)
    
    # Query the document
    result = collection.find_one({"name": "test_name"})
    
    # Cleanup
    collection.drop()
    
    assert result["name"] == "test_name"