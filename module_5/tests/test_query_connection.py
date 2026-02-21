"""
Test for query_data.py to achieve 100% coverage
Covers the default parameter in get_db_connection
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from query_data import get_db_connection


@pytest.mark.db
class TestQueryDataConnection:
    """Test database connection with default parameters"""
    
    def test_get_db_connection_with_default_dbname(self):
        """Test that get_db_connection uses default dbname when None provided"""
        # Mock DATABASE_URL to control user for testing
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://fadetoblack@localhost/gradcafe_test'}, clear=False):
            with patch('query_data.psycopg2.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                
                # Call with None (should use default 'gradcafe_sample')
                conn = get_db_connection(dbname=None)
                
                # Verify it tried to connect with default dbname
                call_kwargs = mock_connect.call_args[1]
                assert call_kwargs['dbname'] == 'gradcafe_sample'
                assert call_kwargs['user'] == 'fadetoblack'
                assert call_kwargs['host'] == 'localhost'
