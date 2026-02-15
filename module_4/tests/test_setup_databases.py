"""
Tests for setup_databases module.

These tests verify database setup utilities.
"""
import pytest
import os


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
    
    # Get postgres credentials from DATABASE_URL if available
    db_url = os.getenv('DATABASE_URL', '')
    if 'postgres:postgres@' in db_url:
        # GitHub Actions environment
        user_flag = '-U postgres'
        env_vars = 'PGPASSWORD=postgres '
    else:
        # Local environment
        user_flag = ''
        env_vars = ''
    
    # Cleanup first if exists
    run_command(f'{env_vars}dropdb {user_flag} test_temp_db 2>&1 || true')
    
    # Create the database
    result1 = run_command(f'{env_vars}createdb {user_flag} test_temp_db 2>&1')
    assert result1 is True  # Should succeed
    
    # Cleanup
    result2 = run_command(f'{env_vars}dropdb {user_flag} test_temp_db 2>&1')
    assert result2 is True  # Should succeed
