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
    
    # Parse username:password@host:port/dbname
    if '@' in db_url:
        user_part, host_part = db_url.split('@')
        # Extract password if present
        if ':' in user_part:
            user, password = user_part.split(':', 1)
        else:
            user = user_part
            password = None
        
        # Parse host:port/dbname
        if '/' in host_part:
            host_and_port, dbname = host_part.split('/', 1)
        else:
            host_and_port = host_part
            dbname = 'gradcafe_test'
        
        # Extract port if present
        if ':' in host_and_port:
            host, port = host_and_port.split(':', 1)
        else:
            host = host_and_port
            port = None
    else:
        # No DATABASE_URL provided and no defaults with credentials
        raise ValueError(
            "DATABASE_URL is malformed. Expected format: "
            "postgresql://[user[:password]@]host[:port]/dbname"
        )
    
    conn_params = {
        "dbname": dbname,
        "user": user,
        "host": host
    }
    if password:
        conn_params["password"] = password
    if port:
        conn_params["port"] = port
    
    return conn_params
