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

The application factory pattern allows dependency injection for testing.

**Parameters**:

- ``query_func`` (callable, optional): Custom query function for testing
- ``scraper_func`` (callable, optional): Custom scraper function for testing
- ``status_func`` (callable, optional): Custom status function for testing

**Returns**: Flask application instance

**Example**:

.. code-block:: python

   from app import create_app
   
   # Production
   app = create_app()
   
   # Testing with mocks
   def mock_query(dbname=None):
       return {"q1": {"question": "Test", "answer": 42}}
   
   app = create_app(query_func=mock_query)

Route Handlers
~~~~~~~~~~~~~~

The following routes are available:

**GET /** or **GET /analysis**
   Display the main analysis page with all query results.
   
   **Query Parameters**:
   
   - ``db`` (optional): Database name (default: ``gradcafe_sample``)
   
   **Returns**: HTML page with analysis results
   
   **Example**:
   
   .. code-block:: bash
   
      curl http://localhost:8080/
      curl http://localhost:8080/analysis?db=gradcafe_test

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
   
   - ``409 Conflict**: Scraping in progress, cannot update
   
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

   Creates a PostgreSQL connection with the specified database name.
   
   **Parameters**:
   
   - ``dbname`` (str, optional): Database name (default: "gradcafe_sample")
   
   **Returns**: psycopg2 connection object
   
   **Example**:
   
   .. code-block:: python
   
      from query_data import get_db_connection
      
      conn = get_db_connection("gradcafe_sample")
      cur = conn.cursor()
      cur.execute("SELECT COUNT(*) FROM gradcafe_main")
      count = cur.fetchone()[0]
      conn.close()

Query Functions
~~~~~~~~~~~~~~~~~~~

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

   **Returns**: Dictionary with percentage formatted as string
   
   .. code-block:: python
   
      {
        "question": "What percentage of entries are from international students?",
        "answer": "45.67%"
      }

.. autofunction:: query_data.question_3

   **Returns**: Dictionary with average scores
   
   .. code-block:: python
   
      {
        "question": "What is the average GPA, GRE, GRE V, GRE AW of applicants?",
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
        "q1": {"question": "...", "query": "...", "answer": 150},
        "q2": {"question": "...", "query": "...", "answer": "45.67%"},
        ...
        "q11": {"question": "...", "query": "...", "answer": [[...]]}
      }
   
   **Parameters**:
   
   - ``dbname`` (str, optional): Database name (default:  "gradcafe_sample")
   
   **Returns**: dict - Mapping "q1" through "q11" to query results

Data Loader (load_data.py)
---------------------------

.. automodule:: load_data
   :members:
   :undoc-members:
   :show-inheritance:

Main Functions
~~~~~~~~~~~~~~

.. autofunction:: load_data.load_data

   Loads data from a JSON file into the specified PostgreSQL database.
   
   **Parameters**:
   
   - ``dbname`` (str, optional): Database name (default: "gradcafe_sample")
   - ``file_path`` (str, optional): Path to JSON file (default: "module_3/sample_data/llm_extend_applicant_data.json")
   
   **Behavior**:
   
   1. Drops existing ``gradcafe_main`` table
   2. Creates fresh table schema
   3. Parses JSON file (supports both JSON array and JSONL formats)
   4. Transforms data (converts dates, extracts numeric values, cleans strings)
   5. Batch inserts records using ``execute_values``
   
   **Example**:
   
   .. code-block:: python
   
      from load_data import load_data
      
      # Load default data
      load_data()
      
      # Load custom data
      load_data(dbname="gradcafe_test", file_path="my_data.json")
   
   **Command Line**:
   
   .. code-block:: bash
   
      python load_data.py gradcafe_sample data.json

Data Updater (data_updater.py)
-------------------------------

.. automodule:: data_updater
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
~~~~~~~~~~~~~~~~

.. autofunction:: data_updater.parse_date

   Converts various date formats to YYYY-MM-DD for PostgreSQL.
   
   **Supported formats**:
   
   - DD/MM/YYYY (e.g., "28/01/2026")
   - Month DD, YYYY (e.g., "January 28, 2026")
   
   **Returns**: str or None

.. autofunction:: data_updater.extract_numeric

   Extracts numeric values from formatted strings.
   
   **Examples**:
   
   - "GPA 3.74" → 3.74
   - "GRE 320" → 320.0
   - "N/A" → None

.. autofunction:: data_updater.clean_string

   Removes NUL characters from strings to prevent PostgreSQL errors.

Database Operations
~~~~~~~~~~~~~~~~~~~

.. autofunction:: data_updater.get_existing_urls

   Retrieves all URLs currently in the database for duplicate detection.
   
   **Returns**: set of URL strings

.. autofunction:: data_updater.add_new_records_to_db

   Inserts new records into the database with duplicate checking.
   
   **Parameters**:
   
   - ``records`` (list): List of record dictionaries
   - ``dbname`` (str): Database name
   
   **Returns**: int - Number of records added

Scraping Workflow
~~~~~~~~~~~~~~~~~

.. autofunction:: data_updater.scrape_and_update_background

   Background function to scrape new data and update database.
   Runs in a separate thread to avoid blocking the web server.
   
   **Workflow**:
   
   1. Check existing URLs in database
   2. Scrape data from GradCafe (calls ``GradCafeScraper``)
   3. Clean data (calls ``GradCafeDataCleaner``)
   4. Enhance with LLM (calls ``apply_llm_standardization``)
   5. Filter out duplicates
   6. Insert new records
   7. Update global status
   
   **Parameters**:
   
   - ``dbname`` (str): Database name
   - ``max_pages`` (int): Maximum pages to scrape

.. autofunction:: data_updater.start_scraping

   Starts the scraping process in a background thread.
   
   **Returns**: dict with success status and message

.. autofunction:: data_updater.get_scraping_status

   Returns current scraping status.
   
   **Returns**: dict with is_running, status_message, last_run, records_added

Scraper Module (scrape.py)
---------------------------

.. automodule:: module_2_code.scrape
   :members:
   :undoc-members:
   :show-inheritance:

GradCafeScraper Class
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: module_2_code.scrape.GradCafeScraper
   :members:
   :special-members: __init__
   :exclude-members: __weakref__

   Main class for scraping GradCafe website.
   
   **Key Methods**:
   
   - ``scrape_data(max_pages=None)``: Scrape multiple pages
   - ``scrape_page(page_num)``: Scrape a single page
   - ``parse_result_row(row)``: Parse a table row into a dictionary
   
   **Example**:
   
   .. code-block:: python
   
      from module_2_code.scrape import GradCafeScraper
      
      scraper = GradCafeScraper()
      data = scraper.scrape_data(max_pages=2)
      print(f"Scraped {len(data)} results")

Cleaner Module (clean.py)
--------------------------

.. automodule:: module_2_code.clean
   :members:
   :undoc-members:
   :show-inheritance:

GradCafeDataCleaner Class
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: module_2_code.clean.GradCafeDataCleaner
   :members:
   :special-members: __init__
   :exclude-members: __weakref__

   Main class for cleaning and standardizing scraped data.
   
   **Key Methods**:
   
   - ``clean_data(input_file, output_file=None)``: Clean data from JSON file
   - ``normalize_date(date_str)``: Standardize date formats
   - ``normalize_numeric(value)``: Extract and validate numeric values
   
   **Example**:
   
   .. code-block:: python
   
      from module_2_code.clean import GradCafeDataCleaner
      
      cleaner = GradCafeDataCleaner()
      cleaned = cleaner.clean_data("raw_data.json", "clean_data.json")

LLM Functions
~~~~~~~~~~~~~

.. autofunction:: module_2_code.clean.apply_llm_standardization

   Applies LLM-based standardization to program and university names.
   
   **Parameters**:
   
   - ``input_file`` (str): Path to cleaned data JSON
   - ``output_file`` (str): Path for LLM-enhanced output
   
   **Returns**: bool - True if successful

Database Setup (setup_databases.py)
------------------------------------

.. automodule:: setup_databases
   :members:
   :undoc-members:
   :show-inheritance:

Utility Functions
~~~~~~~~~~~~~~~~~

Functions for creating and managing PostgreSQL databases and schema.

**Example**:

.. code-block:: python

   from setup_databases import create_database, create_schema
   
   create_database("gradcafe_sample")
   create_schema("gradcafe_sample")

Return Value Conventions
-------------------------

All query functions return dictionaries with these keys:

- ``question``: Human-readable question text
- ``query``: SQL statement that was executed
- ``answer``: Query result in appropriate format:
  
  - Scalar: int or float
  - Percentage: str formatted as "XX.XX%"
  - Dictionary: dict with named fields
  - Table: list of lists

Error Handling
--------------

All database functions handle errors gracefully:

- Connection errors return None or empty sets
- Query errors return default values
- Scraping errors update global status with error message

**Example**:

.. code-block:: python

   from query_data import question_1
   
   try:
       result = question_1("nonexistent_db")
   except Exception as e:
       print(f"Query failed: {e}")
       result = {"question": "...", "answer": 0}
