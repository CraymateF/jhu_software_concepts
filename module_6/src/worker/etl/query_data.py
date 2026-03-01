"""
query_data.py – read-only database queries for the worker ETL layer.

Provides helpers that the worker can use to check data state without
going through the web service.
"""
import os
import re

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=False)


def get_db_connection(dbname=None):
    """Return a psycopg2 connection using DATABASE_URL or DB_* env vars."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if dbname:
            database_url = re.sub(r"(/[^/?]+)(\?.*)?$", f"/{dbname}\\2", database_url)
        return psycopg2.connect(database_url)

    conn_params = {
        "dbname": dbname or os.getenv("DB_NAME", "gradcafe"),
        "user":   os.getenv("DB_USER"),
        "host":   os.getenv("DB_HOST"),
        "port":   os.getenv("DB_PORT", "5432"),
    }
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        conn_params["password"] = db_password
    return psycopg2.connect(**conn_params)


def get_record_count(dbname=None) -> int:
    """Return the total number of rows in gradcafe_main."""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_existing_urls(dbname=None) -> set:
    """Return the set of URLs already present in gradcafe_main."""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    cur.execute("SELECT url FROM gradcafe_main WHERE url IS NOT NULL;")
    urls = {row[0] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return urls


def get_watermark(source: str, dbname=None) -> str | None:
    """Return the last_seen watermark for the given source, or None."""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    cur.execute(
        "SELECT last_seen FROM ingestion_watermarks WHERE source = %s;", (source,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None
