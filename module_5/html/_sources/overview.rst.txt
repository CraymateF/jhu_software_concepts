Overview & Setup
================

Introduction
------------

The GradCafe Analysis Application is a Flask-based web application that provides analysis and insights from graduate school admissions data scraped from GradCafe. The application allows users to:

- View statistical analysis of admissions data (11 analytical queries)
- Pull new data from GradCafe website (automated scraping)
- Update analysis with the latest database information
- Query data across multiple metrics (GPA, GRE scores, acceptance rates, universities)

Features
--------

* **Web Interface**: Clean, responsive UI with AJAX-powered controls
* **Data Scraping**: Automated scraping with BeautifulSoup4
* **ETL Pipeline**: Extract, Transform, Load with data cleaning and validation
* **Database Integration**: PostgreSQL with JSONB support
* **Real-time Updates**: Background processing with status tracking
* **Statistical Analysis**: 11 queries covering key admissions metrics
* **100% Test Coverage**: Comprehensive test suite with pytest

Project Structure
-----------------

.. code-block:: text

   module_4/
   ├── src/                     # Application source code
   │   ├── app.py              # Flask application factory
   │   ├── query_data.py       # Database queries
   │   ├── data_updater.py     # Scraping orchestration
   │   ├── load_data.py        # Batch data loader
   │   ├── setup_databases.py  # Database schema setup
   │   ├── module_2_code/      # ETL modules from Module 2
   │   │   ├── scrape.py       # GradCafe scraper
   │   │   └── clean.py        # Data cleaning
   │   ├── templates/          # Jinja2 templates
   │   └── static/             # CSS, JS, images
   ├── tests/                   # Test suite (100% coverage)
   │   ├── conftest.py         # Shared fixtures
   │   ├── test_flask_page.py  # Web tests
   │   ├── test_buttons.py     # Button tests
   │   ├── test_analysis_format.py
   │   ├── test_db_insert.py
   │   ├── test_integration_end_to_end.py
   │   ├── test_data_updater_complete.py
   │   ├── test_load_data_complete.py
   │   ├── test_query_connection.py
   │   └── test_final_coverage.py
   ├── docs/                    # Sphinx documentation
   ├── pytest.ini              # Pytest configuration
   ├── requirements.txt        # Python dependencies
   └── README.md               # Project overview

Requirements
------------

System Requirements
~~~~~~~~~~~~~~~~~~~

- **Python**: 3.8 or higher (tested with 3.13.2)
- **PostgreSQL**: 12 or higher
- **Memory**: 2GB RAM minimum
- **Network**: Internet connection required for scraping
- **OS**: macOS, Linux, or Windows with WSL

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Install all dependencies using pip:

.. code-block:: bash

   cd module_4
   pip install -r requirements.txt

Core packages:

- **Flask** >= 3.0.0 - Web framework
- **psycopg2-binary** >= 2.9.0 - PostgreSQL adapter
- **beautifulsoup4** >= 4.9.0 - HTML parsing for scraping
- **lxml** >= 4.6.0 - XML/HTML parser backend
- **requests** >= 2.31.0 - HTTP library

Development packages:

- **pytest** >= 9.0.0 - Testing framework
- **pytest-cov** >= 7.0.0 - Coverage reporting
- **pytest-mock** >= 3.12.0 - Mocking support

Environment Variables
---------------------

The application uses the following environment variables:

DATABASE_URL (Optional)
~~~~~~~~~~~~~~~~~~~~~~~

PostgreSQL connection string. Format:

.. code-block:: bash

   export DATABASE_URL="postgresql://username@host/database_name"

**Default**: ``postgresql://fadetoblack@localhost/gradcafe_sample``

**Usage in code**:

.. code-block:: python

   import os
   db_url = os.getenv('DATABASE_URL', 'postgresql://user@localhost/dbname')

PYTHONPATH (Optional)
~~~~~~~~~~~~~~~~~~~~~~

Add src directory to Python path:

.. code-block:: bash

   export PYTHONPATH="${PYTHONPATH}:$(pwd)/module_4/src"

FLASK_ENV (Optional)
~~~~~~~~~~~~~~~~~~~~~

Set development or production mode:

.. code-block:: bash

   export FLASK_ENV=development  # Enable debug mode
   export FLASK_ENV=production   # Disable debug mode

Quick Start
-----------

1. **Clone and Install**:

   .. code-block:: bash

      git clone <repository-url>
      cd jhu_software_concepts/module_4
      pip install -r requirements.txt

2. **Set up PostgreSQL**:

   .. code-block:: bash

      # Create databases
      createdb gradcafe_sample
      createdb gradcafe_test  # For testing

      # Initialize schema
      cd src
      python setup_databases.py

3. **Load sample data** (optional):

   .. code-block:: bash

      python load_data.py gradcafe_sample sample_data/llm_extend_applicant_data.json

4. **Run the application**:

   .. code-block:: bash

      python app.py

5. **Access the web interface**:

   Open ``http://localhost:8080`` in your browser

Running the Application
-----------------------

Development Mode
~~~~~~~~~~~~~~~~

**Step 1**: Set up your database:

.. code-block:: bash

   createdb gradcafe_sample
   cd module_4/src
   python setup_databases.py

**Step 2**: (Optional) Set environment variables:

.. code-block:: bash

   export DATABASE_URL="postgresql://username@localhost/gradcafe_sample"
   export FLASK_ENV=development

**Step 3**: Start the Flask application:

.. code-block:: bash

   python app.py

You should see:

.. code-block:: text

   * Running on http://127.0.0.1:8080
   * Debug mode: on

