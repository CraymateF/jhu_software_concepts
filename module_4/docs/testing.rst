Testing Guide
=============

This guide covers how to run tests, understand test organization, and use test doubles/fixtures provided by the test suite.

Test Organization
-----------------

The test suite is organized into five categories using pytest markers. All 100 tests have markers - no unmarked tests are allowed.

Test Markers
~~~~~~~~~~~~

All tests must be marked with one or more of the following:

.. code-block:: python

   @pytest.mark.web        # Flask route/page tests (5 tests)
   @pytest.mark.buttons    # Button endpoints & busy-state behavior (7 tests)
   @pytest.mark.analysis   # Formatting/rounding of analysis output (4 tests)
   @pytest.mark.db         # Database schema/inserts/selects (60+ tests)
   @pytest.mark.integration  # End-to-end flows (4 tests)

**Total**: 100 tests with 100% code coverage

Running Tests
-------------

Run All Tests
~~~~~~~~~~~~~

Execute the entire test suite (required command per project policy):

.. code-block:: bash

   cd module_4
   pytest -m "web or buttons or analysis or db or integration"

**Expected output**:

.. code-block:: text

   ============================= test session starts ==============================
   100 passed in 1.77s
   ================================ tests coverage ================================
   Name                  Stmts   Miss  Cover
   ---------------------------------------------------
   src/__init__.py           0      0   100%
   src/app.py               47      0   100%
   src/data_updater.py     193      0   100%
   src/load_data.py        132      0   100%
   src/query_data.py       109      0   100%
   ---------------------------------------------------
   TOTAL                   481      0   100%
   Required test coverage of 100% reached. Total coverage: 100.00%

Run Specific Test Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run only web tests:

.. code-block:: bash

   pytest -m web -v

Run only button tests:

.. code-block:: bash

   pytest -m buttons -v

Run only analysis formatting tests:

.. code-block:: bash

   pytest -m analysis -v

Run only database tests:

.. code-block:: bash

   pytest -m db -v

Run only integration tests:

.. code-block:: bash

   pytest -m integration -v

Run Multiple Categories
~~~~~~~~~~~~~~~~~~~~~~~

Combine markers using boolean expressions:

.. code-block:: bash

   pytest -m "web or buttons"
   pytest -m "db and not integration"
   pytest -m "(web or buttons) and not integration"

Run with Coverage
~~~~~~~~~~~~~~~~~

Generate coverage report (enforces 100% requirement):

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

The test suite is configured to fail if coverage is below 100%:

.. code-block:: ini

   # pytest.ini
   [pytest]
   addopts = --cov=src --cov-report=term-missing --cov-fail-under=100

Generate HTML coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=html
   open htmlcov/index.html  # macOS
   xdg-open htmlcov/index.html  # Linux

Verbose Output
~~~~~~~~~~~~~~

For detailed test output with test names:

.. code-block:: bash

   pytest -v -m "web or buttons or analysis or db or integration"

Show stdout/print statements:

.. code-block:: bash

   pytest -s -m "web or buttons or analysis or db or integration"

Test Files
----------

Test Suite Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   module_4/
   ├── tests/
   │   ├── __init__.py
   │   ├── conftest.py                      # Shared fixtures
   │   ├── test_flask_page.py               # @pytest.mark.web
   │   ├── test_buttons.py                  # @pytest.mark.buttons
   │   ├── test_analysis_format.py          # @pytest.mark.analysis
   │   ├── test_db_insert.py                # @pytest.mark.db
   │   ├── test_integration_end_to_end.py   # @pytest.mark.integration
   │   ├── test_data_updater.py             # @pytest.mark.db
   │   ├── test_data_updater_complete.py    # @pytest.mark.db, integration
   │   ├── test_load_data.py                # @pytest.mark.db
   │   ├── test_load_data_complete.py       # @pytest.mark.db
   │   ├── test_query_functions.py          # @pytest.mark.db
   │   ├── test_query_connection.py         # @pytest.mark.db
   │   ├── test_coverage_improvements.py    # @pytest.mark.db, web
   │   ├── test_setup_databases.py          # @pytest.mark.db
   │   └── test_final_coverage.py           # @pytest.mark.db
   └── pytest.ini                           # Pytest configuration

test_flask_page.py
~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.web``

**Purpose**: Verify Flask routes and page rendering

**Tests**:

- ``test_app_factory_creates_app``: App factory pattern works
- ``test_app_has_all_required_routes``: All routes registered
- ``test_analysis_page_returns_200``: GET /analysis succeeds
- ``test_analysis_page_contains_required_buttons``: Buttons present in HTML
- ``test_analysis_page_text_contains_analysis_and_answer``: Labels present

