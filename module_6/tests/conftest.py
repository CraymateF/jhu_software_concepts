"""
Pytest configuration and shared fixtures for Module 6 tests.

Module 6 uses RabbitMQ for async task publishing.
Button endpoints return HTTP 202 (Accepted) instead of synchronous 200.
"""
import os
import sys
from unittest.mock import patch

import pytest

# Prevent collection of legacy carried-over tests that target removed
# module_4/module_5 behavior rather than module_6 web microservice logic.
collect_ignore = [
    "test_analysis_format.py",
    "test_buttons.py",
    "test_coverage_100_branches.py",
    "test_coverage_improvements.py",
    "test_data_updater.py",
    "test_db_helpers.py",
    "test_db_insert.py",
    "test_final_coverage.py",
    "test_flask_page.py",
    "test_integration_end_to_end.py",
    "test_load_data.py",
    "test_query_connection.py",
    "test_query_functions.py",
    "test_setup_databases.py",
]

# Add src/web/ to Python path so tests can import Flask app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'web'))
# Add src/db/ to Python path for optional imports in tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'db'))


@pytest.fixture(autouse=True)
def _patch_publisher():
    """Auto-patch publisher.publish_task for all tests to prevent RabbitMQ connections."""
    with patch('app.publish_task'):
        yield


def _make_mock_results():
    return {
        'q1':  {'question': 'Test Q1',  'query': 'SELECT 1',  'answer': 100},
        'q2':  {'question': 'Test Q2',  'query': 'SELECT 2',  'answer': '50.00%'},
        'q3':  {'question': 'Test Q3',  'query': 'SELECT 3',
                'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
        'q4':  {'question': 'Test Q4',  'query': 'SELECT 4',  'answer': 3.7},
        'q5':  {'question': 'Test Q5',  'query': 'SELECT 5',  'answer': 'Rejected (50 entries)'},
        'q6':  {'question': 'Test Q6',  'query': 'SELECT 6',  'answer': 3.6},
        'q7':  {'question': 'Test Q7',  'query': 'SELECT 7',  'answer': 200},
        'q8':  {'question': 'Test Q8',  'query': 'SELECT 8',  'answer': 50},
        'q9':  {'question': 'Test Q9',  'query': 'SELECT 9',  'answer': 48},
        'q10': {'question': 'Test Q10', 'query': 'SELECT 10', 'answer': 1000},
        'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]},
    }


@pytest.fixture
def app():
    """Create a test Flask app instance with mocked query function and publisher."""
    from app import create_app

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        flask_app = create_app(query_func=_make_mock_results)
        flask_app.config['TESTING'] = True
        yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()
