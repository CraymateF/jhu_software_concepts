"""
Module to query GradCafe database and return analysis results.
"""
import os

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file (don't override existing vars for testing)
load_dotenv(override=False)

def get_db_connection(dbname=None):
    """
    Create and return a database connection using environment variables.
    Supports both DATABASE_URL and individual DB_* variables.
    """
    if dbname is None:
        dbname = os.getenv('DB_NAME', 'gradcafe_sample')

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
                # Use parameter dbname if provided, otherwise use URL dbname
                conn_params["dbname"] = dbname if dbname else url_db
            else:
                host_and_port = host_part
                conn_params["dbname"] = dbname if dbname else os.getenv('DB_NAME', 'gradcafe_sample')

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
                "dbname": dbname if dbname else os.getenv('DB_NAME', 'gradcafe_sample'),
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

    return psycopg2.connect(**conn_params)

def question_1(dbname=None):
    """How many entries do you have in your database who have applied for Fall 2026?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    # Use SQL composition for safe query construction
    query = sql.SQL("""
        SELECT COUNT(*) as count
        FROM {table}
        WHERE term = %s
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('Fall 2026',))
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('Fall 2026',)).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "How many entries do you have in your database who have applied for Fall 2026?",
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_2(dbname=None):
    """What percentage of entries are from international students (not American or Other)?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT
            ROUND(
                (COUNT(*) FILTER (WHERE us_or_international = %s) * 100.0 / NULLIF(COUNT(*), 0)),
                2
            ) as percentage
        FROM {table}
        WHERE us_or_international IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('International',))
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('International',)).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What percentage of entries are from international students?",
        "query": query_str.strip(),
        "answer": f"{result[0]}%" if result[0] is not None else "N/A"
    }

def question_3(dbname=None):
    """What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT
            ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa,
            ROUND(CAST(AVG(gre) AS NUMERIC), 2) as avg_gre,
            ROUND(CAST(AVG(gre_v) AS NUMERIC), 2) as avg_gre_v,
            ROUND(CAST(AVG(gre_aw) AS NUMERIC), 2) as avg_gre_aw
        FROM {table}
        WHERE gpa IS NOT NULL OR gre IS NOT NULL OR gre_v IS NOT NULL OR gre_aw IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query)
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?",
        "query": query_str.strip(),
        "answer": {
            "avg_gpa": result[0],
            "avg_gre": result[1],
            "avg_gre_v": result[2],
            "avg_gre_aw": result[3]
        }
    }

def question_4(dbname=None):
    """What is the average GPA of American students in Fall 2026?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa
        FROM {table}
        WHERE us_or_international = %s
        AND term = %s
        AND gpa IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('American', 'Fall 2026'))
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('American', 'Fall 2026')).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What is the average GPA of American students in Fall 2026?",
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_5(dbname=None):
    """What percent of entries for Fall 2026 are Acceptances?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT
            ROUND(
                (COUNT(*) FILTER (WHERE status = %s) * 100.0 / NULLIF(COUNT(*), 0)),
                2
            ) as percentage
        FROM {table}
        WHERE term = %s
        AND status IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('Accepted', 'Fall 2026'))
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('Accepted', 'Fall 2026')).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What percent of entries for Fall 2026 are Acceptances?",
        "query": query_str.strip(),
        "answer": f"{result[0]}%" if result[0] is not None else "N/A"
    }

