"""
Application entry point.
Starts the Flask web server on port 8080.
Run this file with: python run.py
"""

from app import create_app

if __name__ == '__main__':
    # Create the Flask application instance
    app = create_app()
    
    # Run the development server
    # Host: 0.0.0.0 allows external connections, localhost for local testing
    # Port: 8080 as specified in requirements
    # Debug: True for development, auto-reloads on code changes
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
