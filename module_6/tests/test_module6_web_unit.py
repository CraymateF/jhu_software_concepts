"""Focused unit tests for module_6 web app behavior.

These tests target active module_6 microservice routes and status behavior.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


def _query_results(dbname=None):  # pylint: disable=unused-argument
    return {
        'q1': {'question': 'Q1', 'query': 'SELECT 1', 'answer': 1},
        'q2': {'question': 'Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
        'q3': {'question': 'Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
        'q4': {'question': 'Q4', 'query': 'SELECT 4', 'answer': 4.0},
        'q5': {'question': 'Q5', 'query': 'SELECT 5', 'answer': 'Accepted (1 entries)'},
        'q6': {'question': 'Q6', 'query': 'SELECT 6', 'answer': 3.0},
        'q7': {'question': 'Q7', 'query': 'SELECT 7', 'answer': 1},
        'q8': {'question': 'Q8', 'query': 'SELECT 8', 'answer': 1},
        'q9': {'question': 'Q9', 'query': 'SELECT 9', 'answer': 2},
        'q10': {'question': 'Q10', 'query': 'SELECT 10', 'answer': 10},
        'q11': {'question': 'Q11', 'query': 'SELECT 11', 'answer': [['MIT', 4.0, 1]]},
    }


def _make_app(config=None):
    from app import create_app

    return create_app(query_func=_query_results, config=config)


def test_analysis_route_sets_no_cache_and_renders():
    app = _make_app()
    client = app.test_client()

    response = client.get('/analysis')

    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'no-store, no-cache, must-revalidate'
    assert response.headers['Pragma'] == 'no-cache'
    assert b'GradCafe Database Analysis' in response.data


def test_analysis_invalid_db_falls_back_to_default():
    app = _make_app()
    client = app.test_client()

    response = client.get('/analysis?db=does-not-exist')

    assert response.status_code == 200


def test_create_app_accepts_config_override():
    app = _make_app(config={'TESTING': True, 'CUSTOM_FLAG': 'yes'})

    assert app.config['TESTING'] is True
    assert app.config['CUSTOM_FLAG'] == 'yes'


def test_root_route_aliases_analysis():
    app = _make_app()
    client = app.test_client()

    response = client.get('/')

    assert response.status_code == 200


def test_pull_data_json_queues_task():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        response = client.post('/pull-data', json={'dbname': 'gradcafe', 'max_pages': 3})

    assert response.status_code == 202
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['queued'] is True
    mock_publish.assert_called_once_with('scrape_new_data', payload={'dbname': 'gradcafe', 'max_pages': 3})


def test_pull_data_non_json_uses_defaults():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        response = client.post('/pull_data')

    assert response.status_code == 202
    mock_publish.assert_called_once_with('scrape_new_data', payload={'dbname': 'gradcafe', 'max_pages': 2})


def test_pull_data_invalid_dbname_coerced_to_default():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task') as mock_publish:
        mock_publish.return_value = None
        response = client.post('/pull-data', json={'dbname': 'bad-db'})

    assert response.status_code == 202
    mock_publish.assert_called_once_with('scrape_new_data', payload={'dbname': 'gradcafe', 'max_pages': 2})


def test_pull_data_publish_failure_returns_503():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task', side_effect=RuntimeError('mq down')):
        response = client.post('/pull-data', json={})

    assert response.status_code == 503
    payload = response.get_json()
    assert payload['ok'] is False


def test_update_analysis_queues_task():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task') as mock_publish:
        response = client.post('/update-analysis')

    assert response.status_code == 202
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['queued'] is True
    mock_publish.assert_called_once_with('recompute_analytics', payload={})


def test_update_analysis_publish_failure_returns_503():
    app = _make_app()
    client = app.test_client()

    with patch('app.publish_task', side_effect=RuntimeError('mq down')):
        response = client.post('/update-analysis')

    assert response.status_code == 503
    payload = response.get_json()
    assert payload['ok'] is False


def test_scraping_status_is_idle():
    app = _make_app()
    client = app.test_client()

    response = client.get('/scraping_status')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['is_running'] is False
    assert payload['records_added'] == 0


def test_worker_status_success_payload():
    app = _make_app()
    client = app.test_client()

    updated_at = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    scrape_at = datetime(2026, 3, 1, 12, 1, 0, tzinfo=timezone.utc)
    recompute_at = datetime(2026, 3, 1, 12, 2, 0, tzinfo=timezone.utc)

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (123,),
        ('gradcafe_scraped', '2026-02-01', updated_at),
        ('2026-02-01', scrape_at),
        ('2026-03-01', recompute_at),
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('query_data.get_db_connection', return_value=mock_conn):
        response = client.get('/worker_status')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['total_records'] == 123
    assert payload['last_source'] == 'gradcafe_scraped'
    assert payload['seeded'] is True
    assert payload['scrape_last_seen'] == '2026-02-01'
    assert payload['recompute_last_seen'] == '2026-03-01'


def test_worker_status_handles_missing_watermarks():
    app = _make_app()
    client = app.test_client()

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (0,),
        None,
        None,
        None,
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('query_data.get_db_connection', return_value=mock_conn):
        response = client.get('/worker_status')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['seeded'] is False
    assert payload['last_source'] is None
    assert payload['scrape_last_updated'] is None
    assert payload['recompute_last_updated'] is None


def test_worker_status_db_error_returns_ok_false():
    app = _make_app()
    client = app.test_client()

    with patch('query_data.get_db_connection', side_effect=RuntimeError('db down')):
        response = client.get('/worker_status')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['ok'] is False
    assert payload['seeded'] is False
    assert payload['total_records'] == 0
