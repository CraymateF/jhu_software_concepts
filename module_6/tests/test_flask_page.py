"""
Tests for Flask app page rendering and routes.

These tests verify:
- App factory creates testable Flask app with required routes
- GET /analysis returns 200 with correct page structure
- Page contains required buttons and analysis content
"""
import pytest
from bs4 import BeautifulSoup


@pytest.mark.web
def test_app_factory_creates_app():
    """Test that create_app factory creates a testable Flask app."""
    from app import create_app
    
    app = create_app()
    assert app is not None
    assert app.name == 'app'


@pytest.mark.web
def test_app_has_required_routes():
    """Test that app has all required routes configured."""
    from app import create_app
    
    # Create app with mock functions to avoid database dependencies
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
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    # Test each route exists (should not return 404)
    response_index = client.get('/')
    assert response_index.status_code == 200
    
    response_analysis = client.get('/analysis')
    assert response_analysis.status_code == 200
    
    # POST routes should accept POST requests
    response_pull = client.post('/pull-data', json={})
    assert response_pull.status_code in [200, 202, 409]  # Valid responses
    
    response_update = client.post('/update-analysis')
    assert response_update.status_code in [200, 202, 409]  # Valid responses


@pytest.mark.web
def test_analysis_page_returns_200():
    """Test GET /analysis returns status 200."""
    from app import create_app
    
    # Mock query function to return test data
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
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
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    assert response.status_code == 200


@pytest.mark.web
def test_analysis_page_contains_required_buttons():
    """Test that page contains both 'Pull Data' and 'Update Analysis' buttons."""
    from app import create_app
    
    # Mock query function
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
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
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for Pull Data button
    pull_data_btn = soup.find('button', {'data-testid': 'pull-data-btn'})
    assert pull_data_btn is not None, "Pull Data button not found with data-testid='pull-data-btn'"
    assert 'Pull Data' in pull_data_btn.get_text()
    
    # Look for Update Analysis button
    update_analysis_btn = soup.find('button', {'data-testid': 'update-analysis-btn'})
    assert update_analysis_btn is not None, "Update Analysis button not found with data-testid='update-analysis-btn'"
    assert 'Update Analysis' in update_analysis_btn.get_text()


@pytest.mark.web
def test_analysis_page_contains_required_text():
    """Test that page text includes 'Analysis' and at least one 'Answer:' label."""
    from app import create_app
    
    # Mock query function
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
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
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    
    # Check for "Analysis" in page text
    assert 'Analysis' in html, "Page should contain 'Analysis' text"
    
    # Check for at least one "Answer:" label
    assert 'Answer:' in html, "Page should contain at least one 'Answer:' label"
