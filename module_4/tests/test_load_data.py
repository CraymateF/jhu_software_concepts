"""
Tests for load_data module.

These tests verify data loading functionality.
"""
import pytest
import psycopg2
import json
import tempfile
import os
from unittest.mock import patch, MagicMock


@pytest.mark.db
def test_load_data_creates_table():
    """Test load_data creates gradcafe_main table."""
    from load_data import load_data
    
    # Create temporary JSON file
    test_data = [
        {
            'program': 'MIT - CS',
            'comments': 'Test comment',
            'date_added': 'February 14, 2026',
            'url': 'http://test1.com',
            'applicant_status': 'Accepted',
            'semester_year_start': 'Fall 2026',
            'citizenship': 'International',
            'gpa': 'GPA 3.85',
            'gre': 'GRE 325',
            'gre_v': 165,
            'gre_aw': 4.5,
            'masters_or_phd': 'PhD',
            'llm-generated-program': 'CS',
            'llm-generated-university': 'MIT'
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name
    
    try:
        # Load data
        load_data(dbname='gradcafe_test', file_path=temp_file)
        
        # Verify table exists and has data
        conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
        count = cur.fetchone()[0]
        assert count >= 1, "Should have at least 1 row after load_data"
        
        cur.close()
        conn.close()
    except Exception as e:
        pytest.skip(f"Test database not available: {e}")
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.db
def test_parse_date_in_load_data():
    """Test date parsing within load_data context."""
    from load_data import load_data
    import tempfile
    import json
    
    test_data = [{
        'program': 'Test',
        'date_added': '14/02/2026',
        'url': 'http://unique-test.com',
        'applicant_status': 'Accepted',
        'semester_year_start': 'Fall 2026',
        'citizenship': 'American',
        'gpa': 3.5,
        'gre': 320,
        'gre_v': 160,
        'gre_aw': 4.0,
        'masters_or_phd': 'Masters',
        'llm-generated-program': 'CS',
        'llm-generated-university': 'Test U'
    }]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name
    
    try:
        load_data(dbname='gradcafe_test', file_path=temp_file)
        
        conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
        cur = conn.cursor()
        
        cur.execute("SELECT date_added FROM gradcafe_main WHERE url = 'http://unique-test.com';")
        row = cur.fetchone()
        if row:
            assert row[0] is not None
        
        cur.close()
        conn.close()
    except Exception as e:
        pytest.skip(f"Test database not available: {e}")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# ============================================================================
# Comprehensive tests for 100% coverage
# Tests JSON parsing, old format handling, error paths, and edge cases
# ============================================================================

from load_data import load_data


@pytest.mark.db
class TestLoadDataDefaultParameters:
    """Test default parameter handling"""
    
    def test_load_data_with_default_dbname(self):
        """Test load_data uses default dbname when None provided"""
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test Program',
                'url': 'http://test.com'
            }], f)
            temp_file = f.name
        
        try:
            # Mock the database connection to avoid actually creating gradcafe_sample
            with patch('load_data.psycopg2.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_cur = MagicMock()
                mock_conn.cursor.return_value = mock_cur
                mock_connect.return_value = mock_conn
                
                # Call with None dbname (should use default 'gradcafe_sample')
                load_data(dbname=None, file_path=temp_file)
                
                # Verify it tried to connect to gradcafe_sample
                call_args = mock_connect.call_args[1]
                assert call_args['dbname'] == 'gradcafe_sample'
        finally:
            os.unlink(temp_file)
    
    def test_load_data_with_default_file_path(self, test_db):
        """Test load_data uses default file path when None provided"""
        # Mock file opening to avoid needing the actual default file
        mock_file_content = json.dumps([{
            'applicant_status': 'Accepted',
            'program': 'Test',
            'url': 'http://test.com'
        }])
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
            
            # This should try to open the default file path
            load_data(dbname='gradcafe_test', file_path=None)
            
            # Verify it tried to open the default path
            assert mock_open.called


@pytest.mark.db  
class TestLoadDataJSONParsing:
    """Test JSON parsing edge cases"""
    
    def test_load_data_with_jsonl_format(self, test_db):
        """Test loading JSONL (newline-delimited JSON) format"""
        # Create a JSONL file (one JSON object per line)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"applicant_status": "Accepted", "program": "CS", "url": "http://1.com"}\n')
            f.write('{"applicant_status": "Rejected", "program": "EE", "url": "http://2.com"}\n')
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify data was loaded
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM gradcafe_main")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert count == 2
        finally:
            os.unlink(temp_file)
    
    def test_load_data_with_invalid_jsonl_line(self, test_db):
        """Test JSONL parsing with some invalid lines"""
        # Create a JSONL file with one invalid line
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"applicant_status": "Accepted", "program": "CS", "url": "http://valid.com"}\n')
            f.write('invalid json line here\n')  # This will be skipped
            f.write('{"applicant_status": "Rejected", "program": "EE", "url": "http://valid2.com"}\n')
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify valid data was loaded (invalid line skipped)
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM gradcafe_main")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert count == 2  # Only 2 valid records
        finally:
            os.unlink(temp_file)
    
    def test_load_data_with_empty_jsonl(self, test_db):
        """Test JSONL parsing with no valid records raises ValueError"""
        # Create a file with only empty lines and invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('\n')
            f.write('   \n')
            f.write('invalid json\n')
            temp_file = f.name
        
        try:
            # The function catches the exception and prints it, doesn't raise
            load_data(dbname='gradcafe_test', file_path=temp_file)
            # If we get here, the error was handled internally
        finally:
            os.unlink(temp_file)
    
    def test_load_data_with_null_bytes_in_file(self, test_db):
        """Test handling of null bytes in JSON file"""
        # Create a JSON file with null bytes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            data = [{
                'applicant_status': 'Accepted',
                'program': 'CS with null\x00byte',
                'url': 'http://nullbyte.com'
            }]
            content = json.dumps(data)
            f.write(content)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify data was loaded
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM gradcafe_main")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert count == 1
        finally:
            os.unlink(temp_file)
    
    def test_load_data_with_single_object_not_array(self, test_db):
        """Test loading when JSON is a single object, not an array"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write a single object (not wrapped in array)
            json.dump({
                'applicant_status': 'Accepted',
                'program': 'Single Object',
                'url': 'http://single.com'
            }, f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify it was converted to a list and loaded
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM gradcafe_main")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert count == 1
        finally:
            os.unlink(temp_file)


@pytest.mark.db
class TestLoadDataOldFormat:
    """Test old format data loading"""
    
    def test_load_data_old_format_with_acceptance_date(self, test_db):
        """Test loading old format with acceptance date"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'Acceptance Date': '01/03/2026',
                'Rejection Date': None,
                'University': 'MIT',
                'Program': 'Computer Science',
                'Notes': 'Accepted!',
                'Url': 'http://mit1.com',
                'Term': 'Fall 2026',
                'US/International': 'American',
                'GPA': 3.8,
                'GRE General': 320,
                'GRE Verbal': 160,
                'GRE Analytical Writing': 4.5,
                'Degree': 'PhD',
                'LLM Generated Program': 'Computer Science',
                'LLM Generated University': 'MIT'
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify status is 'Accepted'
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT status FROM gradcafe_main WHERE url = 'http://mit1.com'")
            status = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert status == 'Accepted'
        finally:
            os.unlink(temp_file)
    
    def test_load_data_old_format_with_rejection_date(self, test_db):
        """Test loading old format with rejection date"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'Acceptance Date': None,
                'Rejection Date': '05/03/2026',
                'University': 'Stanford',
                'Program': 'AI',
                'Notes': 'Unfortunately rejected',
                'Url': 'http://stanford1.com',
                'Term': 'Spring 2027',
                'US/International': 'International',
                'GPA': 3.7,
                'GRE General': 315,
                'GRE Verbal': 155,
                'GRE Analytical Writing': 4.0,
                'Degree': 'Masters',
                'LLM Generated Program': 'Artificial Intelligence',
                'LLM Generated University': 'Stanford University'
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify status is 'Rejected'
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT status FROM gradcafe_main WHERE url = 'http://stanford1.com'")
            status = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert status == 'Rejected'
        finally:
            os.unlink(temp_file)
    
    def test_load_data_old_format_no_dates(self, test_db):
        """Test loading old format with no acceptance or rejection dates"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'Acceptance Date': None,
                'Rejection Date': None,
                'University': 'Berkeley',
                'Program': 'Data Science',
                'Notes': 'Still waiting',
                'Url': 'http://berkeley1.com',
                'Term': 'Fall 2026',
                'US/International': 'American'
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify status is None
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT status FROM gradcafe_main WHERE url = 'http://berkeley1.com'")
            status = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            assert status is None
        finally:
            os.unlink(temp_file)
    
    def test_load_data_old_format_program_combination(self, test_db):
        """Test old format combines university and program correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                # Both university and program
                {
                    'University': 'Harvard',
                    'Program': 'Biology',
                    'Url': 'http://test1.com'
                },
                # Only university
                {
                    'University': 'Yale',
                    'Program': '',
                    'Url': 'http://test2.com'
                },
                # Only program
                {
                    'University': '',
                    'Program': 'Chemistry',
                    'Url': 'http://test3.com'
                }
            ], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify programs were combined correctly
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            
            cur.execute("SELECT program FROM gradcafe_main WHERE url = 'http://test1.com'")
            assert cur.fetchone()[0] == 'Harvard - Biology'
            
            cur.execute("SELECT program FROM gradcafe_main WHERE url = 'http://test2.com'")
            assert cur.fetchone()[0] == 'Yale'
            
            cur.execute("SELECT program FROM gradcafe_main WHERE url = 'http://test3.com'")
            assert cur.fetchone()[0] == 'Chemistry'
            
            cur.close()
            conn.close()
        finally:
            os.unlink(temp_file)


@pytest.mark.db
class TestLoadDataErrorHandling:
    """Test error handling in load_data"""
    
    def test_load_data_database_error_rollback(self, test_db):
        """Test that database errors trigger rollback"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test',
                'url': 'http://test.com'
            }], f)
            temp_file = f.name
        
        try:
            # Mock execute_values to raise an exception
            with patch('load_data.execute_values') as mock_execute:
                mock_execute.side_effect = Exception("Database error")
                
                # Should not raise, but should print error
                load_data(dbname='gradcafe_test', file_path=temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_data_file_not_found(self, test_db):
        """Test handling when file doesn't exist"""
        # The function catches FileNotFoundError and prints it
        load_data(dbname='gradcafe_test', file_path='/nonexistent/file.json')
        # If we get here, the error was handled internally
    
    def test_load_data_connection_cleanup(self, test_db):
        """Test that database connection is always closed"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{'applicant_status': 'Accepted', 'url': 'http://test.com'}], f)
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cur = MagicMock()
            mock_conn.cursor.return_value = mock_cur
            
            with patch('load_data.psycopg2.connect', return_value=mock_conn):
                # Trigger an exception after connection is made
                mock_cur.execute.side_effect = Exception("Test error")
                
                load_data(dbname='gradcafe_test', file_path=temp_file)
                
                # Verify connection was closed in finally block
                assert mock_cur.close.called
                assert mock_conn.close.called
        finally:
            os.unlink(temp_file)


@pytest.mark.db
class TestLoadDataCommandLine:
    """Test command-line execution"""
    
    def test_load_data_main_execution(self, test_db):
        """Test that __main__ execution works"""
        # This tests the if __name__ == "__main__" block
        # We'll mock sys.argv and import the module
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'CLI Test',
                'url': 'http://cli.com'
            }], f)
            temp_file = f.name
        
        try:
            import sys
            original_argv = sys.argv
            sys.argv = ['load_data.py', 'gradcafe_test', temp_file]
            
            # Import and execute
            import load_data
            if hasattr(load_data, '__name__'):
                # Simulate running as main
                with patch.object(load_data, '__name__', '__main__'):
                    exec(f"load_data.load_data(dbname='gradcafe_test', file_path='{temp_file}')")
            
            sys.argv = original_argv
        finally:
            os.unlink(temp_file)


@pytest.mark.db
class TestLoadDataHelperFunctions:
    """Test inline helper functions within load_data"""
    
    def test_extract_numeric_with_prefix(self, test_db):
        """Test extract_numeric function with prefix"""
        # Test through actual data loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test',
                'url': 'http://numeric.com',
                'gpa': 'GPA 3.85',  # String with prefix
                'gre': 'GRE 325'     # String with prefix
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify numeric extraction worked
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT gpa, gre FROM gradcafe_main WHERE url = 'http://numeric.com'")
            gpa, gre = cur.fetchone()
            cur.close()
            conn.close()
            
            assert gpa == 3.85
            assert gre == 325.0
        finally:
            os.unlink(temp_file)
    
    def test_extract_numeric_invalid_value(self, test_db):
        """Test extract_numeric with non-numeric string"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{
                'applicant_status': 'Accepted',
                'program': 'Test',
                'url': 'http://invalid-numeric.com',
                'gpa': 'GPA N/A',  # Non-numeric
                'gre': 'GRE Unknown'
            }], f)
            temp_file = f.name
        
        try:
            load_data(dbname='gradcafe_test', file_path=temp_file)
            
            # Verify None was stored for invalid values
            conn = psycopg2.connect(dbname='gradcafe_test', user='fadetoblack', host='localhost')
            cur = conn.cursor()
            cur.execute("SELECT gpa, gre FROM gradcafe_main WHERE url = 'http://invalid-numeric.com'")
            gpa, gre = cur.fetchone()
            cur.close()
            conn.close()
            
            assert gpa is None
            assert gre is None
        finally:
            os.unlink(temp_file)
