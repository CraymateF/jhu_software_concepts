================================================================================
FLASK PORTFOLIO WEBSITE - MODULE 1
================================================================================

PROJECT OVERVIEW:
This is a professional portfolio website built with Flask, featuring a modern
responsive design and clean code architecture. The application showcases a
homepage with bio and profile picture, contact information, and project
showcase capabilities.

================================================================================
REQUIREMENTS:
================================================================================

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

================================================================================
INSTALLATION INSTRUCTIONS:
================================================================================

1. CLONE THE REPOSITORY (if not already done):
   $ git clone https://github.com/yourusername/jhu_software_concepts.git
   $ cd module_1

2. CREATE A VIRTUAL ENVIRONMENT (recommended):
   
   On macOS/Linux:
   $ python3 -m venv venv
   $ source venv/bin/activate
   
   On Windows:
   $ python -m venv venv
   $ venv\Scripts\activate

3. INSTALL DEPENDENCIES:
   $ pip install -r requirements.txt

4. ADD YOUR PROFILE PICTURE:
   - Place your profile image in: app/static/images/profile.jpg
   - Supported formats: JPG, PNG, GIF
   - Recommended size: 350x350 pixels

5. CUSTOMIZE YOUR PORTFOLIO:
   Edit the following files with your information:
   
   - app/templates/home.html
     • Replace "Your Name" with your actual name
     • Replace "Your Position / Title" with your position
     • Update the bio section with your information
   
   - app/templates/contact.html
     • Replace email address with your actual email
     • Update LinkedIn profile URL
     • Update GitHub profile URL
     • Update phone number (optional)
   
   - app/templates/projects.html
     • Update project title and description
     • Update GitHub repository link
     • Add more project cards as needed

================================================================================
RUNNING THE APPLICATION:
================================================================================

Start the web server:
$ python run.py

The application will be available at:
- http://localhost:8080
- http://0.0.0.0:8080 (for network access)

The server runs in debug mode by default, which means:
- Code changes are automatically reloaded
- Detailed error messages are displayed
- Interactive debugger is available

To STOP the server:
Press Ctrl+C in the terminal

================================================================================
PROJECT STRUCTURE:
================================================================================

module_1/
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── README.txt                  # This file
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── home.py            # Homepage routes
│   │   ├── contact.py         # Contact page routes
│   │   └── projects.py        # Projects page routes
│   ├── templates/
│   │   ├── base.html          # Base template with navigation
│   │   ├── home.html          # Homepage template
│   │   ├── contact.html       # Contact page template
│   │   └── projects.html      # Projects page template
│   └── static/
│       ├── css/
│       │   └── style.css      # Main stylesheet
│       └── images/
│           └── profile.jpg    # Profile picture (add your own)

================================================================================
FEATURES:
================================================================================

✓ Multi-page application with Flask blueprints
✓ Navigation bar with active tab highlighting
✓ Responsive design (works on mobile, tablet, desktop)
✓ Professional color scheme
✓ HTML5 and CSS3 standards compliant
✓ Jinja2 template inheritance
✓ Clean and well-commented code
✓ Easy customization

================================================================================
NAVIGATION BAR:
================================================================================

The navigation bar appears at the top of every page and includes:
- Portfolio brand/logo
- Home link
- Contact link
- Projects link

The current page is highlighted in the navigation bar with a blue background.

================================================================================
TROUBLESHOOTING:
================================================================================

Q: Port 8080 is already in use
A: Change the port in run.py by modifying:
   app.run(host='0.0.0.0', port=8081, debug=True)
   Then access the site at http://localhost:8081

Q: Profile image not showing
A: Make sure you have placed the image at: app/static/images/profile.jpg
   Currently uses a placeholder if the file is missing.

Q: Template/CSS changes not appearing
A: Hard refresh the browser (Ctrl+F5 or Cmd+Shift+R)
   The server should auto-reload in debug mode.

Q: Import errors when running
A: Ensure you're in the virtual environment and all dependencies are installed:
   $ pip install -r requirements.txt

Q: Can't access from other machines
A: The app runs on 0.0.0.0, so it should be accessible from other machines.
   Try: http://<your-machine-ip>:8080

================================================================================
CUSTOMIZATION GUIDE:
================================================================================

1. CHANGE COLOR SCHEME:
   Edit app/static/css/style.css and modify the :root CSS variables:
   - --primary-color: Main text color
   - --secondary-color: Highlight/button color
   - --accent-color: Hover/emphasis color
   - --nav-bg: Navigation bar background

2. ADD MORE PAGES:
   a) Create a new blueprint in app/routes/newpage.py
   b) Create a new template in app/templates/newpage.html
   c) Register the blueprint in app/__init__.py
   d) Add navigation links in app/templates/base.html

3. MODIFY STYLING:
   All styling is in app/static/css/style.css
   Use CSS comments to organize sections

4. UPDATE CONTENT:
   All text content is in the HTML templates
   No backend changes needed for content updates

================================================================================
DEPLOYMENT:
================================================================================

For production deployment:
1. Set debug=False in run.py
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Set up proper environment variables
4. Use a reverse proxy (Nginx, Apache)
5. Configure SSL/TLS for HTTPS

Example with Gunicorn:
$ pip install gunicorn
$ gunicorn -w 4 -b 0.0.0.0:8080 'app:create_app()'

================================================================================
SUPPORT & RESOURCES:
================================================================================

Flask Documentation: https://flask.palletsprojects.com/
Jinja2 Documentation: https://jinja.palletsprojects.com/
CSS Guide: https://developer.mozilla.org/en-US/docs/Web/CSS/
Python 3 Documentation: https://docs.python.org/3/

================================================================================
AUTHOR:
================================================================================

Created as a Module 1 project for JHU Software Concepts course.

================================================================================
