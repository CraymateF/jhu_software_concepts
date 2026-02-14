"""
Pytest configuration and shared fixtures for Module 4 tests.
"""
import pytest
import sys
import os
import psycopg2

# Add module_4/src to Python path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def app():
    """Create a test Flask app instance."""
    from app import create_app
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 
                   'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test Q5', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test Q10', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query, status_func=mock_status)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def test_db():
    """Create and setup a test database connection."""
    # Use DATABASE_URL from environment or default to test database
    db_url = os.getenv('DATABASE_URL', 'postgresql://fadetoblack@localhost/gradcafe_test')
    
    # Parse connection string
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', '')
    
    # Simple parsing (username@host/dbname)
    if '@' in db_url:
        user_part, host_part = db_url.split('@')
        user = user_part
        if '/' in host_part:
            host, dbname = host_part.split('/')
        else:
            host = host_part
            dbname = 'gradcafe_test'
    else:
        user = 'fadetoblack'
        host = 'localhost'
        dbname = 'gradcafe_test'
    
    conn_params = {
        "dbname": dbname,
        "user": user,
        "host": host
    }
    
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
    
    # Teardown
    conn.close()
