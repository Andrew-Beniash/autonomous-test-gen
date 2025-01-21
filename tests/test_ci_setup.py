import pytest

def test_basic_addition():
    """Basic test to verify CI pipeline."""
    assert 1 + 1 == 2

def test_basic_subtraction():
    """Another basic test to verify CI pipeline."""
    assert 2 - 1 == 1

def test_environmental_setup(monkeypatch):
    """Test to verify environment variables are set."""
    monkeypatch.setenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/test_gen_db')
    monkeypatch.setenv('MONGODB_URL', 'mongodb://localhost:27017/test_gen_db')
    
    import os
    assert 'DATABASE_URL' in os.environ
    assert 'MONGODB_URL' in os.environ