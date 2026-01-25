"""
Routes for the contact blueprint.
Displays contact information including email and LinkedIn.
"""

from flask import Blueprint, render_template

# Create blueprint for contact routes
contact_bp = Blueprint('contact', __name__, url_prefix='/contact')


@contact_bp.route('/')
def contact():
    """
    Render the contact page.
    Displays email address and LinkedIn information.
    
    Returns:
        str: Rendered HTML template for contact page
    """
    return render_template('contact.html')
