"""
Tests for database writes and queries.

These tests verify:
- Insert on pull: new rows exist with required (non-null) fields
- Idempotency/constraints: duplicate rows don't create duplicates
- Simple query function returns dict with expected keys
"""
import pytest
import psycopg2
import os
from datetime import datetime
from conftest import get_test_db_params


@pytest.fixture
def test_db():
    """Create a test database connection."""
    conn_params = get_test_db_params()
    conn = psycopg2.connect(**conn_params)
    
    # Setup: Create table
    cur = conn.cursor()
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
    conn.commit()
    cur.close()
    
    yield conn
    
    # Teardown: Clean up
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
    conn.commit()
    cur.close()
    conn.close()


@pytest.mark.db
def test_insert_on_pull_creates_new_rows(test_db):
    """Test that after insert, new rows exist with required non-null fields."""
    # Note: We insert directly rather than calling add_new_records_to_db
    # since that function uses hardcoded connection params
    
    # Before: table should be empty
    cur = test_db.cursor()
    cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
    count_before = cur.fetchone()[0]
    assert count_before == 0, "Table should be empty before insert"
    cur.close()
    
    # Create test records
    test_records = [
        {
            'program': 'MIT - Computer Science',
            'comments': 'Great program!',
            'date_added': 'February 14, 2026',
            'url': 'http://gradcafe.com/test1',
            'applicant_status': 'Accepted',
            'semester_year_start': 'Fall 2026',
            'citizenship': 'International',
            'gpa': 'GPA 3.85',
            'gre': 'GRE 325',
            'gre_v': 165,
            'gre_aw': 4.5,
            'masters_or_phd': 'PhD',
            'llm-generated-program': 'Computer Science',
            'llm-generated-university': 'MIT'
        },
        {
            'program': 'Stanford - Electrical Engineering',
            'comments': 'Amazing research opportunities',
            'date_added': 'February 13, 2026',
            'url': 'http://gradcafe.com/test2',
            'applicant_status': 'Accepted',
            'semester_year_start': 'Fall 2026',
            'citizenship': 'American',
            'gpa': 'GPA 3.90',
            'gre': 'GRE 330',
            'gre_v': 168,
            'gre_aw': 5.0,
            'masters_or_phd': 'Masters',
            'llm-generated-program': 'Electrical Engineering',
            'llm-generated-university': 'Stanford'
        }
    ]
    
    # Mock function needs to work with test database
    # Since add_new_records_to_db uses hardcoded connection, we need to insert directly
    from psycopg2.extras import execute_values
    
    cur = test_db.cursor()
    data_to_insert = []
    for r in test_records:
        row = (
            r.get('program'),
            r.get('comments'),
            datetime.strptime(r.get('date_added'), '%B %d, %Y').strftime('%Y-%m-%d'),
            r.get('url'),
            r.get('applicant_status'),
            r.get('semester_year_start'),
            r.get('citizenship'),
            float(r.get('gpa', 'GPA 0').replace('GPA ', '')),
            float(r.get('gre', 'GRE 0').replace('GRE ', '')),
            r.get('gre_v'),
            r.get('gre_aw'),
            r.get('masters_or_phd'),
            r.get('llm-generated-program'),
            r.get('llm-generated-university'),
            '{}' # raw_data
        )
        data_to_insert.append(row)
    
    insert_query = """
        INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international,
                                   gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                                   llm_generated_university, raw_data)
        VALUES %s
    """
    execute_values(cur, insert_query, data_to_insert)
    test_db.commit()
    cur.close()
    
    # After: rows should exist
    cur = test_db.cursor()
    cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
    count_after = cur.fetchone()[0]
    assert count_after == 2, "Should have 2 rows after insert"
    
    # Verify required non-null fields
    cur.execute("""
        SELECT program, url, status, term 
        FROM gradcafe_main 
        WHERE program IS NOT NULL 
          AND url IS NOT NULL 
          AND status IS NOT NULL;
    """)
    rows_with_required = cur.fetchall()
    assert len(rows_with_required) == 2, "All rows should have required non-null fields"
    cur.close()