def question_6(dbname=None):
    """What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa
        FROM {table}
        WHERE term = %s
        AND status = %s
        AND gpa IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('Fall 2026', 'Accepted'))
    result = cur.fetchone()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('Fall 2026', 'Accepted')).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?",
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_7(dbname=None):
    """
    How many entries are from applicants who applied to JHU
    for a masters degree in Computer Science?
    """
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT COUNT(*) as count
        FROM {table}
        WHERE (program ILIKE %s OR program ILIKE %s)
        AND (program ILIKE %s OR program ILIKE %s)
        AND (degree ILIKE %s OR degree ILIKE %s)
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(
        query,
        ('%Johns Hopkins%', '%JHU%', '%Computer Science%', '%CS%', '%MS%', '%Master%')
    )
    result = cur.fetchone()

    # Get query string before closing connection
    params = ('%Johns Hopkins%', '%JHU%', '%Computer Science%', '%CS%', '%MS%', '%Master%')
    query_str = cur.mogrify(query, params).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "How many entries are from applicants who applied to JHU for a masters degree in Computer Science?",
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_8(dbname=None):
    """
    How many entries from 2026 are acceptances from applicants who applied
    to Georgetown/MIT/Stanford/CMU for PhD in CS?
    """
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT COUNT(*) as count
        FROM {table}
        WHERE term ILIKE %s
        AND status = %s
        AND (
            program ILIKE %s OR
            program ILIKE %s OR
            program ILIKE %s OR
            program ILIKE %s
        )
        AND (program ILIKE %s OR program ILIKE %s)
        AND degree = %s
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(
        query,
        ('%2026%', 'Accepted', '%Georgetown%', '%MIT%', '%Stanford%',
         '%Carnegie Mellon%', '%Computer Science%', '%CS%', 'PhD')
    )
    result = cur.fetchone()

    # Get query string before closing connection
    params = ('%2026%', 'Accepted', '%Georgetown%', '%MIT%', '%Stanford%',
              '%Carnegie Mellon%', '%Computer Science%', '%CS%', 'PhD')
    query_str = cur.mogrify(query, params).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": (
            "How many entries from 2026 are acceptances for "
            "Georgetown/MIT/Stanford/CMU PhD in CS?"
        ),
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_9(dbname=None):
    """Do the numbers for question 8 change if you use LLM Generated Fields?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT COUNT(*) as count
        FROM {table}
        WHERE term ILIKE %s
        AND status = %s
        AND (
            llm_generated_university ILIKE %s OR
            llm_generated_university ILIKE %s OR
            llm_generated_university ILIKE %s OR
            llm_generated_university ILIKE %s
        )
        AND llm_generated_program ILIKE %s
        AND degree = %s
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(
        query,
        ('%2026%', 'Accepted', '%Georgetown%', '%MIT%', '%Stanford%',
         '%Carnegie Mellon%', '%Computer Science%', 'PhD')
    )
    result = cur.fetchone()

    # Get query string before closing connection
    params = ('%2026%', 'Accepted', '%Georgetown%', '%MIT%', '%Stanford%',
              '%Carnegie Mellon%', '%Computer Science%', 'PhD')
    query_str = cur.mogrify(query, params).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "Do the numbers change if you use LLM Generated Fields (Question 8 comparison)?",
        "query": query_str.strip(),
        "answer": result[0]
    }

def question_10(dbname=None):
    """
    Additional Question 1: What is the acceptance rate for PhD programs
    in Computer Science for Fall 2026?
    """
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    query = sql.SQL("""
        SELECT
            ROUND(
                (COUNT(*) FILTER (WHERE status = %s) * 100.0 / NULLIF(COUNT(*), 0)),
                2
            ) as acceptance_rate
        FROM {table}
        WHERE term = %s
        AND degree = %s
        AND (program ILIKE %s OR llm_generated_program ILIKE %s)
        AND status IS NOT NULL
        LIMIT 1
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(
        query,
        ('Accepted', 'Fall 2026', 'PhD', '%Computer Science%', '%Computer Science%')
    )
    result = cur.fetchone()

    # Get query string before closing connection
    params = ('Accepted', 'Fall 2026', 'PhD', '%Computer Science%', '%Computer Science%')
    query_str = cur.mogrify(query, params).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "What is the acceptance rate for PhD programs in Computer Science for Fall 2026?",
        "query": query_str.strip(),
        "answer": f"{result[0]}%" if result[0] is not None else "N/A"
    }

def question_11(dbname=None, max_limit=10):
    """
    Additional Question 2: Which university has the highest average GPA
    for accepted students?
    """
    conn = get_db_connection(dbname)
    cur = conn.cursor()

    # Enforce maximum limit between 1 and 100
    limit = max(1, min(max_limit, 100))

    query = sql.SQL("""
        SELECT
            llm_generated_university,
            ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa,
            COUNT(*) as num_acceptances
        FROM {table}
        WHERE status = %s
        AND gpa IS NOT NULL
        AND llm_generated_university IS NOT NULL
        GROUP BY llm_generated_university
        HAVING COUNT(*) >= 5
        ORDER BY avg_gpa DESC
        LIMIT %s
    """).format(
        table=sql.Identifier('gradcafe_main')
    )

    cur.execute(query, ('Accepted', limit))
    results = cur.fetchall()

    # Get query string before closing connection
    query_str = cur.mogrify(query, ('Accepted', limit)).decode('utf-8')

    cur.close()
    conn.close()

    return {
        "question": "Which universities have the highest average GPA for accepted students (min 5 accept ances)?",
        "query": query_str.strip(),
        "answer": results
    }

def run_all_queries(dbname=None):
    """Run all queries and return results"""
    results = {
        "q1": question_1(dbname),
        "q2": question_2(dbname),
        "q3": question_3(dbname),
        "q4": question_4(dbname),
        "q5": question_5(dbname),
        "q6": question_6(dbname),
        "q7": question_7(dbname),
        "q8": question_8(dbname),
        "q9": question_9(dbname),
        "q10": question_10(dbname),
        "q11": question_11(dbname)
    }
    return results

if __name__ == "__main__":
    print("Running all queries...\n")
    all_results = run_all_queries()

    for key, query_result in all_results.items():
        print(f"\n{'='*80}")
        print(f"QUESTION: {query_result['question']}")
        print(f"{'='*80}")
        # print(f"QUERY:\n{query_result['query']}")
        print(f"\nANSWER: {query_result['answer']}")
