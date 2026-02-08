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
    """Convert DD/MM/YYYY format to YYYY-MM-DD for PostgreSQL"""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

def get_existing_urls():
    """Get all URLs already in the database to avoid duplicates"""
    conn_params = {
        "dbname": "gradcafe",
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

def add_new_records_to_db(records):
    """Add new records to the database"""
    if not records:
        return 0
    
    conn_params = {
        "dbname": "gradcafe",
        "user": "fadetoblack",
        "host": "localhost"
    }
    
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
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

def scrape_and_update_background(max_pages=2):
    """
    Background function to scrape new data and update database
    This runs in a separate thread so it doesn't block the web server
    """
    global scraping_status
    
    temp_raw_file = 'module_3/temp_raw_data.json'
    temp_cleaned_file = 'module_3/temp_cleaned_data.json'
    temp_extended_file = 'module_3/temp_extended_data.json'
    
    try:
        scraping_status["is_running"] = True
        scraping_status["status_message"] = "Initializing scraper..."
        scraping_status["records_added"] = 0
        
        # Get existing URLs to avoid duplicates
        scraping_status["status_message"] = "Checking existing data..."
        existing_urls = get_existing_urls()
        
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
        scraping_status["status_message"] = f"Adding {len(new_records)} new records to database..."
        records_added = add_new_records_to_db(new_records)
        
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

def start_scraping(max_pages=2):
    """Start the scraping process in a background thread"""
    global scraping_status
    
    if scraping_status["is_running"]:
        return {"success": False, "message": "Scraping is already in progress"}
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_and_update_background, args=(max_pages,))
    thread.daemon = True
    thread.start()
    
    return {"success": True, "message": "Scraping started in background"}

def get_scraping_status():
    """Get current scraping status"""
    return scraping_status.copy()
