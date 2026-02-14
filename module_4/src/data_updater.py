"""
Module to handle data scraping and database updates
Uses existing module_2_code for scraping and cleaning
"""
import json
import sys
import os
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import threading

# Add module_2_code to path to import scraper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module_2_code'))

from scrape import GradCafeScraper
from clean import GradCafeDataCleaner, apply_llm_standardization

# Global variable to track scraping status
scraping_status = {
    "is_running": False,
    "last_run": None,
    "status_message": "Ready",
    "records_added": 0
}

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

def get_existing_urls(dbname='gradcafe'):
    """Get all URLs already in the database to avoid duplicates"""
    conn_params = {
        "dbname": dbname,
        "user": "fadetoblack",
        "host": "localhost"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT url FROM gradcafe_main WHERE url IS NOT NULL;")
        existing_urls = set(row[0] for row in cur.fetchall())
        cur.close()
        conn.close()
        return existing_urls
    except Exception as e:
        print(f"Error getting existing URLs: {e}")
        return set()

def add_new_records_to_db(records, dbname='gradcafe'):
    """Add new records to the database"""
    if not records:
        return 0
    
    conn_params = {
        "dbname": dbname,
        "user": "fadetoblack",
        "host": "localhost"
    }
    
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
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
                # OLD FORMAT HANDLING (from scraper - default)
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
                gre = r.get('GRE General') if isinstance(r.get('GRE General'), (int, float)) else None
                gre_v = r.get('GRE Verbal') if isinstance(r.get('GRE Verbal'), (int, float)) else None
                gre_aw = r.get('GRE Analytical Writing') if isinstance(r.get('GRE Analytical Writing'), (int, float)) else None
                
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
        
        # Execute batch insert
        insert_query = """
            INSERT INTO gradcafe_main (program, comments, date_added, url, status, term, us_or_international, 
                                       gpa, gre, gre_v, gre_aw, degree, llm_generated_program, 
                                       llm_generated_university, raw_data)
            VALUES %s
        """
        execute_values(cur, insert_query, data_to_insert)
        
        conn.commit()
        records_added = len(records)
        cur.close()
        conn.close()
        return records_added
        
    except Exception as e:
        print(f"Error adding records to database: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def scrape_and_update_background(dbname='gradcafe', max_pages=2):
    """
    Background function to scrape new data and update database
    This runs in a separate thread so it doesn't block the web server
    """
    global scraping_status
    
    # Use absolute paths based on the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_raw_file = os.path.join(script_dir, 'temp_raw_data.json')
    temp_cleaned_file = os.path.join(script_dir, 'temp_cleaned_data.json')
    temp_extended_file = os.path.join(script_dir, 'temp_extended_data.json')
    
    try:
        scraping_status["is_running"] = True
        scraping_status["status_message"] = f"Initializing scraper for {dbname}..."
        scraping_status["records_added"] = 0
        
        # Get existing URLs to avoid duplicates
        scraping_status["status_message"] = "Checking existing data..."
        existing_urls = get_existing_urls(dbname=dbname)
        
        # Scrape new data
        scraping_status["status_message"] = f"Scraping GradCafe (up to {max_pages} pages)..."
        scraper = GradCafeScraper()
        raw_data = scraper.scrape_data(max_pages=max_pages)
        
        if not raw_data:
            scraping_status["status_message"] = "No data found from scraper"
            scraping_status["is_running"] = False
            return
        
        # Save raw data temporarily
        with open(temp_raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        
        # Clean the data using module_2_code
        scraping_status["status_message"] = "Cleaning scraped data..."
        cleaner = GradCafeDataCleaner()
        cleaned_data = cleaner.clean_data(temp_raw_file, output_file=temp_cleaned_file)
        
        if not cleaned_data:
            scraping_status["status_message"] = "No data after cleaning"
            scraping_status["is_running"] = False
            return
        
        # Extend with LLM data using module_2_code
        scraping_status["status_message"] = "Enhancing with LLM analysis..."
        success = apply_llm_standardization(temp_cleaned_file, output_file=temp_extended_file)
        
        if not success:
            scraping_status["status_message"] = "LLM standardization failed, using cleaned data"
            extended_data = cleaned_data
        else:
            with open(temp_extended_file, 'r', encoding='utf-8') as f:
                extended_data = json.load(f)
        
        # Filter out existing URLs
        scraping_status["status_message"] = "Filtering for new entries..."
        new_records = [r for r in extended_data if r.get('Url') not in existing_urls]
        
        if not new_records:
            scraping_status["status_message"] = "No new records found (all URLs already in database)"
            scraping_status["is_running"] = False
            scraping_status["last_run"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Clean up temp files
            for temp_file in [temp_raw_file, temp_cleaned_file, temp_extended_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return
        
        # Add to database
        scraping_status["status_message"] = f"Adding {len(new_records)} new records to {dbname}..."
        records_added = add_new_records_to_db(new_records, dbname=dbname)
        
        scraping_status["records_added"] = records_added
        scraping_status["status_message"] = f"Successfully added {records_added} new records!"
        scraping_status["last_run"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean up temp files
        for temp_file in [temp_raw_file, temp_cleaned_file, temp_extended_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
    except Exception as e:
        scraping_status["status_message"] = f"Error: {str(e)}"
        print(f"Scraping error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraping_status["is_running"] = False

def start_scraping(dbname='gradcafe', max_pages=2):
    """Start the scraping process in a background thread"""
    global scraping_status
    
    if scraping_status["is_running"]:
        return {"success": False, "message": "Scraping is already in progress"}
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_and_update_background, args=(dbname, max_pages))
    thread.daemon = True
    thread.start()
    
    return {"success": True, "message": f"Scraping started in background for {dbname}"}

def get_scraping_status():
    """Get current scraping status"""
    return scraping_status.copy()
