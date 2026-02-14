API Reference
=============

This section provides detailed API documentation for the main modules of the GradCafe Analysis Application.

Flask Application (app.py)
---------------------------

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance:

Application Factory
~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.create_app

Route Handlers
~~~~~~~~~~~~~~

The following routes are available:

**GET /** or **GET /analysis**
   Display the main analysis page with all query results.
   
   **Query Parameters**:
   
   - ``db`` (optional): Database name (default: ``gradcafe_sample``)
   
   **Returns**: HTML page with analysis results

**POST /pull-data** or **POST /pull_data**
   Trigger data scraping from GradCafe.
   
   **Request Body** (JSON):
   
   .. code-block:: json
   
      {
        "dbname": "gradcafe_sample",
        "max_pages": 2
      }
   
   **Responses**:
   
   - ``200 OK``: Scraping started successfully
   
     .. code-block:: json
     
        {
          "ok": true,
          "status": "started",
          "message": "Scraping initiated"
        }
   
   - ``409 Conflict``: Scraping already in progress
   
     .. code-block:: json
     
        {
          "busy": true,
          "message": "Scraping already in progress"
        }

**POST /update-analysis**
   Request to update analysis (refresh page with latest data).
   
   **Responses**:
   
   - ``200 OK``: Ready to update
   
     .. code-block:: json
     
        {
          "ok": true,
          "message": "Analysis ready to update"
        }
   
   - ``409 Conflict``: Scraping in progress, cannot update
   
     .. code-block:: json
     
        {
          "busy": true,
          "message": "Cannot update while scraping in progress"
        }

**GET /scraping_status**
   Check the current status of scraping operations.
   
   **Response** (JSON):
   
   .. code-block:: json
   
      {
        "is_running": false,
        "status_message": "Ready",
        "last_run": "2026-02-14T10:30:00",
        "records_added": 25
      }

Query Module (query_data.py)
-----------------------------

.. automodule:: query_data
   :members:
   :undoc-members:
   :show-inheritance:

Database Connection
~~~~~~~~~~~~~~~~~~~

.. autofunction:: query_data.get_db_connection

Query Functions
~~~~~~~~~~~~~~~

All query functions follow a consistent pattern and return a dictionary with:

- ``question``: The question being answered
- ``query``: The SQL query executed
- ``answer``: The result (format varies by question)

.. autofunction:: query_data.question_1

   **Returns**:
   
   .. code-block:: python
   
      {
        "question": "How many entries do you have in your database who have applied for Fall 2026?",
        "query": "SELECT COUNT(*) as count FROM gradcafe_main WHERE term = 'Fall 2026';",
        "answer": 150
      }

.. autofunction:: query_data.question_2

   **Returns**:
   
   .. code-block:: python
   
      {
        "question": "What percentage of entries are from international students?",
        "query": "SELECT ROUND(...) FROM gradcafe_main...",
        "answer": "45.67%"
      }

.. autofunction:: query_data.question_3

   **Returns**:
   
   .. code-block:: python
   
      {
        "question": "What is the average GPA, GRE, GRE V, GRE AW of applicants?",
        "query": "SELECT AVG(gpa)...",
        "answer": {
          "avg_gpa": 3.65,
          "avg_gre": 318.5,
          "avg_gre_v": 159.0,
          "avg_gre_aw": 4.2
        }
      }

.. autofunction:: query_data.question_4
.. autofunction:: query_data.question_5
.. autofunction:: query_data.question_6
.. autofunction:: query_data.question_7
.. autofunction:: query_data.question_8
.. autofunction:: query_data.question_9
.. autofunction:: query_data.question_10
.. autofunction:: query_data.question_11

.. autofunction:: query_data.run_all_queries

   Executes all query functions and returns a dictionary:
   
   .. code-block:: python
   
      {
        "q1": {...},
        "q2": {...},
        ...
        "q11": {...}
      }

Data Loader (load_data.py)
---------------------------

.. automodule:: load_data
   :members:
   :undoc-members:
   :show-inheritance:

Main Functions
~~~~~~~~~~~~~~

.. autofunction:: load_data.load_data

   Loads data from JSON file into PostgreSQL database.
   
   **Parameters**:
   
   - ``dbname`` (str): Target database name
   - ``file_path`` (str): Path to JSON data file
   
   **Process**:
   
   1. Drops and recreates ``gradcafe_main`` table
   2. Parses JSON file (supports both JSON array and JSONL)
   3. Transforms data to match schema
   4. Batch inserts using ``execute_values``

Data Updater (data_updater.py)
-------------------------------

.. automodule:: data_updater
   :members:
   :undoc-members:
   :show-inheritance:

Main Functions
~~~~~~~~~~~~~~

.. autofunction:: data_updater.start_scraping

   Starts background scraping thread.
   
   **Parameters**:
   
   - ``dbname`` (str): Target database
   - ``max_pages`` (int): Maximum pages to scrape
   
   **Returns**: Status dictionary

.. autofunction:: data_updater.get_scraping_status

   Returns current scraping status.
   
   **Returns**:
   
   .. code-block:: python
   
      {
        "is_running": bool,
        "last_run": str,
        "status_message": str,
        "records_added": int
      }

.. autofunction:: data_updater.add_new_records_to_db

   Adds new records to database, avoiding duplicates.
   
   **Parameters**:
   
   - ``records`` (list): List of record dictionaries
   - ``dbname`` (str): Target database
   
   **Returns**: Number of records added

Helper Functions
~~~~~~~~~~~~~~~~

.. autofunction:: data_updater.parse_date
.. autofunction:: data_updater.extract_numeric
.. autofunction:: data_updater.clean_string
.. autofunction:: data_updater.get_existing_urls

Scraper (module_2_code/scrape.py)
----------------------------------

.. automodule:: module_2_code.scrape
   :members:
   :undoc-members:
   :show-inheritance:

GradCafeScraper Class
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: module_2_code.scrape.GradCafeScraper
   :members:
   :special-members: __init__

Data Cleaner (module_2_code/clean.py)
--------------------------------------

.. automodule:: module_2_code.clean
   :members:
   :undoc-members:
   :show-inheritance:

GradCafeDataCleaner Class
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: module_2_code.clean.GradCafeDataCleaner
   :members:
   :special-members: __init__

Error Handling
--------------

Database Errors
~~~~~~~~~~~~~~~

All database functions handle common errors:

- **Connection failures**: Return None or empty results
- **SQL errors**: Logged and re-raised with context
- **Data type mismatches**: Gracefully converted or set to NULL

HTTP Errors
~~~~~~~~~~~

Flask routes return appropriate status codes:

- ``200 OK``: Success
- ``404 Not Found``: Invalid route
- ``409 Conflict``: Busy state
- ``500 Internal Server Error``: Unexpected errors

Data Type Reference
-------------------

The application uses the following primary data structures:

Query Result Dictionary
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   {
     "question": str,      # Human-readable question
     "query": str,         # SQL statement
     "answer": Any         # Result (int, str, dict, or list)
   }

Scraping Status Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   {
     "is_running": bool,         # Whether scraping is active
     "last_run": str,            # ISO 8601 timestamp
     "status_message": str,      # Status description
     "records_added": int        # Count from last run
   }

Record Dictionary
~~~~~~~~~~~~~~~~~

.. code-block:: python

   {
     "program": str,
     "comments": str,
     "date_added": str,
     "url": str,
     "status": str,             # "Accepted", "Rejected", etc.
     "term": str,               # "Fall 2026", etc.
     "us_or_international": str,
     "gpa": float,
     "gre": float,
     "gre_v": float,
     "gre_aw": float,
     "degree": str,
     "llm_generated_program": str,
     "llm_generated_university": str
   }
