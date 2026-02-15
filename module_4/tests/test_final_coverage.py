"""
Final tests to achieve 100% coverage
Covers edge cases in helper functions
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import psycopg2
from conftest import get_test_db_params

from data_updater import extract_numeric, add_new_records_to_db
from load_data import load_data


@pytest.mark.db
class TestFinalCoverage:
    """Tests for the final uncovered lines"""
    
    def test_extract_numeric_with_none_type(self):
        """Test extract_numeric with None type (covers line 61 in data_updater.py)"""
        from data_updater import extract_numeric
        # Pass a non-string, non-numeric type (like a list or dict)
        result = extract_numeric([1, 2, 3])
        assert result is None
        
        result = extract_numeric({'key': 'value'})
        assert result is None
    
    def test_add_records_database_rollback(self, test_db):
        """Test that database error triggers rollback (covers line 253 in data_updater.py)"""
        records = [
            {
                'applicant_status': 'Accepted',
                'program': 'Test',
                'url': 'http://rollback-test.com'
            }
        ]
        
        # Mock execute_values to raise an exception after connection is made
        with patch('data_updater.execute_values') as mock_execute:
            mock_execute.side_effect = Exception("Database insert error")
            
            result = add_new_records_to_db(records, dbname='gradcafe_test')
            
            # Should return 0 due to error
            assert result == 0
    
    def test_load_data_parse_date_invalid_format(self, test_db):
        """Test parse_date with invalid date format (covers lines 108-111 in load_data.py)"""
        # Create a JSON file with an invalid date format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test Program',
                'url': 'http://invalid-date.com',
                'date_added': 'Invalid Date Format 2026'  # This will fail both date parsers
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify data was loaded with None for date
            conn = psycopg2.connect(**get_test_db_params())
            cur = conn.cursor()
            cur.execute("SELECT date_added FROM gradcafe_main WHERE url = 'http://invalid-date.com'")
            date_added = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert date_added is None
        finally:
            os.unlink(temp_file)
    
    def test_load_data_extract_numeric_non_convertible_type(self, test_db):
        """Test extract_numeric with non-convertible types (covers line 126 in load_data.py)"""
        # Create data with non-standard types for numeric fields
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test',
                'url': 'http://non-numeric.com',
                'gpa': ['list', 'instead', 'of', 'number'],  # Will use internal extract_numeric
                'gre': {'dict': 'instead of number'}  # Will use internal extract_numeric
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify None was stored for these fields
            conn = psycopg2.connect(**get_test_db_params())
            cur = conn.cursor()
            cur.execute("SELECT gpa, gre FROM gradcafe_main WHERE url = 'http://non-numeric.com'")
            gpa, gre = cur.fetchone()
            cur.close()
            conn.close()
            
            assert gpa is None
            assert gre is None
        finally:
            os.unlink(temp_file)
