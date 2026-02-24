"""
Module to load GradCafe data from JSON files into PostgreSQL database.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables from .env file (don't override existing vars for testing)
load_dotenv(override=False)

def get_db_params(dbname='gradcafe_sample'):
    """
    Get database connection parameters from environment variables.
    Supports both DATABASE_URL and individual DB_* variables.
    """
    # Check if DATABASE_URL is set (for testing and GitHub Actions)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Parse DATABASE_URL format: postgresql://user:pass@host:port/dbname
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', '')
        
        conn_params = {}
        
        if '@' in database_url:
            user_part, host_part = database_url.split('@', 1)
            # Extract password if present
            if ':' in user_part:
                user, password = user_part.split(':', 1)
                conn_params["password"] = password
            else:
                user = user_part
            conn_params["user"] = user
            
            # Parse host:port/dbname
            if '/' in host_part:
                host_and_port, url_db = host_part.split('/', 1)
                # Use parameter dbname if provided explicitly, otherwise use URL dbname
                conn_params["dbname"] = dbname
            else:
                host_and_port = host_part
                conn_params["dbname"] = dbname
            
            # Parse port if present
            if ':' in host_and_port:
                host, port = host_and_port.split(':', 1)
                conn_params["host"] = host
                conn_params["port"] = port
            else:
                conn_params["host"] = host_and_port
        else:
            # No @ sign - DATABASE_URL is malformed, use defaults
            conn_params = {
                "dbname": dbname,
                "user": os.getenv('DB_USER', 'fadetoblack'),
                "host": os.getenv('DB_HOST', 'localhost'),
                "port": os.getenv('DB_PORT', '5432')
            }
    else:
        # Fall back to individual environment variables
        conn_params = {
            "dbname": dbname,
            "user": os.getenv('DB_USER', 'fadetoblack'),
            "host": os.getenv('DB_HOST', 'localhost'),
            "port": os.getenv('DB_PORT', '5432')
        }

        # Only add password if it's set in environment
        db_password = os.getenv('DB_PASSWORD')
        if db_password:
            conn_params["password"] = db_password

    return conn_params

def load_data(dbname=None, file_path=None):
    """
    Load data into specified database from specified file

    Args:
        dbname: Database name (default: 'gradcafe_sample')
        file_path: Path to JSON file (default: 'module_3/sample_data/llm_extend_applicant_data.json')
    """
    # 1. Database connection parameters
    if dbname is None:
        dbname = 'gradcafe_sample'

    if file_path is None:
        file_path = 'module_3/sample_data/llm_extend_applicant_data.json'

    # Validate dbname to prevent SSRF - only alphanumeric and underscores
    if not dbname.replace('_', '').isalnum():
        raise ValueError(
            f"Invalid database name: {dbname}. "
            "Only alphanumeric characters and underscores are allowed."
        )

    conn_params = get_db_params(dbname)

    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # 2. Prepare table structure
        print("Cleaning up and preparing table schema...")
        cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
        cur.execute("""
            CREATE TABLE gradcafe_main (
                p_id SERIAL PRIMARY KEY,
                program TEXT,
                comments TEXT,
                date_added DATE,
                url TEXT,
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

        # 3. Load and parse JSON file
        print(f"Loading data from: {file_path}")
        print(f"Target database: {dbname}")

        # Validate file path to prevent path traversal
        abs_file_path = Path(file_path).resolve()
        allowed_dirs = [
            Path('module_3/sample_data').resolve(),
            Path('sample_data').resolve(),
            Path('.').resolve()
        ]
        if not any(abs_file_path.is_relative_to(d) for d in allowed_dirs):
            raise ValueError(f"Access denied: {file_path} is outside allowed directories")
        if not abs_file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try to handle both standard JSON array and JSONL (newline-delimited JSON)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove null bytes which can cause issues with PostgreSQL
            content = content.replace('\x00', '')

            # First, try to parse as standard JSON array
            try:
                records = json.loads(content)
                # Ensure it's a list
                if not isinstance(records, list):
                    records = [records]
            except json.JSONDecodeError:
                # If that fails, try parsing as JSONL (one JSON object per line)
                records = []
                for line_num, line in enumerate(content.strip().split('\n'), 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            record = json.loads(line)
                            records.append(record)
                        except json.JSONDecodeError as line_exc:
                            print(f"Warning: Could not parse line {line_num}: {line_exc}")
                            continue

                if not records:
                    raise ValueError(
                        "Could not parse any valid JSON records from file"
                    ) from line_exc

        # 4. Prepare data for batch insertion
        print(f"Detected {len(records)} records. Starting import...")

        def parse_date(date_str):
            """Convert various date formats to YYYY-MM-DD for PostgreSQL"""
            if not date_str or not isinstance(date_str, str):
                return None

            # Try DD/MM/YYYY format (old format)
            try:
                dt = datetime.strptime(date_str, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

            # Try "January 28, 2026" format (new format)
            try:
                dt = datetime.strptime(date_str, '%B %d, %Y')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

            return None

        def extract_numeric(value_str, prefix=""):
            """Extract numeric value from strings like 'GPA 3.74' or 'GRE 314'"""
            if not value_str:
                return None
            if isinstance(value_str, (int, float)):
                return float(value_str)
            if isinstance(value_str, str):
                # Remove prefix and extract number
                value_str = value_str.replace(prefix, '').strip()
                try:
                    return float(value_str)
                except ValueError:
                    return None
            return None

        def clean_string(value):
            """Remove NUL characters from strings to prevent PostgreSQL errors"""
            if isinstance(value, str):
                return value.replace('\x00', '').replace('\u0000', '')
            return value

        data_to_insert = []
        for r in records:
            # Detect which format we're dealing with
            is_new_format = 'applicant_status' in r or 'citizenship' in r or 'semester_year_start' in r

            if is_new_format:
                # NEW FORMAT HANDLING
                # Program is already combined in new format
                combined_program = r.get('program', '')

                # Comments
                comments = r.get('comments')

                # Date added
                date_added = parse_date(r.get('date_added'))

                # URL
                url = r.get('url')

                # Status
                status_map = {
                    'Accepted': 'Accepted',
                    'Rejected': 'Rejected',
                    'Interview': 'Interview',
                    'Wait listed': 'Wait listed',
                    'Waitlisted': 'Wait listed'
                }
                raw_status = r.get('applicant_status', '')
                status = status_map.get(raw_status, raw_status) if raw_status else None

                # Term
                term = r.get('semester_year_start')

                # Citizenship (us_or_international)
                citizenship_map = {
                    'American': 'American',
                    'International': 'International',
                    'U': 'American',
                    'I': 'International'
                }
                raw_citizenship = r.get('citizenship', '')
                us_or_international = citizenship_map.get(raw_citizenship, raw_citizenship) if raw_citizenship else None

                # GPA - extract from "GPA 3.74" format
                gpa = extract_numeric(r.get('gpa'), 'GPA')

                # GRE scores - extract from "GRE 314" format or handle direct numeric values
                gre = extract_numeric(r.get('gre'), 'GRE')

                # gre_v and gre_aw are already numeric or null in new format
                gre_v_raw = r.get('gre_v')
                gre_v = float(gre_v_raw) if isinstance(gre_v_raw, (int, float)) else None

                gre_aw_raw = r.get('gre_aw')
                gre_aw = float(gre_aw_raw) if isinstance(gre_aw_raw, (int, float)) else None

                # Degree
                degree = r.get('masters_or_phd')

                # LLM generated fields
                llm_program = r.get('llm-generated-program')
                llm_university = r.get('llm-generated-university')

            else:
                # OLD FORMAT HANDLING
                # Determine status and date_added
                acceptance_date = r.get('Acceptance Date')
                rejection_date = r.get('Rejection Date')

                if acceptance_date:
                    status = 'Accepted'
                    date_added = parse_date(acceptance_date)
                elif rejection_date:
                    status = 'Rejected'
                    date_added = parse_date(rejection_date)
                else:
                    status = None
                    date_added = None

                # Combine University and Program into single program field
                university = r.get('University', '')
                program_name = r.get('Program', '')
                if university and program_name:
                    combined_program = f"{university} - {program_name}"
                else:
                    combined_program = university or program_name

                # Comments
                comments = r.get('Notes')

                # URL
                url = r.get('Url')

                # Term
                term = r.get('Term')

                # Citizenship
                us_or_international = r.get('US/International')

                # GPA and GRE scores
                gpa = r.get('GPA') if isinstance(r.get('GPA'), (int, float)) else None
                gre_val = r.get('GRE General')
                gre = gre_val if isinstance(gre_val, (int, float)) else None
                gre_v_val = r.get('GRE Verbal')
                gre_v = gre_v_val if isinstance(gre_v_val, (int, float)) else None
                gre_aw_val = r.get('GRE Analytical Writing')
                gre_aw = gre_aw_val if isinstance(gre_aw_val, (int, float)) else None

                # Degree
                degree = r.get('Degree')

                # LLM generated fields
                llm_program = r.get('LLM Generated Program')
                llm_university = r.get('LLM Generated University')

            # Create row tuple with cleaned string values
            row = (
                clean_string(combined_program),
                clean_string(comments) if isinstance(comments, str) else None,
                date_added,
                clean_string(url) if isinstance(url, str) else None,
                clean_string(status),
                clean_string(term) if isinstance(term, str) else None,
                clean_string(us_or_international) if isinstance(us_or_international, str) else None,
                gpa,
                gre,
                gre_v,
                gre_aw,
                clean_string(degree) if isinstance(degree, str) else None,
                clean_string(llm_program),
                clean_string(llm_university),
                # Clean the JSON string to remove null bytes before storing
                json.dumps(r).replace('\x00', '').replace('\\u0000', '')
            )
            data_to_insert.append(row)

        # 5. Execute batch insert
        insert_query = """
            INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international,
                                       gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                                       llm_generated_university, raw_data)
            VALUES %s
        """
        execute_values(cur, insert_query, data_to_insert)

        conn.commit()
        print(f"Success! Total records imported: {len(records)}")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Error during import: {exc}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    # Support command line arguments: python load_data.py [dbname] [file_path]
    arg_dbname = sys.argv[1] if len(sys.argv) > 1 else None
    arg_file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if arg_dbname:
        print(f"Command line args - Database: {arg_dbname}, File: {arg_file_path or 'default'}")

    load_data(dbname=arg_dbname, file_path=arg_file_path)
