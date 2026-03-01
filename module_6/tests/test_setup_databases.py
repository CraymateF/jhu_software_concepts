"""
Tests for setup_databases module.

NOTE: setup_databases.py is not used in module_6.  Schema DDL is in
src/db/init.sql and data loading is in src/db/load_data.py.
These tests are skipped.
"""
import pytest
import os

pytestmark = pytest.mark.skip(
    reason="setup_databases.py not present in module_6 (replaced by src/db/init.sql + load_data.py)"
)


@pytest.mark.db
def test_run_command_success():
    """Test run_command succeeds with valid command."""
    from setup_databases import run_command
    
    # Test with a simple command that should succeed
    result = run_command('echo "test"')
    assert result is True


@pytest.mark.db
def test_run_command_handles_existing_database():
    """Test run_command handles database operations."""
    from setup_databases import run_command
    import subprocess
    
    # Get postgres credentials from DATABASE_URL if available
    db_url = os.getenv('DATABASE_URL', '')
    if '@' in db_url and 'localhost' in db_url:
        # GitHub Actions or configured environment - use TCP connection
        from db_helpers import get_test_db_params
        try:
            params = get_test_db_params()
            user_flag = ['-U', params['user'], '-h', params['host']]
            env_password = params.get('password')
        except (ValueError, KeyError):
            # Fallback to local
            user_flag = []
            env_password = None
    else:
        # Local environment
        user_flag = []
        env_password = None
    
    # Cleanup first if exists (directly using subprocess to handle errors)
    env = os.environ.copy()
    if env_password:
        env['PGPASSWORD'] = env_password
    cmd_parts = ['dropdb'] + user_flag + ['test_temp_db']
    subprocess.run(cmd_parts, env=env, capture_output=True)  # Ignore result
    
    # Create the database - this should succeed
    cmd_parts = ['createdb'] + user_flag + ['test_temp_db']
    result1 = subprocess.run(cmd_parts, env=env, capture_output=True)
    assert result1.returncode == 0, f"Create failed: {result1.stderr.decode()}"
    
    # Cleanup - this should succeed
    cmd_parts = ['dropdb'] + user_flag + ['test_temp_db']
    result2 = subprocess.run(cmd_parts, env=env, capture_output=True)
    assert result2.returncode == 0, f"Drop failed: {result2.stderr.decode()}"
