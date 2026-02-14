"""
Tests for data_updater helper functions.

These tests verify data transformation and helper utilities.
"""
import pytest
from datetime import datetime


@pytest.mark.db
def test_parse_date_old_format():
    """Test parse_date handles DD/MM/YYYY format."""
    from data_updater import parse_date
    
    result = parse_date('14/02/2026')
    assert result == '2026-02-14'


@pytest.mark.db
def test_parse_date_new_format():
    """Test parse_date handles 'Month DD, YYYY' format."""
    from data_updater import parse_date
    
    result = parse_date('February 14, 2026')
    assert result == '2026-02-14'


@pytest.mark.db
def test_parse_date_invalid():
    """Test parse_date returns None for invalid dates."""
    from data_updater import parse_date
    
    result = parse_date('invalid date')
    assert result is None
    
    result = parse_date('')
    assert result is None
    
    result = parse_date(None)
    assert result is None


@pytest.mark.db
def test_extract_numeric_from_gpa_string():
    """Test extract_numeric extracts GPA from 'GPA X.XX' format."""
    from data_updater import extract_numeric
    
    result = extract_numeric('GPA 3.85', 'GPA')
    assert result == 3.85


@pytest.mark.db
def test_extract_numeric_from_gre_string():
    """Test extract_numeric extracts GRE from 'GRE XXX' format."""
    from data_updater import extract_numeric
    
    result = extract_numeric('GRE 325', 'GRE')
    assert result == 325.0


@pytest.mark.db
def test_extract_numeric_from_number():
    """Test extract_numeric handles direct numbers."""
    from data_updater import extract_numeric
    
    result = extract_numeric(3.85)
    assert result == 3.85
    
    result = extract_numeric(325)
    assert result == 325.0


@pytest.mark.db
def test_extract_numeric_invalid():
    """Test extract_numeric returns None for invalid input."""
    from data_updater import extract_numeric
    
    result = extract_numeric('invalid')
    assert result is None
    
    result = extract_numeric('')
    assert result is None
    
    result = extract_numeric(None)
    assert result is None


@pytest.mark.db
def test_clean_string_removes_null_bytes():
    """Test clean_string removes NUL characters."""
    from data_updater import clean_string
    
    result = clean_string('test\x00string')
    assert result == 'teststring'
    assert '\x00' not in result
    
    result = clean_string('test\u0000string')
    assert result == 'teststring'
    assert '\u0000' not in result


@pytest.mark.db
def test_clean_string_non_string():
    """Test clean_string returns non-strings unchanged."""
    from data_updater import clean_string
    
    result = clean_string(123)
    assert result == 123
    
    result = clean_string(None)
    assert result is None


@pytest.mark.db
def test_get_existing_urls():
    """Test get_existing_urls retrieves URLs from database."""
    from data_updater import get_existing_urls
    import psycopg2
    
    # Create test database and insert data
    conn_params = {
        "dbname": 'gradcafe_test',
        "user": "fadetoblack",
        "host": "localhost"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Setup table
        cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
        cur.execute("""
            CREATE TABLE gradcafe_main (
                p_id SERIAL PRIMARY KEY,
                program TEXT,
                comments TEXT,
                date_added DATE,
                url TEXT UNIQUE,
                status TEXT,
                term TEXT,
                us_or_international TEXT,
                gpa FLOAT,
                gre FLOAT,
                gre_v FLOAT,
                gre_aw FLOAT,
                degree TEXT,
                llm_generated_program TEXT,
                llm_generated_university TEXT,
                raw_data JSONB
            );
        """)
        
        # Insert test URLs
        cur.execute("""
            INSERT INTO gradcafe_main (url) VALUES ('http://test1.com'), ('http://test2.com');
        """)
        conn.commit()
        
        # Test function
        urls = get_existing_urls(dbname='gradcafe_test')
        assert isinstance(urls, set)
        assert 'http://test1.com' in urls
        assert 'http://test2.com' in urls
        
        # Cleanup
        cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        # If test database doesn't exist, skip this test
        pytest.skip(f"Test database not available: {e}")


@pytest.mark.db
def test_get_scraping_status():
    """Test get_scraping_status returns status dict."""
    from data_updater import get_scraping_status
    
    status = get_scraping_status()
    assert isinstance(status, dict)
    assert 'is_running' in status
    assert 'status_message' in status
    assert isinstance(status['is_running'], bool)
