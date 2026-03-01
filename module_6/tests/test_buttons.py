"""
Tests for button endpoints.

Module 6 changes: buttons now publish tasks to RabbitMQ and return HTTP 202.
No synchronous scraping / busy-state 409s.
"""
import pytest
import json
from unittest.mock import patch


@pytest.mark.buttons
def test_pull_data_returns_202():
    """Test POST /pull-data returns 202 (task queued) with ok: true."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        app = create_app(query_func=mock_query)
        client = app.test_client()

        response = client.post(
            '/pull-data',
            json={'dbname': 'gradcafe', 'max_pages': 2},
            content_type='application/json',
        )

    assert response.status_code == 202
    data = json.loads(response.data)
    assert data['ok'] is True
    assert data.get('queued') is True


@pytest.mark.buttons
def test_pull_data_publishes_task():
    """Test POST /pull-data calls publish_task with the correct kind."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        app = create_app(query_func=mock_query)
        client = app.test_client()

        client.post(
            '/pull-data',
            json={'dbname': 'gradcafe', 'max_pages': 2},
            content_type='application/json',
        )
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == 'scrape_new_data'


@pytest.mark.buttons
def test_update_analysis_returns_202():
    """Test POST /update-analysis returns 202 (task queued) with ok: true."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        app = create_app(query_func=mock_query)
        client = app.test_client()

        response = client.post('/update-analysis')

    assert response.status_code == 202
    data = json.loads(response.data)
    assert data['ok'] is True
    assert data.get('queued') is True


@pytest.mark.buttons
def test_update_analysis_publishes_recompute_task():
    """Test POST /update-analysis calls publish_task with recompute_analytics kind."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        app = create_app(query_func=mock_query)
        client = app.test_client()
        client.post('/update-analysis')
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == 'recompute_analytics'


@pytest.mark.buttons
def test_pull_data_supports_both_url_forms():
    """Test that /pull-data and /pull_data both return 202."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        app = create_app(query_func=mock_query)
        client = app.test_client()

        r1 = client.post('/pull-data', json={'dbname': 'gradcafe'}, content_type='application/json')
        r2 = client.post('/pull_data', json={'dbname': 'gradcafe'}, content_type='application/json')

    assert r1.status_code == 202
    assert r2.status_code == 202


@pytest.mark.buttons
def test_publisher_error_returns_503():
    """Test that a RabbitMQ failure on publish returns HTTP 503."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task', side_effect=RuntimeError('RabbitMQ down')):
        app = create_app(query_func=mock_query)
        client = app.test_client()
        response = client.post('/pull-data', json={}, content_type='application/json')

    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['ok'] is False


@pytest.mark.buttons
def test_scraping_status_always_ready():
    """GET /scraping_status returns idle status (worker handles the state)."""
    from app import create_app

    def mock_query(dbname=None):
        return {}

    with patch('app.publish_task'):
        app = create_app(query_func=mock_query)
        client = app.test_client()
        response = client.get('/scraping_status')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['is_running'] is False

