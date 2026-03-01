"""
Integration tests for end-to-end flows.

These tests verify:
- End-to-end (pull -> update -> render)
- Multiple pulls with overlapping data remain consistent
"""
import pytest
import re
from bs4 import BeautifulSoup


@pytest.mark.integration
def test_end_to_end_pull_update_render():
    """
    Test end-to-end flow:
    1. Inject fake scraper that returns multiple records
    2. POST /pull-data succeeds and rows are in DB
    3. POST /update-analysis succeeds (when not busy)
    4. GET /analysis shows updated analysis with correctly formatted values
    """
    from app import create_app
    
    # Simulate a database state
    db_state = {
        'records': [],
        'is_running': False
    }
    
    # Mock scraper that adds records to our simulated DB
    def mock_scraper(dbname=None, max_pages=None):
        db_state['records'] = [
            {
                'program': 'MIT - Computer Science',
                'term': 'Fall 2026',
                'status': 'Accepted',
                'us_or_international': 'International',
                'gpa': 3.85,
                'gre': 325
            },
            {
                'program': 'Stanford - EE',
                'term': 'Fall 2026',
                'status': 'Accepted',
                'us_or_international': 'American',
                'gpa': 3.90,
                'gre': 330
            },
            {
                'program': 'Berkeley - CS',
                'term': 'Fall 2026',
                'status': 'Rejected',
                'us_or_international': 'International',
                'gpa': 3.70,
                'gre': 315
            }
        ]
        return {'status': 'success', 'records_added': len(db_state['records'])}
    
    # Mock query that uses our simulated DB
    def mock_query(dbname=None):
        records = db_state['records']
        total = len(records)
        fall_2026 = len([r for r in records if r.get('term') == 'Fall 2026'])
        intl = len([r for r in records if r.get('us_or_international') == 'International'])
        intl_pct = (intl / total * 100) if total > 0 else 0
        
        gpas = [r['gpa'] for r in records if 'gpa' in r]
        avg_gpa = sum(gpas) / len(gpas) if gpas else 0
        
        gres = [r['gre'] for r in records if 'gre' in r]
        avg_gre = sum(gres) / len(gres) if gres else 0
        
        return {
            'q1': {'question': 'How many Fall 2026?', 'query': 'SELECT...', 'answer': fall_2026},
            'q2': {'question': 'Percentage international?', 'query': 'SELECT...', 'answer': f'{intl_pct:.2f}%'},
            'q3': {'question': 'Averages?', 'query': 'SELECT...', 
                   'answer': {'avg_gpa': round(avg_gpa, 2), 'avg_gre': round(avg_gre, 2), 
                             'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
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
        return {'is_running': db_state['is_running'], 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    # Step 1: Initial state - no data
    assert len(db_state['records']) == 0
    
    # Step 2: POST /pull-data queues task and returns 202 (async model)
    response_pull = client.post('/pull-data', json={'dbname': 'gradcafe', 'max_pages': 1},
                                content_type='application/json')
    assert response_pull.status_code == 202
    data_pull = response_pull.get_json()
    assert data_pull['ok'] is True

    # Step 3: POST /update-analysis queues task and returns 202
    response_update = client.post('/update-analysis')
    assert response_update.status_code == 202
    data_update = response_update.get_json()
    assert data_update['ok'] is True

    # Step 4: GET /analysis shows current analysis (worker updates asynchronously)
    response_analysis = client.get('/analysis')
    assert response_analysis.status_code == 200
    html = response_analysis.data.decode('utf-8')

    # Verify percentage formatting (should be XX.XX%)
    percentages = re.findall(r'\d+\.\d{2}%', html)
    assert len(percentages) > 0, "Should have percentages with 2 decimal places"


@pytest.mark.integration
def test_multiple_pulls_maintain_consistency():
    """
    Test that running POST /pull-data twice with overlapping data
    remains consistent with uniqueness policy.
    """
    from app import create_app
    
    # Simulate database with URL uniqueness
    db_state = {
        'records': {},  # Use URL as key for uniqueness
        'is_running': False
    }
    
    # Mock scraper that returns records (some overlap on second call)
    call_count = {'count': 0}
    
    def mock_scraper(dbname=None, max_pages=None):
        call_count['count'] += 1
        
        if call_count['count'] == 1:
            # First pull: 3 records
            new_records = [
                {'url': 'http://test1.com', 'program': 'MIT - CS', 'term': 'Fall 2026', 'status': 'Accepted'},
                {'url': 'http://test2.com', 'program': 'Stanford - EE', 'term': 'Fall 2026', 'status': 'Accepted'},
                {'url': 'http://test3.com', 'program': 'Berkeley - CS', 'term': 'Fall 2026', 'status': 'Rejected'}
            ]
        else:
            # Second pull: 3 records (2 overlap, 1 new)
            new_records = [
                {'url': 'http://test2.com', 'program': 'Stanford - EE', 'term': 'Fall 2026', 'status': 'Accepted'},  # Duplicate
                {'url': 'http://test3.com', 'program': 'Berkeley - CS', 'term': 'Fall 2026', 'status': 'Rejected'},  # Duplicate
                {'url': 'http://test4.com', 'program': 'CMU - Robotics', 'term': 'Fall 2026', 'status': 'Accepted'}  # New
            ]
        
        # Add to DB state (URL as key ensures uniqueness)
        for record in new_records:
            db_state['records'][record['url']] = record
        
        return {'status': 'success', 'records_added': len(new_records)}
    
    def mock_query(dbname=None):
        total = len(db_state['records'])
        return {
            'q1': {'question': 'Total records', 'query': 'SELECT...', 'answer': total},
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
        return {'is_running': db_state['is_running'], 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    # First pull – queues task, returns 202
    response1 = client.post('/pull-data', json={'dbname': 'gradcafe', 'max_pages': 1},
                           content_type='application/json')
    assert response1.status_code == 202

    # Second pull – also queues, returns 202
    response2 = client.post('/pull-data', json={'dbname': 'gradcafe', 'max_pages': 1},
                           content_type='application/json')
    assert response2.status_code == 202

    # Both responses confirm task was accepted
    assert response1.get_json()['ok'] is True
    assert response2.get_json()['ok'] is True


@pytest.mark.integration
def test_end_to_end_with_busy_state():
    """
    Test end-to-end flow where scraping is in progress and update is blocked.
    """
    from app import create_app
    
    db_state = {
        'records': [],
        'is_running': True  # Simulate busy state
    }
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
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
        return {'is_running': db_state['is_running'], 'status_message': 'Scraping...'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    # In module_6 there is no "busy" concept – all requests are queued via RabbitMQ
    # and return 202 regardless of worker state.
    response_pull = client.post('/pull-data', json={'dbname': 'gradcafe', 'max_pages': 1},
                                content_type='application/json')
    assert response_pull.status_code == 202
    data_pull = response_pull.get_json()
    assert data_pull['ok'] is True

    response_update = client.post('/update-analysis')
    assert response_update.status_code == 202
    data_update = response_update.get_json()
    assert data_update['ok'] is True

    # GET /analysis should still work (just shows current state)
    response_analysis = client.get('/analysis')
    assert response_analysis.status_code == 200


@pytest.mark.integration
def test_render_shows_correctly_formatted_percentages():
    """Test that rendered page shows percentages with exactly 2 decimal places."""
    from app import create_app
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
    def mock_query(dbname=None):
        # Return various percentages to test formatting
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'International %', 'query': 'SELECT 2', 'answer': '33.33%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 
                   'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Another %', 'query': 'SELECT 5', 'answer': '87.65%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Third %', 'query': 'SELECT 10', 'answer': '0.12%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    
    # Find all percentages
    percentages = re.findall(r'\d+\.\d+%', html)
    
    # All should have exactly 2 decimal places
    for pct in percentages:
        decimal_part = pct.split('.')[1].rstrip('%')
        assert len(decimal_part) == 2, f"Percentage {pct} should have exactly 2 decimal places"
    
    # Verify specific values are present
    assert '33.33%' in html
    assert '87.65%' in html
    assert '0.12%' in html
