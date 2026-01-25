"""
Routes for the projects blueprint.
Displays projects and publications information.
"""

from flask import Blueprint, render_template

# Create blueprint for projects routes
projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


@projects_bp.route('/')
def projects():
    """
    Render the projects/publications page.
    Displays Module 1 project details and GitHub link.
    
    Returns:
        str: Rendered HTML template for projects page
    """
    return render_template('projects.html')