**Selectors Used**:

.. code-block:: python

   # HTML data-testid attributes
   soup.find(attrs={"data-testid": "pull-data-btn"})
   soup.find(attrs={"data-testid": "update-analysis-btn"})

**Fixtures Used**: ``app``, ``client``

**Example**:

.. code-block:: python

   @pytest.mark.web
   def test_analysis_page_contains_required_buttons(client):
       response = client.get('/analysis')
       html = response.data.decode('utf-8')
       soup = BeautifulSoup(html, 'html.parser')
       
       pull_btn = soup.find(attrs={"data-testid": "pull-data-btn"})
       assert pull_btn is not None

test_buttons.py
~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.buttons``

**Purpose**: Test button endpoints and busy-state management

**Tests**:

- ``test_pull_data_returns_200``: POST /pull-data succeeds
- ``test_pull_data_triggers_loader``: Scraper function called
- ``test_update_analysis_returns_200_when_not_busy``: POST /update-analysis when free
- ``test_update_analysis_returns_409_when_busy``: Returns conflict when scraping
- ``test_update_analysis_performs_no_update_when_busy``: No database changes when busy
- ``test_pull_data_returns_409_when_already_scraping``: Prevents concurrent scraping
- ``test_both_pull_data_routes_work``: Both /pull-data and /pull_data work

**Test Doubles Used**:

.. code-block:: python

   # Mock scraper to avoid network calls
   with patch('app.start_scraping') as mock_scraper:
       mock_scraper.return_value = {"success": True}
       response = client.post('/pull-data')

**Busy-State Testing**:

.. code-block:: python

   # Simulate scraping in progress
   with patch('app.get_scraping_status') as mock_status:
       mock_status.return_value = {"is_running": True}
       response = client.post('/update-analysis')
       assert response.status_code == 409

**Fixtures Used**: ``app``, ``client``

test_analysis_format.py
~~~~~~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.analysis``

**Purpose**: Verify percentage formatting and label consistency

**Tests**:

- ``test_page_includes_answers_label``: "Answer:" labels present
- ``test_percentages_formatted_with_two_decimals``: XX.XX% format
- ``test_all_percentages_have_consistent_format``: No variations
- ``test_analysis_items_have_proper_labeling``: Structured output

**Regex Pattern Used**:

.. code-block:: python

   import re
   
   percentage_pattern = r'\d+\.\d{2}%'
   percentages = re.findall(percentage_pattern, html)
   
   # Verify all match
   for pct in percentages:
       assert re.match(r'^\d+\.\d{2}%$', pct)

**Fixtures Used**: ``app``, ``client``

test_db_insert.py
~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.db``

**Purpose**: Verify database schema, inserts, and idempotency

**Tests**:

- ``test_insert_on_pull_creates_new_rows``: Records inserted
- ``test_duplicate_rows_do_not_create_duplicates``: URL uniqueness
- ``test_query_function_returns_dict_with_expected_keys``: Return format
- ``test_database_schema_has_required_fields``: All Module 3 fields present
- ``test_query_handles_empty_database``: Graceful handling of empty data

**Fixtures Used**: ``test_db``

**Database Setup**:

.. code-block:: python

   @pytest.fixture
   def test_db():
       """Create and setup a test database connection."""
       conn = psycopg2.connect(
           dbname="gradcafe_test",
           user="fadetoblack",
           host="localhost"
       )
       
       # Setup: Create table
       cur = conn.cursor()
       cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
       cur.execute("""CREATE TABLE gradcafe_main (...);""")
       conn.commit()
       
       yield conn
       conn.close()

test_integration_end_to_end.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.integration``

**Purpose**: Test complete workflows from start to finish

**Tests**:

- ``test_end_to_end_pull_update_render``: Full data flow
- ``test_multiple_pulls_maintain_consistency``: Idempotency across pulls
- ``test_scraping_status_tracking``: Status updates correctly
- ``test_error_recovery``: System recovers from failures

**Fixtures Used**: ``app``, ``client``, ``test_db``

**Workflow Testing**:

.. code-block:: python

   # 1. Pull data
   response = client.post('/pull-data', json={"dbname": "gradcafe_test"})
   assert response.status_code == 200
   
   # 2. Wait for completion (or mock)
   time.sleep(0.1)
   
   # 3. Update analysis
   response = client.post('/update-analysis')
   assert response.status_code == 200
   
   # 4. Verify render
   response = client.get('/analysis')
   assert b'Answer:' in response.data

Shared Fixtures (conftest.py)
------------------------------

