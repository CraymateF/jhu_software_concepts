"""
Module to query GradCafe database and return analysis results.
Adapted for Docker environment – uses DATABASE_URL for connections.
"""
import os
import re

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv(override=False)


def get_db_connection(dbname=None):
    """
    Create a psycopg2 connection.
    Prefers DATABASE_URL env var; falls back to individual DB_* vars.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if dbname:
            database_url = re.sub(r"(/[^/?]+)(\?.*)?$", f"/{dbname}\\2", database_url)
        return psycopg2.connect(database_url)

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


def _run_query(dbname, query_template, params=()):
    """Execute a query and return the first row."""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    q = sql.SQL(query_template).format(table=sql.Identifier("gradcafe_main"))
    cur.execute(q, params)
    result = cur.fetchone()
    query_str = cur.mogrify(q, params).decode("utf-8")
    cur.close()
    conn.close()
    return result, query_str


def question_1(dbname=None):
    """How many entries have applied for Fall 2026?"""
    result, query_str = _run_query(
        dbname,
        "SELECT COUNT(*) FROM {table} WHERE term = %s",
        ("Fall 2026",),
    )
    return {
        "question": "How many entries do you have in your database who have applied for Fall 2026?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_2(dbname=None):
    """What percentage of entries are from international students?"""
    result, query_str = _run_query(
        dbname,
        """SELECT ROUND((COUNT(*) FILTER (WHERE us_or_international = %s) * 100.0
                         / NULLIF(COUNT(*), 0)), 2)
           FROM {table}
           WHERE us_or_international IS NOT NULL""",
        ("International",),
    )
    return {
        "question": "What percentage of entries are from international students?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_3(dbname=None):
    """What are the average GPA and GRE scores for accepted students?"""
    result, query_str = _run_query(
        dbname,
        """SELECT ROUND(AVG(gpa)::numeric, 2),
                  ROUND(AVG(gre)::numeric, 2),
                  ROUND(AVG(gre_v)::numeric, 2),
                  ROUND(AVG(gre_aw)::numeric, 2)
           FROM {table}
           WHERE status = %s""",
        ("Accepted",),
    )
    if result:
        return {
            "question": "What are the average GPA and GRE scores for accepted applicants?",
            "query": query_str.strip(),
            "answer": {
                "avg_gpa": result[0],
                "avg_gre": result[1],
                "avg_gre_v": result[2],
                "avg_gre_aw": result[3],
            },
        }
    return {
        "question": "What are the average GPA and GRE scores for accepted applicants?",
        "query": query_str.strip(),
        "answer": {"avg_gpa": None, "avg_gre": None, "avg_gre_v": None, "avg_gre_aw": None},
    }


def question_4(dbname=None):
    """What is the highest GPA among accepted applicants?"""
    result, query_str = _run_query(
        dbname,
        "SELECT MAX(gpa) FROM {table} WHERE status = %s",
        ("Accepted",),
    )
    return {
        "question": "What is the highest GPA among accepted applicants?",
        "query": query_str.strip(),
        "answer": result[0] if result else None,
    }


def question_5(dbname=None):
    """What is the most common application status?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    q = sql.SQL(
        "SELECT status, COUNT(*) AS cnt FROM {table} WHERE status IS NOT NULL "
        "GROUP BY status ORDER BY cnt DESC LIMIT 1"
    ).format(table=sql.Identifier("gradcafe_main"))
    cur.execute(q)
    result = cur.fetchone()
    query_str = cur.mogrify(q).decode("utf-8")
    cur.close()
    conn.close()
    return {
        "question": "What is the most common application status?",
        "query": query_str.strip(),
        "answer": f"{result[0]} ({result[1]} entries)" if result else "N/A",
    }


def question_6(dbname=None):
    """What is the average GPA of rejected applicants?"""
    result, query_str = _run_query(
        dbname,
        "SELECT ROUND(AVG(gpa)::numeric, 2) FROM {table} WHERE status = %s",
        ("Rejected",),
    )
    return {
        "question": "What is the average GPA of rejected applicants?",
        "query": query_str.strip(),
        "answer": result[0] if result else None,
    }


def question_7(dbname=None):
    """How many entries are PhD applicants?"""
    result, query_str = _run_query(
        dbname,
        "SELECT COUNT(*) FROM {table} WHERE degree ILIKE %s",
        ("%PhD%",),
    )
    return {
        "question": "How many entries are PhD applicants?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_8(dbname=None):
    """How many CS-related program acceptances are there?"""
    result, query_str = _run_query(
        dbname,
        "SELECT COUNT(*) FROM {table} WHERE status = %s AND program ILIKE %s",
        ("Accepted", "%Computer Science%"),
    )
    return {
        "question": "How many Computer Science program acceptances are there?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_9(dbname=None):
    """How many total CS applications are there using original program text aliases?"""
    result, query_str = _run_query(
        dbname,
        """SELECT COUNT(*)
           FROM {table}
           WHERE (
                 program ILIKE %s OR
                 program ILIKE %s OR
                 program ILIKE %s OR
                 program ILIKE %s OR
                 program ILIKE %s
             )""",
        (
            "%Computer Science%",
            "%Comp Sci%",
            "% CS %",
            "%Software Engineering%",
            "%Informatics%",
        ),
    )
    return {
        "question": "What is the total number of CS applications?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_10(dbname=None):
    """What is the total number of records in the database?"""
    result, query_str = _run_query(dbname, "SELECT COUNT(*) FROM {table}")
    return {
        "question": "What is the total number of records in the database?",
        "query": query_str.strip(),
        "answer": result[0] if result else 0,
    }


def question_11(dbname=None):
    """Which universities have the highest average GPA for acceptances?"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    q = sql.SQL(
        """SELECT
                  CASE WHEN llm_generated_university = LOWER(llm_generated_university)
                       THEN INITCAP(llm_generated_university)
                       ELSE llm_generated_university
                  END AS university_name,
                  ROUND(AVG(gpa)::numeric, 2) AS avg_gpa,
                  COUNT(*) AS acceptances
           FROM {table}
           WHERE status = 'Accepted'
             AND llm_generated_university IS NOT NULL
             AND gpa IS NOT NULL
           GROUP BY university_name
           ORDER BY avg_gpa DESC
           LIMIT 10"""
    ).format(table=sql.Identifier("gradcafe_main"))
    cur.execute(q)
    rows = cur.fetchall()
    query_str = cur.mogrify(q).decode("utf-8")
    cur.close()
    conn.close()
    return {
        "question": "Which universities have the highest average GPA among accepted applicants?",
        "query": query_str.strip(),
        "answer": rows,
    }


def run_all_queries(dbname=None):
    """Run all analysis queries and return results dict."""
    if dbname is None:
        dbname = os.getenv("DB_NAME", "gradcafe")
    return {
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
        "q11": question_11(dbname),
    }
