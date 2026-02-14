"""
Pytest configuration and shared fixtures for Module 4 tests.
"""
import pytest
import sys
import os

# Add module_4/src to Python path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def app():
    """Create a test Flask app instance."""
    from app import create_app
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 
                   'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test Q5', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test Q10', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query, status_func=mock_status)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()
