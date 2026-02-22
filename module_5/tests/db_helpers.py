"""
Database helper utilities for tests.
"""
import os


def get_test_db_params():
    """
    Parse DATABASE_URL and return connection parameters.
    This helper function can be used by all tests to get database credentials.
    """
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError(
            "DATABASE_URL environment variable is required for tests. "
            "Example: export DATABASE_URL='postgresql://user@localhost/gradcafe_test'"
        )
    
    # Parse connection string
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', '')
    
    # Parse username:password@host/dbname
    if '@' in db_url:
        user_part, host_part = db_url.split('@')
        # Extract password if present
        if ':' in user_part:
            user, password = user_part.split(':', 1)
        else:
            user = user_part
            password = None
        if '/' in host_part:
            host, dbname = host_part.split('/')
        else:
            host = host_part
            dbname = 'gradcafe_test'
    else:
        # No DATABASE_URL provided and no defaults with credentials
        raise ValueError(
            "DATABASE_URL is malformed. Expected format: "
            "postgresql://[user[:password]@]host/dbname"
        )
    
    conn_params = {
        "dbname": dbname,
        "user": user,
        "host": host
    }
    if password:
        conn_params["password"] = password
    
    return conn_params
