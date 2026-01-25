"""
Portfolio website - old entry point
This file is kept for backwards compatibility.
Please use 'python run.py' to start the application.
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)

