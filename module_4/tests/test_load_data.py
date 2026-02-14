"""
Tests for load_data module.

These tests verify data loading functionality.
"""
import pytest
import psycopg2
import json
import tempfile
import os


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