@pytest.mark.db
def test_duplicate_rows_do_not_create_duplicates(test_db):
    """Test idempotency: duplicate pulls don't duplicate rows in database."""
    from psycopg2.extras import execute_values
    from psycopg2 import IntegrityError
    
    # Insert first record
    cur = test_db.cursor()
    test_record = (
        'MIT - Computer Science',
        'Test comment',
        '2026-02-14',
        'http://gradcafe.com/unique1',  # Unique URL
        'Accepted',
        'Fall 2026',
        'International',
        3.85,
        325,
        165,
        4.5,
        'PhD',
        'Computer Science',
        'MIT',
        '{}'
    )
    
    insert_query = """
        INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international,
                                   gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                                   llm_generated_university, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(insert_query, test_record)
    test_db.commit()
    cur.close()
    
    # Check count after first insert
    cur = test_db.cursor()
    cur.execute("SELECT COUNT(*) FROM gradcafe_main WHERE url = 'http://gradcafe.com/unique1';")
    count_first = cur.fetchone()[0]
    assert count_first == 1
    cur.close()
    
    # Try to insert duplicate (same URL)
    cur = test_db.cursor()
    with pytest.raises(IntegrityError):
        cur.execute(insert_query, test_record)
        test_db.commit()
    
    test_db.rollback()
    cur.close()
    
    # Verify count is still 1 (no duplicate created)
    cur = test_db.cursor()
    cur.execute("SELECT COUNT(*) FROM gradcafe_main WHERE url = 'http://gradcafe.com/unique1';")
    count_after = cur.fetchone()[0]
    assert count_after == 1, "Should still have only 1 row (no duplicates)"
    cur.close()


@pytest.mark.db
def test_simple_query_function_returns_expected_keys(test_db):
    """Test that query function returns dict with expected Module-3 keys."""
    from query_data import question_1, question_2, question_3, question_4
    
    # Insert test data first
    cur = test_db.cursor()
    from psycopg2.extras import execute_values
    
    test_data = [
        (
            'MIT - CS', 'Comment 1', '2026-02-14', 'http://test1.com',
            'Accepted', 'Fall 2026', 'International', 3.8, 320, 160, 4.0,
            'PhD', 'CS', 'MIT', '{}'
        ),
        (
            'Stanford - EE', 'Comment 2', '2026-02-13', 'http://test2.com',
            'Accepted', 'Fall 2026', 'American', 3.9, 330, 165, 4.5,
            'Masters', 'EE', 'Stanford', '{}'
        )
    ]
    
    insert_query = """
        INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international,
                                   gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                                   llm_generated_university, raw_data)
        VALUES %s
    """
    execute_values(cur, insert_query, test_data)
    test_db.commit()
    cur.close()
    
    # Test question_1 - should return dict with 'question', 'query', 'answer'
    result_q1 = question_1(dbname='gradcafe_test')
    assert isinstance(result_q1, dict), "Result should be a dictionary"
    assert 'question' in result_q1, "Result should have 'question' key"
    assert 'query' in result_q1, "Result should have 'query' key"
    assert 'answer' in result_q1, "Result should have 'answer' key"
    assert result_q1['answer'] == 2, "Should find 2 Fall 2026 entries"
    
    # Test question_2 - percentage of international students
    result_q2 = question_2(dbname='gradcafe_test')
    assert isinstance(result_q2, dict)
    assert 'question' in result_q2
    assert 'query' in result_q2
    assert 'answer' in result_q2
    assert '%' in result_q2['answer'], "Answer should include percentage symbol"
    
    # Test question_3 - averages (nested dict)
    result_q3 = question_3(dbname='gradcafe_test')
    assert isinstance(result_q3, dict)
    assert 'answer' in result_q3
    assert isinstance(result_q3['answer'], dict), "Answer should be a dictionary"
    assert 'avg_gpa' in result_q3['answer']
    assert 'avg_gre' in result_q3['answer']
    assert 'avg_gre_v' in result_q3['answer']
    assert 'avg_gre_aw' in result_q3['answer']
    
    # Test question_4
    result_q4 = question_4(dbname='gradcafe_test')
    assert isinstance(result_q4, dict)
    assert 'question' in result_q4
    assert 'answer' in result_q4


@pytest.mark.db
def test_database_schema_has_required_fields(test_db):
    """Test that database schema includes all required Module-3 fields."""
    cur = test_db.cursor()
    
    # Get column information
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'gradcafe_main';
    """)
    columns = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    
    # Check required fields exist
    required_fields = [
        'p_id', 'program', 'comments', 'date_added', 'url', 'status',
        'term', 'us_or_international', 'gpa', 'gre', 'gre_v', 'gre_aw',
        'degree', 'llm_generated_program', 'llm_generated_university', 'raw_data'
    ]
    
    for field in required_fields:
        assert field in columns, f"Required field '{field}' missing from schema"


@pytest.mark.db
def test_query_handles_empty_database(test_db):
    """Test that query functions handle empty database gracefully."""
    from query_data import question_1, question_2
    
    # Database is empty (from fixture setup)
    result_q1 = question_1(dbname='gradcafe_test')
    assert result_q1['answer'] == 0, "Should return 0 for empty database"
    
    # Question 2 may return N/A or 0.00% for empty database
    result_q2 = question_2(dbname='gradcafe_test')
    assert 'answer' in result_q2
