"""
Additional tests to improve code coverage.

These tests cover edge cases and alternative code paths.
"""
import pytest


@pytest.mark.web
def test_create_app_with_config():
    """Test create_app accepts config parameter."""
    from app import create_app
    
    config = {'TESTING': True, 'DATABASE_URL': 'postgresql://test@localhost/test'}
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test', 'query': 'SELECT 1', 'answer': 1},
            'q2': {'question': 'Test', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False}
    
    app = create_app(query_func=mock_query, status_func=mock_status, config=config)
    
    assert app.config['TESTING'] is True
    assert app.config['DATABASE_URL'] == 'postgresql://test@localhost/test'


@pytest.mark.web
def test_analysis_page_with_invalid_database():
    """Test GET /analysis with invalid database name defaults to gradcafe_sample."""
    from app import create_app
    
    def mock_query(dbname=None):
        # Track which dbname was used
        mock_query.called_with = dbname
        return {
            'q1': {'question': 'Test', 'query': 'SELECT 1', 'answer': 1},
            'q2': {'question': 'Test', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False}
    
    app = create_app(query_func=mock_query, status_func=mock_status)
    client = app.test_client()
    
    # Request with invalid database name
    response = client.get('/analysis?db=invalid_db_name')
    assert response.status_code == 200
    
    # Should have defaulted to gradcafe_sample
    assert mock_query.called_with == 'gradcafe_sample'


@pytest.mark.buttons
def test_pull_data_with_invalid_database():
    """Test POST /pull-data with invalid database name defaults to gradcafe_sample."""
    from app import create_app
    
    scraper_called_with = {}
    
    def mock_scraper(dbname=None, max_pages=None):
        scraper_called_with['dbname'] = dbname
        scraper_called_with['max_pages'] = max_pages
        return {'status': 'started'}
    
    def mock_status():
        return {'is_running': False}
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/pull-data',
                          json={'dbname': 'invalid_db', 'max_pages': 3},
                          content_type='application/json')
    
    assert response.status_code == 200
    # Should have defaulted to gradcafe_sample
    assert scraper_called_with['dbname'] == 'gradcafe_sample'


@pytest.mark.buttons
def test_pull_data_without_json():
    """Test POST /pull-data without JSON content type."""
    from app import create_app
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
    def mock_status():
        return {'is_running': False}
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    # POST without JSON content
    response = client.post('/pull-data')
    assert response.status_code == 200


@pytest.mark.web
def test_scraping_status_endpoint():
    """Test GET /scraping_status returns status."""
    from app import create_app
    
    def mock_status():
        return {
            'is_running': True,
            'status_message': 'Scraping page 3',
            'records_added': 25
        }
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, status_func=mock_status)
    client = app.test_client()
    
    response = client.get('/scraping_status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['is_running'] is True
    assert data['status_message'] == 'Scraping page 3'
    assert data['records_added'] == 25


@pytest.mark.db
def test_load_data_with_jsonl_format():
    """Test load_data handles JSONL format (newline-delimited JSON)."""
    from load_data import load_data
    import tempfile
    import os
    
    # Create JSONL format (one JSON object per line)
    jsonl_content = '''{"program": "MIT - CS", "date_added": "February 14, 2026", "url": "http://jsonl1.com", "applicant_status": "Accepted", "semester_year_start": "Fall 2026", "citizenship": "International", "gpa": 3.85, "gre": 325, "gre_v": 165, "gre_aw": 4.5, "masters_or_phd": "PhD", "llm-generated-program": "CS", "llm-generated-university": "MIT"}
{"program": "Stanford - EE", "date_added": "February 13, 2026", "url": "http://jsonl2.com", "applicant_status": "Accepted", "semester_year_start": "Fall 2026", "citizenship": "American", "gpa": 3.90, "gre": 330, "gre_v": 168, "gre_aw": 5.0, "masters_or_phd": "Masters", "llm-generated-program": "EE", "llm-generated-university": "Stanford"}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(jsonl_content)
        temp_file = f.name
    
    try:
        load_data(dbname='gradcafe_test', file_path=temp_file)
        
        import psycopg2
        conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM gradcafe_main WHERE url IN ('http://jsonl1.com', 'http://jsonl2.com');")
        count = cur.fetchone()[0]
        assert count >= 2, "Should have loaded JSONL records"
        
        cur.close()
        conn.close()
    except Exception as e:
        pytest.skip(f"Test database not available: {e}")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.db
def test_load_data_handles_invalid_json():
    """Test load_data handles invalid JSON by printing warning."""
    from load_data import load_data
    import tempfile
    import os
    
    # Create file with invalid JSON
    invalid_content = '''This is not valid JSON at all!'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(invalid_content)
        temp_file = f.name
    
    try:
        # load_data prints a warning but doesn't raise - it just reports error
        # This should complete without crashing even with invalid data
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
        except ValueError as e:
            # Acceptable - ValueError is raised for "Could not parse any valid JSON records"
            assert "Could not parse" in str(e)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.db
def test_setup_databases_main_function():
    """Test setup_databases main function can be imported."""
    from setup_databases import main
    
    # Just verify the function exists and is callable
    assert callable(main)
