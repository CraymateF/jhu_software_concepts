from flask import Flask, render_template, jsonify, request
from query_data import run_all_queries
from data_updater import start_scraping, get_scraping_status

app = Flask(__name__)

# Database configuration mapping
DATABASE_INFO = {
    'gradcafe': {
        'name': 'gradcafe',
        'display_name': 'My Dataset (Module 2)',
        'file_path': 'module_2/llm_extend_applicant_data.json'
    },
    'gradcafe_sample': {
        'name': 'gradcafe_sample',
        'display_name': 'Provided Dataset (Module 3)',
        'file_path': 'module_3/sample_data/llm_extend_applicant_data.json'
    }
}

@app.route('/')
def index():
    """Display all query results on the main page"""
    # Get database name from query parameter, default to gradcafe_sample
    dbname = request.args.get('db', 'gradcafe_sample')
    
    # Validate database name
    if dbname not in DATABASE_INFO:
        dbname = 'gradcafe_sample'
    
    results = run_all_queries(dbname=dbname)
    scraping_status = get_scraping_status()
    
    return render_template('results.html', 
                         results=results, 
                         scraping_status=scraping_status,
                         current_db=dbname,
                         db_info=DATABASE_INFO)

@app.route('/pull_data', methods=['POST'])
def pull_data():
    """
    Endpoint to trigger data scraping from GradCafe
    This starts a background process to scrape and add new data
    """
    dbname = request.json.get('dbname', 'gradcafe_sample') if request.is_json else 'gradcafe_sample'
    max_pages = request.json.get('max_pages', 2) if request.is_json else 2
    
    # Validate database name
    if dbname not in DATABASE_INFO:
        dbname = 'gradcafe_sample'
    
    result = start_scraping(dbname=dbname, max_pages=max_pages)
    return jsonify(result)

@app.route('/scraping_status', methods=['GET'])
def scraping_status():
    """
    Endpoint to check the status of the scraping process
    """
    status = get_scraping_status()
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
