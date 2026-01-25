"""
Routes for the home/homepage blueprint.
Displays the user's homepage with bio and profile picture.
"""

from flask import Blueprint, render_template

# Create blueprint for home routes
home_bp = Blueprint('home', __name__, url_prefix='/')


@home_bp.route('/')
@home_bp.route('/home')
def index():
    """
    Render the homepage.
    Displays user's name, position, bio, and profile picture.
    
    Returns:
        str: Rendered HTML template for homepage
    """
    return render_template('home.html')
