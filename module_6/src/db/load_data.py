"""
Module to load GradCafe data from JSON files into PostgreSQL database.
Extended with watermark table for idempotent incremental ingestion.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables (don't override existing vars)
load_dotenv(override=False)


def get_db_connection(dbname=None):
    """
    Create a psycopg2 connection using DATABASE_URL or individual DB_* env vars.
    In Docker Compose, DATABASE_URL is always set.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Replace dbname in URL if override requested
        if dbname:
            # Replace the database name portion in the URL
            import re  # pylint: disable=import-outside-toplevel
            database_url = re.sub(r"(/[^/?]+)(\?.*)?$", f"/{dbname}\\2", database_url)
        return psycopg2.connect(database_url)

    # Fallback to individual env vars
    conn_params = {
        "dbname": dbname or os.getenv("DB_NAME", "gradcafe"),
        "user": os.getenv("DB_USER"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
    }
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        conn_params["password"] = db_password
    return psycopg2.connect(**conn_params)


def ensure_schema(conn):
    """Create tables if they don't exist (idempotent)."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gradcafe_main (
            p_id                    SERIAL PRIMARY KEY,
            program                 TEXT,
            comments                TEXT,
            date_added              DATE,
            url                     TEXT,
            status                  TEXT,
            term                    TEXT,
            us_or_international     TEXT,
            gpa                     FLOAT,
            gre                     FLOAT,
            gre_v                   FLOAT,
            gre_aw                  FLOAT,
            degree                  TEXT,
            llm_generated_program   TEXT,
            llm_generated_university TEXT,
            raw_data                JSONB
        );
    """)
    cur.execute("ALTER TABLE gradcafe_main ADD COLUMN IF NOT EXISTS raw_data JSONB;")

    # Watermark table for incremental scraping idempotence
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_watermarks (
            source      TEXT PRIMARY KEY,
            last_seen   TEXT,
            updated_at  TIMESTAMPTZ DEFAULT now()
        );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_gradcafe_url ON gradcafe_main (url);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gradcafe_date ON gradcafe_main (date_added);")
    conn.commit()
    cur.close()


