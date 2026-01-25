"""
Flask application factory and configuration.
Creates and configures the Flask app with blueprints.
"""

from flask import Flask


def create_app():
    """
    Application factory function.
    Creates and configures the Flask app instance.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Register blueprints
    from app.routes.home import home_bp
    from app.routes.contact import contact_bp
    from app.routes.projects import projects_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(projects_bp)
    
    return app
