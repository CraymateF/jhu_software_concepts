"""
Flask application for GradCafe database analysis and data management.

This application provides a web interface to:
- View analysis results from GradCafe admissions data
- Pull new data from GradCafe website
- Update analysis with latest data

The app uses dependency injection to allow testing with mock data sources.
"""
import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from query_data import run_all_queries
from data_updater import start_scraping, get_scraping_status

# Load environment variables from .env file
load_dotenv()

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

def create_app(query_func=None, scraper_func=None, status_func=None, config=None):
    """
    Application factory for creating Flask app instances.

    Args:
        query_func: Function to run queries (defaults to run_all_queries)
        scraper_func: Function to start scraping (defaults to start_scraping)
        status_func: Function to get status (defaults to get_scraping_status)
        config: Dictionary of configuration settings

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Apply configuration
    if config:
        app.config.update(config)

    # Use provided functions or defaults
    _query_func = query_func or run_all_queries
    _scraper_func = scraper_func or start_scraping
    _status_func = status_func or get_scraping_status

    @app.route('/')
    @app.route('/analysis')
    def index():
        """Display all query results on the main page (Analysis page)"""
        # Get database name from query parameter, default to gradcafe_sample
        dbname = request.args.get('db', 'gradcafe_sample')

        # Validate database name
        if dbname not in DATABASE_INFO:
            dbname = 'gradcafe_sample'

        results = _query_func(dbname=dbname)
        scraping_status = _status_func()

        return render_template('results.html',
                             results=results,
                             scraping_status=scraping_status,
                             current_db=dbname,
                             db_info=DATABASE_INFO)

    @app.route('/pull-data', methods=['POST'])
    @app.route('/pull_data', methods=['POST'])
    def pull_data():
        """
        Endpoint to trigger data scraping from GradCafe.
        Returns 409 if scraping is already in progress.
        """
        # Check if already busy
        status = _status_func()
        if status.get('is_running', False):
            return jsonify({"busy": True, "message": "Scraping already in progress"}), 409

        dbname = request.json.get('dbname', 'gradcafe_sample') if request.is_json else 'gradcafe_sample'
        max_pages = request.json.get('max_pages', 2) if request.is_json else 2

        # Validate database name
        if dbname not in DATABASE_INFO:
            dbname = 'gradcafe_sample'

        result = _scraper_func(dbname=dbname, max_pages=max_pages)
        return jsonify({"ok": True, **result}), 200

    @app.route('/update-analysis', methods=['POST'])
    def update_analysis():
        """
        Endpoint to update analysis (refresh the page with latest data).
        Returns 409 if scraping is in progress.
        """
        # Check if scraping is busy
        status = _status_func()
        if status.get('is_running', False):
            return jsonify({"busy": True, "message": "Cannot update while scraping in progress"}), 409

        # Simply return success - the frontend will reload the page
        return jsonify({"ok": True, "message": "Analysis ready to update"}), 200

    @app.route('/scraping_status', methods=['GET'])
    def scraping_status():
        """
        Endpoint to check the status of the scraping process
        """
        status = _status_func()
        return jsonify(status)

    return app

# Create default app instance for running directly
application = create_app()

if __name__ == '__main__':
    # Never use debug=True in production - use environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    application.run(debug=debug_mode, port=8080)