def parse_date(date_str):
    """Convert various date formats to YYYY-MM-DD for PostgreSQL."""
    if not date_str or not isinstance(date_str, str):
        return None
    for fmt in ("%d/%m/%Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def extract_numeric(value_str, prefix=""):
    """Extract float from strings like 'GPA 3.74' or 'GRE 314'."""
    if not value_str:
        return None
    if isinstance(value_str, (int, float)):
        return float(value_str)
    if isinstance(value_str, str):
        cleaned = value_str.replace(prefix, "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def clean_string(value):
    """Remove NUL characters from strings to prevent PostgreSQL errors."""
    if isinstance(value, str):
        return value.replace("\x00", "").replace("\u0000", "")
    return value


def record_to_row(r):
    """Convert a JSON record (old or new format) to a DB row tuple."""
    is_new_format = any(k in r for k in ("applicant_status", "citizenship", "semester_year_start"))

    if is_new_format:
        combined_program = r.get("program", "")
        comments = r.get("comments")
        date_added = parse_date(r.get("date_added"))
        url = r.get("url")
        status_map = {
            "Accepted": "Accepted", "Rejected": "Rejected",
            "Interview": "Interview", "Wait listed": "Wait listed", "Waitlisted": "Wait listed",
        }
        status = status_map.get(r.get("applicant_status", ""), r.get("applicant_status"))
        term = r.get("semester_year_start")
        citizenship_map = {"American": "American", "International": "International", "U": "American", "I": "International"}
        us_or_international = citizenship_map.get(r.get("citizenship", ""), r.get("citizenship"))
        gpa = extract_numeric(r.get("gpa"), "GPA")
        gre = extract_numeric(r.get("gre"), "GRE")
        gre_v_raw = r.get("gre_v")
        gre_v = float(gre_v_raw) if isinstance(gre_v_raw, (int, float)) else None
        gre_aw_raw = r.get("gre_aw")
        gre_aw = float(gre_aw_raw) if isinstance(gre_aw_raw, (int, float)) else None
        degree = r.get("masters_or_phd")
        llm_program = r.get("llm-generated-program")
        llm_university = r.get("llm-generated-university")
    else:
        acceptance_date = r.get("Acceptance Date")
        rejection_date = r.get("Rejection Date")
        if acceptance_date:
            status, date_added = "Accepted", parse_date(acceptance_date)
        elif rejection_date:
            status, date_added = "Rejected", parse_date(rejection_date)
        else:
            status, date_added = None, None
        university = r.get("University", "")
        program_name = r.get("Program", "")
        combined_program = f"{university} - {program_name}" if university and program_name else (university or program_name)
        comments = r.get("Notes")
        url = r.get("Url")
        term = r.get("Term")
        us_or_international = r.get("US/International")
        gpa = r.get("GPA") if isinstance(r.get("GPA"), (int, float)) else None
        gre = r.get("GRE General") if isinstance(r.get("GRE General"), (int, float)) else None
        gre_v = r.get("GRE Verbal") if isinstance(r.get("GRE Verbal"), (int, float)) else None
        gre_aw = r.get("GRE Analytical Writing") if isinstance(r.get("GRE Analytical Writing"), (int, float)) else None
        degree = r.get("Degree")
        llm_program = r.get("LLM Generated Program")
        llm_university = r.get("LLM Generated University")

    return (
        clean_string(combined_program),
        clean_string(comments) if isinstance(comments, str) else None,
        date_added,
        clean_string(url) if isinstance(url, str) else None,
        clean_string(status),
        clean_string(term) if isinstance(term, str) else None,
        clean_string(us_or_international) if isinstance(us_or_international, str) else None,
        gpa, gre, gre_v, gre_aw,
        clean_string(degree) if isinstance(degree, str) else None,
        clean_string(llm_program),
        clean_string(llm_university),
        json.dumps(r).replace("\x00", "").replace("\\u0000", ""),
    )


def load_data(file_path=None, dbname=None, skip_if_populated=True):
    """
    Load applicant data from a JSON file into the PostgreSQL database.

    Args:
        file_path: Path to the JSON data file (defaults to DATA_FILE env var).
        dbname: Override database name (uses DATABASE_URL by default).
        skip_if_populated: Skip insert if table already has rows.
    """
    if file_path is None:
        file_path = os.getenv("DATA_FILE", "/data/applicant_data.json")

    if not Path(file_path).exists():
        # Try a few fallback locations
        candidates = [
            "data/applicant_data.json",
            "../data/applicant_data.json",
            "applicant_data.json",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                file_path = candidate
                break
        else:
            print(f"WARNING: Data file not found at {file_path} or fallbacks. Skipping load.")
            return

    conn = get_db_connection(dbname)
    try:
        ensure_schema(conn)
        cur = conn.cursor()

        if skip_if_populated:
            cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
            count = cur.fetchone()[0]
            if count > 0:
                print(f"Database already contains {count} records. Skipping initial load.")
                cur.close()
                return

        print(f"Loading data from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().replace("\x00", "")

        try:
            records = json.loads(content)
            if not isinstance(records, list):
                records = [records]
        except json.JSONDecodeError:
            records = []
            for line in content.strip().split("\n"):
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        print(f"Detected {len(records)} records. Starting import...")
        data_to_insert = [record_to_row(r) for r in records]

        # Insert with ON CONFLICT DO NOTHING if url is provided as natural key
        insert_query = """
            INSERT INTO gradcafe_main (
                program, comments, date_added, url, status, term, us_or_international,
                gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                llm_generated_university, raw_data
            )
            VALUES %s
        """
        execute_values(cur, insert_query, data_to_insert)
        conn.commit()
        print(f"Success! Imported {len(data_to_insert)} records.")
        cur.close()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Error during data load: {exc}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    load_data(file_path=file_arg, skip_if_populated=True)
