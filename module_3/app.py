from flask import Flask, render_template, jsonify, request
from query_data import run_all_queries
from data_updater import start_scraping, get_scraping_status

app = Flask(__name__)

@app.route('/')
def index():
    """Display all query results on the main page"""
    results = run_all_queries()
    scraping_status = get_scraping_status()
    return render_template('results.html', results=results, scraping_status=scraping_status)

@app.route('/pull_data', methods=['POST'])
def pull_data():
    """
    Endpoint to trigger data scraping from GradCafe
    This starts a background process to scrape and add new data
    """
    max_pages = request.json.get('max_pages', 2) if request.is_json else 2
    result = start_scraping(max_pages=max_pages)
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