All fixtures are defined in ``tests/conftest.py`` for shared access across test files.

app Fixture
~~~~~~~~~~~

Creates a test Flask application with mocked dependencies:

.. code-block:: python

   @pytest.fixture
   def app():
       """Create a test Flask app instance."""
       from app import create_app
       
       def mock_query(dbname=None):
           return {
               'q1': {'question': 'Test Q1', 'answer': 100},
               'q2': {'question': 'Test Q2', 'answer': '50.00%'},
               # ... all 11 queries
           }
       
       def mock_status():
           return {'is_running': False, 'status_message': 'Ready'}
       
       app = create_app(query_func=mock_query, status_func=mock_status)
       app.config['TESTING'] = True
       return app

**Usage**:

.. code-block:: python

   @pytest.mark.web
   def test_something(app):
       assert app is not None
       assert app.config['TESTING'] is True

client Fixture
~~~~~~~~~~~~~~

Creates a test client for making HTTP requests:

.. code-block:: python

   @pytest.fixture
   def client(app):
       """Create a test client for the Flask app."""
       return app.test_client()

**Usage**:

.. code-block:: python

   @pytest.mark.web
   def test_route(client):
       response = client.get('/analysis')
       assert response.status_code == 200
       
       response = client.post('/pull-data', json={"max_pages": 1})
       assert response.json['ok'] is True

test_db Fixture
~~~~~~~~~~~~~~~

Creates a fresh test database for each test:

.. code-block:: python

   @pytest.fixture
   def test_db():
       """Create and setup a test database connection."""
       conn = psycopg2.connect(
           dbname="gradcafe_test",
           user="fadetoblack",
           host="localhost"
       )
       
       # Setup: Drop and create fresh table
       cur = conn.cursor()
       cur.execute("DROP TABLE IF EXISTS gradcafe_main;")
       cur.execute("""
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
       """)
       conn.commit()
       cur.close()
       
       yield conn
       
       # Teardown
       conn.close()

**Usage**:

.. code-block:: python

   @pytest.mark.db
   def test_database_operation(test_db):
       cur = test_db.cursor()
       cur.execute("INSERT INTO gradcafe_main (url) VALUES ('http://test.com')")
       test_db.commit()
       
       cur.execute("SELECT COUNT(*) FROM gradcafe_main")
       count = cur.fetchone()[0]
       assert count == 1

Test Doubles and Mocking
-------------------------

Mock Object Examples
~~~~~~~~~~~~~~~~~~~~

**Mock Query Functions**:

