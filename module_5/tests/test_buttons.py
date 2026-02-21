"""
Tests for button endpoints and busy-state behavior.

These tests verify:
- POST /pull-data returns 200 and triggers the loader
- POST /update-analysis returns 200 when not busy
- Busy gating: when pull is in progress, update returns 409
- Busy gating: when busy, pull-data returns 409
"""
import pytest
import json


@pytest.mark.buttons
def test_pull_data_returns_200():
    """Test POST /pull-data returns 200 with ok: true."""
    from app import create_app
    
    # Mock scraper that returns success
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started', 'message': 'Scraping initiated'}
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/pull-data', 
                          json={'dbname': 'gradcafe_sample', 'max_pages': 2},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['ok'] is True


@pytest.mark.buttons
def test_pull_data_triggers_loader():
    """Test POST /pull-data triggers the loader with fake/mocked scraper."""
    from app import create_app
    
    # Track if scraper was called
    scraper_called = {'called': False, 'dbname': None, 'max_pages': None}
    
    def mock_scraper(dbname=None, max_pages=None):
        scraper_called['called'] = True
        scraper_called['dbname'] = dbname
        scraper_called['max_pages'] = max_pages
        return {'status': 'started', 'message': 'Scraping initiated'}
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/pull-data',
                          json={'dbname': 'gradcafe_sample', 'max_pages': 3},
                          content_type='application/json')
    
    assert response.status_code == 200
    assert scraper_called['called'] is True
    assert scraper_called['dbname'] == 'gradcafe_sample'
    assert scraper_called['max_pages'] == 3


@pytest.mark.buttons
def test_update_analysis_returns_200_when_not_busy():
    """Test POST /update-analysis returns 200 when not busy."""
    from app import create_app
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    def mock_query(dbname=None):
        return {}
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/update-analysis')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['ok'] is True


@pytest.mark.buttons
def test_update_analysis_returns_409_when_busy():
    """Test POST /update-analysis returns 409 when pull is in progress."""
    from app import create_app
    
    # Mock status showing scraping is running
    def mock_status():
        return {'is_running': True, 'status_message': 'Scraping in progress'}
    
    def mock_query(dbname=None):
        return {}
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/update-analysis')
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['busy'] is True


@pytest.mark.buttons
def test_update_analysis_performs_no_update_when_busy():
    """Test POST /update-analysis performs no update when busy."""
    from app import create_app
    
    # Track if query was called
    query_called = {'called': False}
    
    def mock_query(dbname=None):
        query_called['called'] = True
        return {}
    
    def mock_status():
        return {'is_running': True, 'status_message': 'Scraping in progress'}
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started'}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    # Call update-analysis while busy
    response = client.post('/update-analysis')
    assert response.status_code == 409
    
    # Query should not have been called for the POST endpoint
    # (it's only called when rendering the page via GET)
    assert query_called['called'] is False


@pytest.mark.buttons
def test_pull_data_returns_409_when_busy():
    """Test POST /pull-data returns 409 when already scraping."""
    from app import create_app
    
    # Mock status showing scraping is already running
    def mock_status():
        return {'is_running': True, 'status_message': 'Scraping in progress'}
    
    def mock_query(dbname=None):
        return {}
    
    scraper_called = {'called': False}
    
    def mock_scraper(dbname=None, max_pages=None):
        scraper_called['called'] = True
        return {'status': 'started'}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    response = client.post('/pull-data',
                          json={'dbname': 'gradcafe_sample', 'max_pages': 2},
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['busy'] is True
    assert scraper_called['called'] is False  # Should not call scraper when busy


@pytest.mark.buttons
def test_both_endpoints_support_alternative_paths():
    """Test that both /pull-data and /pull_data routes work (same for update)."""
    from app import create_app
    
    def mock_scraper(dbname=None, max_pages=None):
        return {'status': 'started', 'message': 'Scraping initiated'}
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    def mock_query(dbname=None):
        return {}
    
    app = create_app(query_func=mock_query, scraper_func=mock_scraper, status_func=mock_status)
    client = app.test_client()
    
    # Test /pull-data (hyphenated)
    response1 = client.post('/pull-data', json={'dbname': 'gradcafe_sample'}, content_type='application/json')
    assert response1.status_code == 200
    
    # Test /pull_data (underscore)
    response2 = client.post('/pull_data', json={'dbname': 'gradcafe_sample'}, content_type='application/json')
    assert response2.status_code == 200
