Overview & Setup
================

Introduction
------------

The GradCafe Analysis Application is a Flask-based web application that provides analysis and insights from graduate school admissions data scraped from GradCafe. The application allows users to:

- View statistical analysis of admissions data
- Pull new data from GradCafe website
- Update analysis with the latest database information
- Query data across multiple metrics (GPA, GRE scores, acceptance rates, etc.)

Features
--------

* **Web Interface**: Clean, responsive UI for viewing analysis results
* **Data Scraping**: Automated scraping of GradCafe admissions data
* **Database Integration**: PostgreSQL backend for storing and querying data
* **Real-time Updates**: Background processing for data collection
* **Statistical Analysis**: Multiple queries covering key admissions metrics

Requirements
------------

System Requirements
~~~~~~~~~~~~~~~~~~~

- Python 3.8 or higher
- PostgreSQL 12 or higher
- 2GB RAM minimum
- Internet connection (for scraping)

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Install dependencies using pip:

.. code-block:: bash

   pip install -r requirements.txt

Required packages:
- Flask >= 2.0.0
- psycopg2-binary >= 2.9.0
- beautifulsoup4 >= 4.9.0
- lxml >= 4.6.0

Environment Variables
---------------------

The application uses the following environment variables:

DATABASE_URL
~~~~~~~~~~~~

PostgreSQL connection string. Format:

.. code-block:: bash

   export DATABASE_URL="postgresql://username@host/database_name"

**Default**: ``postgresql://fadetoblack@localhost/gradcafe_sample``

Running the Application
-----------------------

Development Mode
~~~~~~~~~~~~~~~~

1. Set up your database:

   .. code-block:: bash

      createdb gradcafe_sample
      python setup_databases.py

2. Start the Flask application:

   .. code-block:: bash

      cd module_4/src
      python app.py

3. Access the application at ``http://localhost:8080``

Production Mode
~~~~~~~~~~~~~~~

For production deployment, use a WSGI server like Gunicorn:

.. code-block:: bash

   gunicorn -w 4 -b 0.0.0.0:8080 app:app

Database Setup
--------------

The application requires PostgreSQL with the following database schema:

.. code-block:: sql

   CREATE TABLE gradcafe_main (
       p_id SERIAL PRIMARY KEY,
       program TEXT,
       comments TEXT,
       date_added DATE,
       url TEXT UNIQUE,
       status TEXT,
       term TEXT,
       us_or_international TEXT,
       gpa FLOAT,
       gre FLOAT,
       gre_v FLOAT,
       gre_aw FLOAT,
       degree TEXT,
       llm_generated_program TEXT,
       llm_generated_university TEXT,
       raw_data JSONB
   );

Use ``setup_databases.py`` to automatically create the required schema.

Running Tests
-------------

The test suite uses pytest. To run all tests:

.. code-block:: bash

   cd module_4
   pytest -m "web or buttons or analysis or db or integration"

To run tests with coverage:

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Troubleshooting
---------------

Database Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter connection errors:

1. Verify PostgreSQL is running: ``pg_isready``
2. Check your DATABASE_URL environment variable
3. Ensure the database exists: ``psql -l``
4. Verify user permissions

Port Already in Use
~~~~~~~~~~~~~~~~~~~

If port 8080 is already in use, modify in ``app.py``:

.. code-block:: python

   app.run(debug=True, port=8081)

Import Errors
~~~~~~~~~~~~~

Ensure you're running from the correct directory and Python path is set:

.. code-block:: bash

   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
