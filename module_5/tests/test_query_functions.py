"""
Additional tests for query functions to ensure 100% coverage.

These tests verify all query functions work correctly with the test database.
"""
import pytest
import psycopg2
import os
from psycopg2.extras import execute_values
from db_helpers import get_test_db_params


@pytest.fixture
def populated_test_db():
    """Create a test database with sample data."""
    conn_params = get_test_db_params()
    conn = psycopg2.connect(**conn_params)
    
    # Setup: Create table and insert test data
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
    
    # Insert sample data
    test_data = [
        ('MIT - CS', 'Comment 1', '2026-02-14', 'http://test1.com', 'Accepted', 'Fall 2026', 
         'International', 3.8, 320, 160, 4.0, 'PhD', 'CS', 'MIT', '{}'),
        ('Stanford - EE', 'Comment 2', '2026-02-13', 'http://test2.com', 'Accepted', 'Fall 2026',
         'American', 3.9, 330, 165, 4.5, 'Masters', 'EE', 'Stanford', '{}'),
        ('Berkeley - CS', 'Comment 3', '2026-02-12', 'http://test3.com', 'Rejected', 'Fall 2026',
         'International', 3.7, 315, 158, 3.5, 'PhD', 'CS', 'Berkeley', '{}'),
        ('CMU - Robotics', 'Comment 4', '2026-02-11', 'http://test4.com', 'Accepted', 'Spring 2026',
         'American', 3.95, 335, 170, 5.0, 'PhD', 'Robotics', 'CMU', '{}'),
    ]
    
    insert_query = """
        INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international,
                                   gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                                   llm_generated_university, raw_data)
        VALUES %s
    """
    execute_values(cur, insert_query, test_data)
    conn.commit()
    cur.close()
    
    yield conn
    
    # Teardown
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
    conn.commit()
    cur.close()
    conn.close()


@pytest.mark.db
def test_question_5(populated_test_db):
    """Test question_5 returns expected format."""
    from query_data import question_5
    
    result = question_5(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_6(populated_test_db):
    """Test question_6 returns expected format."""
    from query_data import question_6
    
    result = question_6(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_7(populated_test_db):
    """Test question_7 returns expected format."""
    from query_data import question_7
    
    result = question_7(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_8(populated_test_db):
    """Test question_8 returns expected format."""
    from query_data import question_8
    
    result = question_8(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_9(populated_test_db):
    """Test question_9 returns expected format."""
    from query_data import question_9
    
    result = question_9(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_10(populated_test_db):
    """Test question_10 returns expected format."""
    from query_data import question_10
    
    result = question_10(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result


@pytest.mark.db
def test_question_11(populated_test_db):
    """Test question_11 returns expected format."""
    from query_data import question_11
    
    result = question_11(dbname='gradcafe_test')
    assert isinstance(result, dict)
    assert 'question' in result
    assert 'query' in result
    assert 'answer' in result
    # Answer should be a list for question 11
    assert isinstance(result['answer'], list)


@pytest.mark.db
def test_run_all_queries(populated_test_db):
    """Test run_all_queries returns all 11 query results."""
    from query_data import run_all_queries
    
    result = run_all_queries(dbname='gradcafe_test')
    assert isinstance(result, dict)
    
    # Should have all 11 questions
    for i in range(1, 12):
        key = f'q{i}'
        assert key in result, f"Missing {key} in results"
        assert isinstance(result[key], dict)
        assert 'question' in result[key]
        assert 'query' in result[key]
        assert 'answer' in result[key]


@pytest.mark.db
def test_get_db_connection():
    """Test get_db_connection creates a valid connection."""
    from query_data import get_db_connection
    
    conn = get_db_connection(dbname='gradcafe_test')
    assert conn is not None
    
    # Test connection is usable
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    assert result[0] == 1
    
    cur.close()
    conn.close()
