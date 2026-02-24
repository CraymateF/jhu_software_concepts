"""Targeted branch tests to drive source coverage to 100%."""

from unittest.mock import MagicMock, patch
import pytest


def test_data_updater_get_db_params_url_without_password(monkeypatch):
    """Covers DATABASE_URL path where user has no password."""
    from data_updater import get_db_params

    monkeypatch.setenv("DATABASE_URL", "postgresql://testuser@localhost:5432/ignored_db")
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    params = get_db_params("gradcafe_test")

    assert params["user"] == "testuser"
    assert params["host"] == "localhost"
    assert params["port"] == "5432"
    assert params["dbname"] == "gradcafe_test"
    assert "password" not in params


def test_data_updater_get_db_params_fallback_with_password(monkeypatch):
    """Covers fallback env path with DB_PASSWORD populated."""
    from data_updater import get_db_params

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "fallback_user")
    monkeypatch.setenv("DB_HOST", "db-host")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_PASSWORD", "fallback_secret")

    params = get_db_params("gradcafe_test")

    assert params == {
        "dbname": "gradcafe_test",
        "user": "fallback_user",
        "host": "db-host",
        "port": "5433",
        "password": "fallback_secret",
    }


def test_load_data_get_db_params_url_without_password(monkeypatch):
    """Covers load_data.get_db_params DATABASE_URL branch without password."""
    from load_data import get_db_params

    monkeypatch.setenv("DATABASE_URL", "postgresql://plainuser@localhost:5432/ignored_db")
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    params = get_db_params("gradcafe_test")

    assert params["user"] == "plainuser"
    assert params["host"] == "localhost"
    assert params["port"] == "5432"
    assert params["dbname"] == "gradcafe_test"
    assert "password" not in params


def test_load_data_get_db_params_fallback_with_password(monkeypatch):
    """Covers load_data.get_db_params fallback path with password."""
    from load_data import get_db_params

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "fallback_user")
    monkeypatch.setenv("DB_HOST", "fallback-host")
    monkeypatch.setenv("DB_PORT", "6543")
    monkeypatch.setenv("DB_PASSWORD", "pw")

    params = get_db_params("gradcafe_test")

    assert params == {
        "dbname": "gradcafe_test",
        "user": "fallback_user",
        "host": "fallback-host",
        "port": "6543",
        "password": "pw",
    }


def test_query_data_get_db_connection_url_without_password(monkeypatch):
    """Covers query_data DATABASE_URL branch where user has no password."""
    from query_data import get_db_connection

    monkeypatch.setenv("DATABASE_URL", "postgresql://q_user@localhost:5432/url_db")

    with patch("query_data.psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        get_db_connection("gradcafe_test")

    kwargs = mock_connect.call_args.kwargs
    assert kwargs["user"] == "q_user"
    assert kwargs["host"] == "localhost"
    assert kwargs["port"] == "5432"
    assert kwargs["dbname"] == "gradcafe_test"
    assert "password" not in kwargs


def test_query_data_get_db_connection_fallback_with_password(monkeypatch):
    """Covers query_data fallback env branch including DB_PASSWORD."""
    from query_data import get_db_connection

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "fallback_query_user")
    monkeypatch.setenv("DB_HOST", "query-host")
    monkeypatch.setenv("DB_PORT", "7000")
    monkeypatch.setenv("DB_PASSWORD", "query_pw")

    with patch("query_data.psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        get_db_connection("gradcafe_test")

    kwargs = mock_connect.call_args.kwargs
    assert kwargs == {
        "dbname": "gradcafe_test",
        "user": "fallback_query_user",
        "host": "query-host",
        "port": "7000",
        "password": "query_pw",
    }


def test_load_data_default_file_path_falls_back_to_first_candidate(monkeypatch):
    """Covers default file path fallback branch when no candidate exists."""
    from load_data import load_data

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    monkeypatch.delenv("DATABASE_URL", raising=False)

    with patch("load_data.Path.exists", return_value=False), patch(
        "load_data.psycopg2.connect", return_value=mock_conn
    ), patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "[]"
        load_data(dbname="gradcafe_test", file_path=None)

    mock_open.assert_called_once()


def test_data_updater_get_db_params_url_with_password(monkeypatch):
    """Covers password extraction branch in data_updater.get_db_params."""
    from data_updater import get_db_params

    monkeypatch.setenv("DATABASE_URL", "postgresql://userx:passx@localhost:5432/ignored")
    params = get_db_params("gradcafe_test")

    assert params["user"] == "userx"
    assert params["password"] == "passx"


def test_load_data_get_db_params_url_with_password(monkeypatch):
    """Covers password extraction branch in load_data.get_db_params."""
    from load_data import get_db_params

    monkeypatch.setenv("DATABASE_URL", "postgresql://userl:passl@localhost:5432/ignored")
    params = get_db_params("gradcafe_test")

    assert params["user"] == "userl"
    assert params["password"] == "passl"


def test_query_data_get_db_connection_url_with_password(monkeypatch):
    """Covers password extraction branch in query_data.get_db_connection."""
    from query_data import get_db_connection

    monkeypatch.setenv("DATABASE_URL", "postgresql://userq:passq@localhost:5432/url_db")

    with patch("query_data.psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        get_db_connection("gradcafe_test")

    kwargs = mock_connect.call_args.kwargs
    assert kwargs["user"] == "userq"
    assert kwargs["password"] == "passq"


def test_load_data_invalid_dbname_raises_value_error():
    """Covers invalid dbname validation branch in load_data."""
    from load_data import load_data

    with pytest.raises(ValueError) as exc_info:
        load_data(dbname="bad-name!", file_path="sample_data/llm_extend_applicant_data.json")

    exc = exc_info.value
    assert "Invalid database name" in str(exc)
