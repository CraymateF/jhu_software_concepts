import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

def load_data():
    # 1. Database connection parameters
    conn_params = {
        "dbname": "gradcafe",
        "user": "fadetoblack", 
        "host": "localhost"
    }

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
        file_path = 'module_2/llm_extend_applicant_data.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        # 4. Prepare data for batch insertion
        print(f"Detected {len(records)} records. Starting import...")
        
        def parse_date(date_str):
            """Convert DD/MM/YYYY format to YYYY-MM-DD for PostgreSQL"""
            if not date_str or not isinstance(date_str, str):
                return None
            try:
                dt = datetime.strptime(date_str, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None
        
        data_to_insert = []
        for r in records:
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
            combined_program = f"{university} - {program_name}" if university and program_name else (university or program_name)
            
            # Extract key fields for easy querying, keep original JSON in raw_data
            row = (
                combined_program,
                r.get('Notes') if isinstance(r.get('Notes'), str) else None,
                date_added,
                r.get('Url') if isinstance(r.get('Url'), str) else None,
                status,
                r.get('Term') if isinstance(r.get('Term'), str) else None,
                r.get('US/International') if isinstance(r.get('US/International'), str) else None,
                r.get('GPA') if isinstance(r.get('GPA'), (int, float)) else None,
                r.get('GRE General') if isinstance(r.get('GRE General'), (int, float)) else None,
                r.get('GRE Verbal') if isinstance(r.get('GRE Verbal'), (int, float)) else None,
                r.get('GRE Analytical Writing') if isinstance(r.get('GRE Analytical Writing'), (int, float)) else None,
                r.get('Degree') if isinstance(r.get('Degree'), str) else None,
                r.get('LLM Generated Program'),
                r.get('LLM Generated University'),
                json.dumps(r)
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

    except Exception as e:
        print(f"Error during import: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    load_data()