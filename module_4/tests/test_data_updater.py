"""
Tests for data_updater helper functions.

These tests verify data transformation and helper utilities.
"""
import pytest
from datetime import datetime
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time
from conftest import get_test_db_params


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
    
    # Get database connection parameters
    conn_params = get_test_db_params()
    
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


# ============================================================================
# Comprehensive tests for 100% coverage
# Tests old format handling, scraping workflows, and error paths
# ============================================================================

# Import additional functions for comprehensive testing
from data_updater import (
    add_new_records_to_db,
    scrape_and_update_background,
    start_scraping,
    scraping_status
)


@pytest.mark.db
class TestDataUpdaterOldFormat:
    """Test old format data processing"""
    
    def test_add_records_old_format_with_acceptance_date(self, test_db):
        """Test processing old format records with acceptance date"""
        old_format_records = [
            {
                'Acceptance Date': '28/01/2026',
                'Rejection Date': None,
                'University': 'MIT',
                'Program': 'Computer Science',
                'Notes': 'Great program!',
                'Url': 'https://example.com/mit1',
                'Term': 'Fall 2026',
                'US/International': 'American',
                'GPA': 3.8,
                'GRE General': 320,
                'GRE Verbal': 160,
                'GRE Analytical Writing': 4.5,
                'Degree': 'PhD',
                'LLM Generated Program': 'Computer Science',
                'LLM Generated University': 'MIT'
            }
        ]
        
        count = add_new_records_to_db(old_format_records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_old_format_with_rejection_date(self, test_db):
        """Test processing old format records with rejection date"""
        old_format_records = [
            {
                'Acceptance Date': None,
                'Rejection Date': '15/01/2026',
                'University': 'Stanford',
                'Program': 'Electrical Engineering',
                'Notes': 'Tough competition',
                'Url': 'https://example.com/stanford1',
                'Term': 'Spring 2026',
                'US/International': 'International',
                'GPA': 3.7,
                'GRE General': 315,
                'GRE Verbal': 155,
                'GRE Analytical Writing': 4.0,
                'Degree': 'Masters',
                'LLM Generated Program': 'Electrical Engineering',
                'LLM Generated University': 'Stanford University'
            }
        ]
        
        count = add_new_records_to_db(old_format_records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_old_format_no_dates(self, test_db):
        """Test processing old format records with no acceptance/rejection dates"""
        old_format_records = [
            {
                'Acceptance Date': None,
                'Rejection Date': None,
                'University': 'Berkeley',
                'Program': 'Bioinformatics',
                'Notes': 'Waiting to hear',
                'Url': 'https://example.com/berkeley1',
                'Term': 'Fall 2026',
                'US/International': 'American',
                'GPA': 3.9,
                'GRE General': 325,
                'GRE Verbal': 165,
                'GRE Analytical Writing': 5.0,
                'Degree': 'PhD',
                'LLM Generated Program': 'Bioinformatics',
                'LLM Generated University': 'UC Berkeley'
            }
        ]
        
        count = add_new_records_to_db(old_format_records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_old_format_only_university(self, test_db):
        """Test old format with only university (no program name)"""
        old_format_records = [
            {
                'Acceptance Date': '10/02/2026',
                'University': 'Harvard',
                'Program': '',  # Empty program
                'Url': 'https://example.com/harvard1'
            }
        ]
        
        count = add_new_records_to_db(old_format_records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_old_format_only_program(self, test_db):
        """Test old format with only program (no university)"""
        old_format_records = [
            {
                'Acceptance Date': '10/02/2026',
                'University': '',  # Empty university
                'Program': 'Data Science',
                'Url': 'https://example.com/ds1'
            }
        ]
        
        count = add_new_records_to_db(old_format_records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_empty_list(self, test_db):
        """Test adding empty list of records returns 0"""
        count = add_new_records_to_db([], dbname='gradcafe_test')
        assert count == 0
    
    def test_add_records_database_error(self, test_db):
        """Test handling database errors during insert"""
        # Use invalid database name to trigger error
        records = [{'University': 'Test', 'Url': 'http://test.com'}]
        count = add_new_records_to_db(records, dbname='nonexistent_db')
        assert count == 0


@pytest.mark.db
class TestScrapingWorkflow:
    """Test the scraping and background update workflow"""
    
    def test_get_existing_urls_success(self, test_db):
        """Test retrieving existing URLs from database"""
        # First add some records
        records = [
            {'applicant_status': 'Accepted', 'url': 'http://test1.com', 'program': 'CS'},
            {'applicant_status': 'Rejected', 'url': 'http://test2.com', 'program': 'EE'}
        ]
        add_new_records_to_db(records, dbname='gradcafe_test')
        
        # Now get existing URLs
        from data_updater import get_existing_urls
        urls = get_existing_urls(dbname='gradcafe_test')
        assert 'http://test1.com' in urls
        assert 'http://test2.com' in urls
    
    def test_get_existing_urls_database_error(self):
        """Test error handling when database doesn't exist"""
        from data_updater import get_existing_urls
        urls = get_existing_urls(dbname='nonexistent_database')
        assert urls == set()
    
    @patch('data_updater.GradCafeScraper')
    @patch('data_updater.GradCafeDataCleaner')
    @patch('data_updater.apply_llm_standardization')
    @patch('data_updater.get_existing_urls')
    @patch('data_updater.add_new_records_to_db')
    def test_scrape_and_update_background_success(
        self, mock_add_records, mock_get_urls, mock_llm, 
        mock_cleaner_class, mock_scraper_class, test_db
    ):
        """Test successful background scraping workflow"""
        # Setup mocks
        mock_scraper = MagicMock()
        mock_scraper.scrape_data.return_value = [
            {'University': 'MIT', 'Program': 'CS', 'Url': 'http://new1.com'}
        ]
        mock_scraper_class.return_value = mock_scraper
        
        mock_cleaner = MagicMock()
        mock_cleaner.clean_data.return_value = [
            {'University': 'MIT', 'Program': 'CS', 'Url': 'http://new1.com'}
        ]
        mock_cleaner_class.return_value = mock_cleaner
        
        mock_llm.return_value = True
        mock_get_urls.return_value = set()  # No existing URLs
        mock_add_records.return_value = 1
        
        # Create temporary extended file for the function to read
        with tempfile.TemporaryDirectory() as tmpdir:
            extended_file = os.path.join(tmpdir, 'temp_extended_data.json')
            with patch('data_updater.os.path.dirname', return_value=tmpdir):
                with open(extended_file, 'w') as f:
                    json.dump([{'University': 'MIT', 'Program': 'CS', 'Url': 'http://new1.com'}], f)
                
                scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        # Verify workflow completed
        assert scraping_status["records_added"] == 1
        assert scraping_status["is_running"] == False
    
    @patch('data_updater.GradCafeScraper')
    def test_scrape_and_update_background_no_data_from_scraper(
        self, mock_scraper_class, test_db
    ):
        """Test handling when scraper returns no data"""
        mock_scraper = MagicMock()
        mock_scraper.scrape_data.return_value = []
        mock_scraper_class.return_value = mock_scraper
        
        scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        assert scraping_status["status_message"] == "No data found from scraper"
        assert scraping_status["is_running"] == False
    
    @patch('data_updater.GradCafeScraper')
    @patch('data_updater.GradCafeDataCleaner')
    def test_scrape_and_update_background_no_data_after_cleaning(
        self, mock_cleaner_class, mock_scraper_class, test_db
    ):
        """Test handling when cleaner returns no data"""
        mock_scraper = MagicMock()
        mock_scraper.scrape_data.return_value = [{'test': 'data'}]
        mock_scraper_class.return_value = mock_scraper
        
        mock_cleaner = MagicMock()
        mock_cleaner.clean_data.return_value = []
        mock_cleaner_class.return_value = mock_cleaner
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('data_updater.os.path.dirname', return_value=tmpdir):
                scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        assert scraping_status["status_message"] == "No data after cleaning"
        assert scraping_status["is_running"] == False
    
    @patch('data_updater.GradCafeScraper')
    @patch('data_updater.GradCafeDataCleaner')
    @patch('data_updater.apply_llm_standardization')
    def test_scrape_and_update_background_llm_fails(
        self, mock_llm, mock_cleaner_class, mock_scraper_class, test_db
    ):
        """Test handling when LLM standardization fails"""
        mock_scraper = MagicMock()
        mock_scraper.scrape_data.return_value = [{'Url': 'http://test.com'}]
        mock_scraper_class.return_value = mock_scraper
        
        cleaned_data = [{'Url': 'http://test.com', 'University': 'MIT'}]
        mock_cleaner = MagicMock()
        mock_cleaner.clean_data.return_value = cleaned_data
        mock_cleaner_class.return_value = mock_cleaner
        
        mock_llm.return_value = False  # LLM fails
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('data_updater.os.path.dirname', return_value=tmpdir):
                with patch('data_updater.get_existing_urls', return_value=set()):
                    with patch('data_updater.add_new_records_to_db', return_value=1):
                        scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        assert "Successfully added" in scraping_status["status_message"]
    
    @patch('data_updater.GradCafeScraper')
    @patch('data_updater.GradCafeDataCleaner')
    @patch('data_updater.apply_llm_standardization')
    @patch('data_updater.get_existing_urls')
    def test_scrape_and_update_background_no_new_records(
        self, mock_get_urls, mock_llm, mock_cleaner_class, 
        mock_scraper_class, test_db
    ):
        """Test when all scraped URLs already exist in database"""
        mock_scraper = MagicMock()
        mock_scraper.scrape_data.return_value = [{'Url': 'http://existing.com'}]
        mock_scraper_class.return_value = mock_scraper
        
        mock_cleaner = MagicMock()
        mock_cleaner.clean_data.return_value = [{'Url': 'http://existing.com'}]
        mock_cleaner_class.return_value = mock_cleaner
        
        mock_llm.return_value = True
        mock_get_urls.return_value = {'http://existing.com'}  # URL already exists
        
        with tempfile.TemporaryDirectory() as tmpdir:
            extended_file = os.path.join(tmpdir, 'temp_extended_data.json')
            with patch('data_updater.os.path.dirname', return_value=tmpdir):
                with open(extended_file, 'w') as f:
                    json.dump([{'Url': 'http://existing.com'}], f)
                
                scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        assert "No new records found" in scraping_status["status_message"]
        assert scraping_status["records_added"] == 0
    
    @patch('data_updater.GradCafeScraper')
    def test_scrape_and_update_background_exception_handling(
        self, mock_scraper_class, test_db
    ):
        """Test exception handling in background scraping"""
        mock_scraper_class.side_effect = Exception("Scraper failed")
        
        scrape_and_update_background(dbname='gradcafe_test', max_pages=1)
        
        assert "Error:" in scraping_status["status_message"]
        assert scraping_status["is_running"] == False


@pytest.mark.integration
class TestScrapingControl:
    """Test scraping control functions"""
    
    def test_start_scraping_success(self, test_db):
        """Test starting scraping in background thread"""
        # Reset scraping status
        scraping_status["is_running"] = False
        
        with patch('data_updater.scrape_and_update_background'):
            result = start_scraping(dbname='gradcafe_test', max_pages=1)
        
        assert result["success"] == True
        assert "started" in result["message"].lower()
    
    def test_start_scraping_already_running(self, test_db):
        """Test starting scraping when already in progress"""
        scraping_status["is_running"] = True
        
        result = start_scraping(dbname='gradcafe_test', max_pages=1)
        
        assert result["success"] == False
        assert "already in progress" in result["message"].lower()
        
        # Reset for other tests
        scraping_status["is_running"] = False
    
    def test_get_scraping_status_returns_copy(self):
        """Test getting current scraping status returns a copy"""
        from data_updater import get_scraping_status
        scraping_status["is_running"] = False
        scraping_status["status_message"] = "Test message"
        scraping_status["records_added"] = 42
        
        status = get_scraping_status()
        
        assert status["is_running"] == False
        assert status["status_message"] == "Test message"
        assert status["records_added"] == 42
        # Verify it returns a copy, not the original
        assert status is not scraping_status


@pytest.mark.db
class TestEdgeCasesDataUpdater:
    """Test edge cases and error paths"""
    
    def test_add_records_with_null_bytes_in_strings(self, test_db):
        """Test handling of null bytes in string fields"""
        records = [
            {
                'applicant_status': 'Accepted',
                'program': 'Computer\x00Science',  # Null byte
                'comments': 'Great\u0000program',  # Unicode null
                'url': 'http://test.com/nullbyte',
                'citizenship': 'American'
            }
        ]
        
        count = add_new_records_to_db(records, dbname='gradcafe_test')
        assert count == 1
    
    def test_add_records_mixed_old_and_new_format(self, test_db):
        """Test processing both old and new format records in same batch"""
        mixed_records = [
            # New format
            {
                'applicant_status': 'Accepted',
                'program': 'MIT - Computer Science',
                'url': 'http://test1.com',
                'citizenship': 'American'
            },
            # Old format
            {
                'Acceptance Date': '15/02/2026',
                'University': 'Stanford',
                'Program': 'AI',
                'Url': 'http://test2.com'
            }
        ]
        
        count = add_new_records_to_db(mixed_records, dbname='gradcafe_test')
        assert count == 2
    
    def test_add_records_with_none_values(self, test_db):
        """Test handling records with None/null values"""
        records = [
            {
                'applicant_status': None,
                'program': None,
                'url': 'http://test-none.com',
                'comments': None
            }
        ]
        
        count = add_new_records_to_db(records, dbname='gradcafe_test')
        assert count == 1
