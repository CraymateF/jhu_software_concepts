import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Create and return a database connection"""
    conn_params = {
        # "dbname": "gradcafe",
        "dbname": "gradcafe_sample",
        "user": "fadetoblack",
        "host": "localhost"
    }
    return psycopg2.connect(**conn_params)

def question_1():
    """How many entries do you have in your database who have applied for Fall 2026?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT COUNT(*) as count
        FROM gradcafe_main
        WHERE term = 'Fall 2026';
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "How many entries do you have in your database who have applied for Fall 2026?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_2():
    """What percentage of entries are from international students (not American or Other)?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            ROUND(
                (COUNT(*) FILTER (WHERE us_or_international = 'International') * 100.0 / COUNT(*)),
                2
            ) as percentage
        FROM gradcafe_main
        WHERE us_or_international IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What percentage of entries are from international students?",
        "query": query.strip(),
        "answer": f"{result[0]}%"
    }

def question_3():
    """What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa,
            ROUND(CAST(AVG(gre) AS NUMERIC), 2) as avg_gre,
            ROUND(CAST(AVG(gre_v) AS NUMERIC), 2) as avg_gre_v,
            ROUND(CAST(AVG(gre_aw) AS NUMERIC), 2) as avg_gre_aw
        FROM gradcafe_main
        WHERE gpa IS NOT NULL OR gre IS NOT NULL OR gre_v IS NOT NULL OR gre_aw IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?",
        "query": query.strip(),
        "answer": {
            "avg_gpa": result[0],
            "avg_gre": result[1],
            "avg_gre_v": result[2],
            "avg_gre_aw": result[3]
        }
    }

def question_4():
    """What is the average GPA of American students in Fall 2026?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa
        FROM gradcafe_main
        WHERE us_or_international = 'American'
        AND term = 'Fall 2026'
        AND gpa IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What is the average GPA of American students in Fall 2026?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_5():
    """What percent of entries for Fall 2026 are Acceptances?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            ROUND(
                (COUNT(*) FILTER (WHERE status = 'Accepted') * 100.0 / COUNT(*)),
                2
            ) as percentage
        FROM gradcafe_main
        WHERE term = 'Fall 2026'
        AND status IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What percent of entries for Fall 2026 are Acceptances?",
        "query": query.strip(),
        "answer": f"{result[0]}%"
    }

def question_6():
    """What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa
        FROM gradcafe_main
        WHERE term = 'Fall 2026'
        AND status = 'Accepted'
        AND gpa IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_7():
    """How many entries are from applicants who applied to JHU for a masters degree in Computer Science?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT COUNT(*) as count
        FROM gradcafe_main
        WHERE (program ILIKE '%Johns Hopkins%' OR program ILIKE '%JHU%')
        AND (program ILIKE '%Computer Science%' OR program ILIKE '%CS%')
        AND (degree ILIKE '%MS%' OR degree ILIKE '%Master%');
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "How many entries are from applicants who applied to JHU for a masters degree in Computer Science?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_8():
    """How many entries from 2026 are acceptances from applicants who applied to Georgetown/MIT/Stanford/CMU for PhD in CS?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT COUNT(*) as count
        FROM gradcafe_main
        WHERE term ILIKE '%2026%'
        AND status = 'Accepted'
        AND (
            program ILIKE '%Georgetown%' OR 
            program ILIKE '%MIT%' OR 
            program ILIKE '%Stanford%' OR 
            program ILIKE '%Carnegie Mellon%'
        )
        AND (program ILIKE '%Computer Science%' OR program ILIKE '%CS%')
        AND degree = 'PhD';
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "How many entries from 2026 are acceptances for Georgetown/MIT/Stanford/CMU PhD in CS?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_9():
    """Do the numbers for question 8 change if you use LLM Generated Fields?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT COUNT(*) as count
        FROM gradcafe_main
        WHERE term ILIKE '%2026%'
        AND status = 'Accepted'
        AND (
            llm_generated_university ILIKE '%Georgetown%' OR 
            llm_generated_university ILIKE '%MIT%' OR 
            llm_generated_university ILIKE '%Stanford%' OR 
            llm_generated_university ILIKE '%Carnegie Mellon%'
        )
        AND llm_generated_program ILIKE '%Computer Science%'
        AND degree = 'PhD';
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "Do the numbers change if you use LLM Generated Fields (Question 8 comparison)?",
        "query": query.strip(),
        "answer": result[0]
    }

def question_10():
    """Additional Question 1: What is the acceptance rate for PhD programs in Computer Science for Fall 2026?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            ROUND(
                (COUNT(*) FILTER (WHERE status = 'Accepted') * 100.0 / COUNT(*)),
                2
            ) as acceptance_rate
        FROM gradcafe_main
        WHERE term = 'Fall 2026'
        AND degree = 'PhD'
        AND (program ILIKE '%Computer Science%' OR llm_generated_program ILIKE '%Computer Science%')
        AND status IS NOT NULL;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "What is the acceptance rate for PhD programs in Computer Science for Fall 2026?",
        "query": query.strip(),
        "answer": f"{result[0]}%" if result[0] else "N/A"
    }

def question_11():
    """Additional Question 2: Which university has the highest average GPA for accepted students?"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            llm_generated_university,
            ROUND(CAST(AVG(gpa) AS NUMERIC), 2) as avg_gpa,
            COUNT(*) as num_acceptances
        FROM gradcafe_main
        WHERE status = 'Accepted'
        AND gpa IS NOT NULL
        AND llm_generated_university IS NOT NULL
        GROUP BY llm_generated_university
        HAVING COUNT(*) >= 5
        ORDER BY avg_gpa DESC
        LIMIT 10;
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        "question": "Which universities have the highest average GPA for accepted students (min 5 acceptances)?",
        "query": query.strip(),
        "answer": results
    }

def run_all_queries():
    """Run all queries and return results"""
    results = {
        "q1": question_1(),
        "q2": question_2(),
        "q3": question_3(),
        "q4": question_4(),
        "q5": question_5(),
        "q6": question_6(),
        "q7": question_7(),
        "q8": question_8(),
        "q9": question_9(),
        "q10": question_10(),
        "q11": question_11()
    }
    return results

if __name__ == "__main__":
    print("Running all queries...\n")
    results = run_all_queries()
    
    for key, result in results.items():
        print(f"\n{'='*80}")
        print(f"QUESTION: {result['question']}")
        print(f"{'='*80}")
        print(f"QUERY:\n{result['query']}")
        print(f"\nANSWER: {result['answer']}")
