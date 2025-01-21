import pytest
from http import HTTPStatus
from typing import Dict, Any
from src.app import create_app
from tests.helpers import TestDataGenerator, AuthTestHelper, async_test

class TestCodeAnalysis:
    """Integration tests for code analysis endpoints."""
    
    def test_code_analysis_workflow(self, client, test_db, mock_mongodb):
        """Test the complete code analysis workflow."""
        # Setup
        auth_headers = AuthTestHelper.get_auth_headers()
        test_code = TestDataGenerator.generate_test_code_snippet()
        
        # Submit code for analysis
        response = client.post(
            '/api/analyze',
            json=test_code,
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        analysis_id = response.json['analysis_id']
        
        # Get analysis results
        response = client.get(
            f'/api/analysis/{analysis_id}',
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        assert 'patterns' in response.json
        assert 'suggested_tests' in response.json

class TestPatternLearning:
    """Integration tests for pattern learning system."""
    
    @async_test
    async def test_pattern_storage_workflow(self, client, mock_mongodb):
        """Test storing and retrieving code patterns."""
        # Setup
        auth_headers = AuthTestHelper.get_auth_headers()
        test_pattern = TestDataGenerator.generate_test_pattern()
        
        # Store pattern
        response = client.post(
            '/api/patterns',
            json=test_pattern,
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.CREATED
        pattern_id = response.json['pattern_id']
        
        # Retrieve pattern
        response = client.get(
            f'/api/patterns/{pattern_id}',
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json['pattern_name'] == test_pattern['pattern_name']

class TestTestGeneration:
    """Integration tests for test generation system."""
    
    def test_test_generation_workflow(self, client, test_db):
        """Test the complete test generation workflow."""
        # Setup
        auth_headers = AuthTestHelper.get_auth_headers()
        test_code = TestDataGenerator.generate_test_code_snippet()
        
        # Request test generation
        response = client.post(
            '/api/generate-tests',
            json=test_code,
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        job_id = response.json['job_id']
        
        # Check test generation status
        response = client.get(
            f'/api/test-jobs/{job_id}',
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json['status'] in ['pending', 'completed']

    def test_test_execution_workflow(self, client, test_db):
        """Test the execution of generated tests."""
        # Setup
        auth_headers = AuthTestHelper.get_auth_headers()
        test_code = TestDataGenerator.generate_test_code_snippet()
        
        # Generate and execute tests
        response = client.post(
            '/api/execute-tests',
            json={
                'code': test_code['code'],
                'tests': [
                    'def test_add_numbers():\n    assert add_numbers(1, 2) == 3'
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        assert 'results' in response.json
        assert 'summary' in response.json

class TestErrorHandling:
    """Integration tests for error handling."""
    
    def test_invalid_code_submission(self, client):
        """Test error handling for invalid code submission."""
        auth_headers = AuthTestHelper.get_auth_headers()
        
        response = client.post(
            '/api/analyze',
            json={'code': None},
            headers=auth_headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'error' in response.json
    
    def test_authentication_error(self, client):
        """Test error handling for invalid authentication."""
        response = client.post(
            '/api/analyze',
            json=TestDataGenerator.generate_test_code_snippet()
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'error' in response.json