.. code-block:: python

   from unittest.mock import Mock, patch, MagicMock
   
   def mock_query(dbname=None):
       return {
           'q1': {'question': 'Q1', 'query': 'SELECT 1', 'answer': 100},
           'q2': {'question': 'Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
       }
   
   app = create_app(query_func=mock_query)

**Mock Scraper**:

.. code-block:: python

   with patch('data_updater.GradCafeScraper') as mock_scraper_class:
       mock_scraper = MagicMock()
       mock_scraper.scrape_data.return_value = [
           {'University': 'MIT', 'Program': 'CS', 'Url': 'http://test.com'}
       ]
       mock_scraper_class.return_value = mock_scraper
       
       # Now scraping will use the mock
       scrape_and_update_background(dbname='test', max_pages=1)

**Mock Database Connection**:

.. code-block:: python

   with patch('query_data.psycopg2.connect') as mock_connect:
       mock_conn = MagicMock()
       mock_cur = MagicMock()
       mock_cur.fetchone.return_value = (100,)
       mock_conn.cursor.return_value = mock_cur
       mock_connect.return_value = mock_conn
       
       result = question_1("test_db")
       assert result['answer'] == 100

Spy Pattern
~~~~~~~~~~~

Verify functions were called with correct arguments:

.. code-block:: python

   with patch('app.start_scraping') as mock_scraper:
       mock_scraper.return_value = {"success": True}
       
       client.post('/pull-data', json={"dbname": "test", "max_pages": 3})
       
       # Verify called with correct args
       mock_scraper.assert_called_once_with(dbname="test", max_pages=3)

HTML Selectors
--------------

Test Selector Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~

All interactive elements use ``data-testid`` attributes for testing:

**Buttons**:

.. code-block:: html

   <button data-testid="pull-data-btn">Pull Data</button>
   <button data-testid="update-analysis-btn">Update Analysis</button>

**Finding with BeautifulSoup**:

.. code-block:: python

   from bs4 import BeautifulSoup
   
   soup = BeautifulSoup(html, 'html.parser')
   pull_btn = soup.find(attrs={"data-testid": "pull-data-btn"})
   update_btn = soup.find(attrs={"data-testid": "update-analysis-btn"})
   
   assert pull_btn is not None
   assert pull_btn.text == "Pull Data"

**CSS Selectors**:

.. code-block:: python

   # By data-testid
   btn = soup.select_one('[data-testid="pull-data-btn"]')
   
   # By class
   answer_divs = soup.select('.analysis-answer')
   
   # By tag and attribute
   buttons = soup.select('button[data-testid]')

Coverage Requirements
---------------------

100% Coverage Requirement
~~~~~~~~~~~~~~~~~~~~~~~~~

The project enforces 100% code coverage across all source modules:

.. code-block:: ini

   # pytest.ini
   [pytest]
   addopts = --cov=src --cov-report=term-missing --cov-fail-under=100

**Coverage by Module**:

- ``src/app.py``: 100% (47 statements)
- ``src/query_data.py``: 100% (109 statements)  
- ``src/data_updater.py``: 100% (193 statements)
- ``src/load_data.py``: 100% (132 statements)
- **TOTAL**: 100% (481 statements)

Excluded Files
~~~~~~~~~~~~~~

The following are excluded from coverage:

.. code-block:: ini

   # .coveragerc
   [run]
   omit =
       */module_2_code/*
       */setup_databases.py
       */tests/*
       */__pycache__/*

Coverage Report Formats
~~~~~~~~~~~~~~~~~~~~~~~

**Terminal output**:

.. code-block:: bash

   pytest --cov=src --cov-report=term

**HTML report for browser viewing**:

.. code-block:: bash

   pytest --cov=src --cov-report=html
   open htmlcov/index.html

**XML for CI/CD tools**:

.. code-block:: bash

   pytest --cov=src --cov-report=xml

Best Practices
--------------

Writing New Tests
~~~~~~~~~~~~~~~~~

1. **Always add a marker**:

   .. code-block:: python
   
      @pytest.mark.db
      def test_my_new_feature():
          pass

2. **Use descriptive names**:

   .. code-block:: python
   
      # Good
      def test_pull_data_returns_409_when_already_scraping():
          pass
      
      # Bad
      def test_1():
          pass

3. **Arrange-Act-Assert pattern**:

   .. code-block:: python
   
      def test_something():
          # Arrange
          data = {"key": "value"}
          
          # Act
          result = process(data)
          
          # Assert
          assert result['success'] is True

4. **Use fixtures over setup/teardown**:

   .. code-block:: python
   
      @pytest.fixture
      def sample_data():
          return {"test": "data"}
      
      def test_with_data(sample_data):
          assert sample_data['test'] == "data"

5. **Mock external dependencies**:

   .. code-block:: python
   
      @patch('module.external_api_call')
      def test_feature(mock_api):
          mock_api.return_value = {"status": "ok"}
          # Test without hitting real API

Debugging Failed Tests
~~~~~~~~~~~~~~~~~~~~~~

**Run single test**:

.. code-block:: bash

   pytest tests/test_file.py::test_specific_function -v

**Show print statements**:

.. code-block:: bash

   pytest -s tests/test_file.py::test_specific_function

**Drop into debugger on failure**:

.. code-block:: bash

   pytest --pdb tests/test_file.py

**Show locals on failure**:

.. code-block:: bash

   pytest -l tests/test_file.py

Continuous Integration
----------------------

GitHub Actions Workflow
~~~~~~~~~~~~~~~~~~~~~~~~

The project includes a CI/CD workflow that runs all tests:

.. code-block:: yaml

   name: Tests
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       
       services:
         postgres:
           image: postgres:14
           env:
             POSTGRES_PASSWORD: postgres
           options: >-
             --health-cmd pg_isready
             --health-interval 10s
             --health-timeout 5s
             --health-retries 5
       
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
           with:
             python-version: '3.13'
         - name: Install dependencies
           run: |
             cd module_4
             pip install -r requirements.txt
         - name: Run tests
           run: |
             cd module_4
             pytest -m "web or buttons or analysis or db or integration"

Local CI Simulation
~~~~~~~~~~~~~~~~~~~

Simulate CI environment locally:

.. code-block:: bash

   # Clean environment
   python -m venv fresh_venv
   source fresh_venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run tests like CI does
   pytest -m "web or buttons or analysis or db or integration"

Next Steps
----------

After reading this guide:

1. Run the test suite: ``pytest -m "web or buttons or analysis or db or integration"``
2. Review :doc:`api` for module documentation
3. Explore :doc:`architecture` for system design
4. Check test files in ``tests/`` directory for examples
