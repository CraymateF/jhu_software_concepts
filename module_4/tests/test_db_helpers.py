"""
Tests for database helper functions.

These tests verify that the get_db_params functions correctly parse
various DATABASE_URL formats.
"""
import pytest
import os
from unittest.mock import patch


@pytest.mark.db
def test_data_updater_get_db_params_no_password():
    """Test get_db_params with DATABASE_URL without password."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from data_updater import get_db_params
    
    # Test with user@host/db format (no password)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost/testdb'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'testuser'
        assert params['host'] == 'testhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_data_updater_get_db_params_no_at_sign():
    """Test get_db_params with DATABASE_URL without @ sign."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from data_updater import get_db_params
    
    # Test with plain format (no @ sign)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://justtext'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'fadetoblack'
        assert params['host'] == 'localhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_data_updater_get_db_params_no_slash():
    """Test get_db_params with DATABASE_URL without slash in host_part."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from data_updater import get_db_params
    
    # Test with user@host format (no database in URL)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'testuser'
        assert params['host'] == 'testhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_load_data_get_db_params_no_password():
    """Test load_data get_db_params with DATABASE_URL without password."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from load_data import get_db_params
    
    # Test with user@host/db format (no password)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost/testdb'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'testuser'
        assert params['host'] == 'testhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_load_data_get_db_params_no_at_sign():
    """Test load_data get_db_params with DATABASE_URL without @ sign."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from load_data import get_db_params
    
    # Test with plain format (no @ sign)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://justtext'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'fadetoblack'
        assert params['host'] == 'localhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_load_data_get_db_params_no_slash():
    """Test load_data get_db_params with DATABASE_URL without slash in host_part."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from load_data import get_db_params
    
    # Test with user@host format (no database in URL)
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost'}):
        params = get_db_params('gradcafe')
        assert params['user'] == 'testuser'
        assert params['host'] == 'testhost'
        assert params['dbname'] == 'gradcafe'
        assert 'password' not in params


@pytest.mark.db
def test_query_data_get_db_connection_no_password():
    """Test get_db_connection with DATABASE_URL without password."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from unittest.mock import MagicMock
    import psycopg2
    
    # Mock psycopg2.connect to avoid actual connection
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = MagicMock()
        from query_data import get_db_connection
        
        # Test with user@host/db format (no password)
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost/testdb'}):
            conn = get_db_connection('gradcafe')
            # Verify connect was called with correct params
            call_args = mock_connect.call_args[1]
            assert call_args['user'] == 'testuser'
            assert call_args['host'] == 'testhost'
            assert call_args['dbname'] == 'gradcafe'
            assert 'password' not in call_args


@pytest.mark.db
def test_query_data_get_db_connection_no_at_sign():
    """Test get_db_connection with DATABASE_URL without @ sign."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from unittest.mock import MagicMock
    
    # Mock psycopg2.connect to avoid actual connection
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = MagicMock()
        from query_data import get_db_connection
        
        # Test with plain format (no @ sign)
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://justtext'}):
            conn = get_db_connection('gradcafe')
            # Verify connect was called with correct params
            call_args = mock_connect.call_args[1]
            assert call_args['user'] == 'fadetoblack'
            assert call_args['host'] == 'localhost'
            assert call_args['dbname'] == 'gradcafe'
            assert 'password' not in call_args


@pytest.mark.db
def test_query_data_get_db_connection_no_slash():
    """Test get_db_connection with DATABASE_URL without slash in host_part."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from unittest.mock import MagicMock
    
    # Mock psycopg2.connect to avoid actual connection
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = MagicMock()
        from query_data import get_db_connection
        
        # Test with user@host format (no database in URL)
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://testuser@testhost'}):
            conn = get_db_connection('gradcafe')
            # Verify connect was called with correct params
            call_args = mock_connect.call_args[1]
            assert call_args['user'] == 'testuser'
            assert call_args['host'] == 'testhost'
            assert call_args['dbname'] == 'gradcafe'
            assert 'password' not in call_args