**Step 4**: Access the application at ``http://localhost:8080``

Production Mode
~~~~~~~~~~~~~~~

For production deployment, use a WSGI server like Gunicorn:

.. code-block:: bash

   # Install Gunicorn
   pip install gunicorn

   # Run with 4 worker processes
   cd module_4/src
   gunicorn -w 4 -b 0.0.0.0:8080 app:app

   # Or with timeout settings
   gunicorn -w 4 -b 0.0.0.0:8080 --timeout 120 app:app

**Production checklist**:

- Set ``FLASK_ENV=production``
- Use a reverse proxy (nginx/Apache)
- Enable HTTPS
- Configure logging
- Set up monitoring
- Use connection pooling for database

Database Setup
--------------

The application requires PostgreSQL with the following database schema:

**gradcafe_main** table structure:

.. code-block:: sql

   CREATE TABLE gradcafe_main (
       p_id SERIAL PRIMARY KEY,
       program TEXT,
       comments TEXT,
       date_added DATE,
       url TEXT UNIQUE,          -- Ensures idempotency
       status TEXT,              -- Accepted/Rejected/Interview/Wait listed
       term TEXT,                -- e.g., "Fall 2026"
       us_or_international TEXT,
       gpa FLOAT,
       gre FLOAT,
       gre_v FLOAT,
       gre_aw FLOAT,
       degree TEXT,              -- PhD/Masters
       llm_generated_program TEXT,
       llm_generated_university TEXT,
       raw_data JSONB            -- Original JSON data
   );

**Automatic Setup**:

Use ``setup_databases.py`` to automatically create the required schema:

.. code-block:: bash

   cd module_4/src
   python setup_databases.py

This creates both ``gradcafe_sample`` (production) and ``gradcafe_test`` (testing) databases.

Running Tests
-------------

The test suite uses pytest with 100% code coverage requirement.

Run All Tests
~~~~~~~~~~~~~

Execute the entire test suite (100 tests):

.. code-block:: bash

   cd module_4
   pytest -m "web or buttons or analysis or db or integration"

**Expected output**:

.. code-block:: text

   100 passed in 1.77s
   Required test coverage of 100% reached. Total coverage: 100.00%

Run with Coverage Report
~~~~~~~~~~~~~~~~~~~~~~~~

Generate detailed coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Generate HTML coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=html
   open htmlcov/index.html  # macOS
   # or
   xdg-open htmlcov/index.html  # Linux

Run Specific Test Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest -m web           # Web interface tests (5 tests)
   pytest -m buttons       # Button functionality (7 tests)
   pytest -m analysis      # Analysis formatting (4 tests)
   pytest -m db            # Database operations (25+ tests)
   pytest -m integration   # End-to-end flows (4 tests)

Verbose Output
~~~~~~~~~~~~~~

For detailed test output:

.. code-block:: bash

   pytest -v -m "web or buttons or analysis or db or integration"

Troubleshooting
---------------

Database Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter connection errors:

1. **Verify PostgreSQL is running**:

   .. code-block:: bash

      pg_isready
      # Expected: /tmp:5432 - accepting connections

2. **Check your DATABASE_URL** environment variable:

   .. code-block:: bash

      echo $DATABASE_URL

3. **Ensure the database exists**:

   .. code-block:: bash

      psql -l | grep gradcafe

4. **Verify user permissions**:

   .. code-block:: bash

      psql gradcafe_sample
      # Should connect without errors

5. **Test connection with Python**:

   .. code-block:: python

      import psycopg2
      conn = psycopg2.connect(
          dbname="gradcafe_sample",
          user="yourusername",
          host="localhost"
      )
      conn.close()
      print("Connection successful!")

Port Already in Use
~~~~~~~~~~~~~~~~~~~

If port 8080 is already in use, modify in ``app.py``:

.. code-block:: python

   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=8081)  # Change port

Import Errors
~~~~~~~~~~~~~

Ensure you're running from the correct directory and Python path is set:

.. code-block:: bash

   cd module_4/src
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python app.py

Test Database Missing
~~~~~~~~~~~~~~~~~~~~~

If tests fail with "database does not exist":

.. code-block:: bash

   createdb gradcafe_test
   # Tests will create the schema automatically

Scraping Fails
~~~~~~~~~~~~~~

If scraping encounters errors:

1. **Check internet connection**
2. **Verify GradCafe is accessible**: Visit https://www.thegradcafe.com/
3. **Check robots.txt compliance**: The scraper respects robots.txt
4. **Rate limiting**: The scraper includes delays between requests

Useful Commands
---------------

Database Management
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all databases
   psql -l

   # Connect to database
   psql gradcafe_sample

   # Count records
   psql gradcafe_sample -c "SELECT COUNT(*) FROM gradcafe_main;"

   # Drop and recreate database
   dropdb gradcafe_sample
   createdb gradcafe_sample
   python setup_databases.py

Development Workflow
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Activate virtual environment
   source .venv/bin/activate

   # Run tests before committing
   pytest -m "web or buttons or analysis or db or integration"

   # Check coverage
   pytest --cov=src --cov-report=term

   # Run Flask in debug mode
   cd src && python app.py

   # Load fresh data
   python load_data.py gradcafe_sample sample_data/llm_extend_applicant_data.json

Next Steps
----------

After installation:

1. Read the :doc:`architecture` guide to understand system design
2. Explore the :doc:`api` reference for module documentation
3. Review the :doc:`testing` guide for test development
4. Check ``README.md`` for assignment-specific requirements
