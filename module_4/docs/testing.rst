Testing Guide
=============

This guide covers how to run tests, understand test organization, and use test doubles/fixtures.

Test Organization
-----------------

The test suite is organized into five categories using pytest markers:

Test Markers
~~~~~~~~~~~~

All tests are marked with one or more of the following:

.. code-block:: python

   @pytest.mark.web        # Flask route/page tests
   @pytest.mark.buttons    # Button endpoints & busy-state behavior
   @pytest.mark.analysis   # Formatting/rounding of analysis output
   @pytest.mark.db         # Database schema/inserts/selects
   @pytest.mark.integration  # End-to-end flows

Running Tests
-------------

Run All Tests
~~~~~~~~~~~~~

Execute the entire test suite:

.. code-block:: bash

   cd module_4
   pytest -m "web or buttons or analysis or db or integration"

This command is required to run all tests as per project policy (no unmarked tests).

Run Specific Test Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run only web tests:

.. code-block:: bash

   pytest -m web

Run only button tests:

.. code-block:: bash

   pytest -m buttons

Run only analysis formatting tests:

.. code-block:: bash

   pytest -m analysis

Run only database tests:

.. code-block:: bash

   pytest -m db

Run only integration tests:

.. code-block:: bash

   pytest -m integration

Run Multiple Categories
~~~~~~~~~~~~~~~~~~~~~~~

Combine markers using boolean expressions:

.. code-block:: bash

   pytest -m "web or buttons"
   pytest -m "db and not integration"

Run with Coverage
~~~~~~~~~~~~~~~~~

Generate coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Generate HTML coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=html
   open htmlcov/index.html

**Coverage Requirement**: The project requires 100% code coverage across all modules.

Verbose Output
~~~~~~~~~~~~~~

For detailed test output:

.. code-block:: bash

   pytest -v -m "web or buttons or analysis or db or integration"

Test Files
----------

Test Suite Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   module_4/
   ├── tests/
   │   ├── __init__.py
   │   ├── conftest.py               # Shared fixtures
   │   ├── test_flask_page.py        # @pytest.mark.web
   │   ├── test_buttons.py           # @pytest.mark.buttons
   │   ├── test_analysis_format.py   # @pytest.mark.analysis
   │   ├── test_db_insert.py         # @pytest.mark.db
   │   └── test_integration_end_to_end.py  # @pytest.mark.integration
   └── pytest.ini                    # Pytest configuration

test_flask_page.py
~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.web``

**Tests**:

- App factory creates testable Flask app
- App has all required routes (/, /analysis, /pull-data, /update-analysis)
- GET /analysis returns 200
- Page contains "Pull Data" and "Update Analysis" buttons
- Page text includes "Analysis" and "Answer:" labels

**Selectors Used**:

- ``data-testid="pull-data-btn"``
- ``data-testid="update-analysis-btn"``

test_buttons.py
~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.buttons``

**Tests**:

- POST /pull-data returns 200 with ``{"ok": true}``
- POST /pull-data triggers the loader (mocked scraper)
- POST /update-analysis returns 200 when not busy
- POST /update-analysis returns 409 when scraping in progress
- POST /update-analysis performs no update when busy
- POST /pull-data returns 409 when already scraping
- Both /pull-data and /pull_data routes work

test_analysis_format.py
~~~~~~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.analysis``

**Tests**:

- Page includes "Answer:" labels
- Percentages formatted with exactly two decimal places (XX.XX%)
- All percentages have consistent format
- Analysis items have proper labeling structure

**Regex Pattern Used**:

.. code-block:: python

   percentage_pattern = r'\d+\.\d{2}%'

test_db_insert.py
~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.db``

**Tests**:

- Insert on pull creates new rows with required non-null fields
- Duplicate rows don't create duplicates (idempotency)
- Query function returns dict with expected keys
- Database schema has all required Module-3 fields
- Query handles empty database gracefully

**Fixtures**:

- ``test_db``: Creates temporary test database

test_integration_end_to_end.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Markers**: ``@pytest.mark.integration``

**Tests**:

- End-to-end: pull → update → render flow
- Multiple pulls with overlapping data maintain consistency
- Busy state blocks both pull and update
- Rendered page shows correctly formatted percentages

Test Doubles & Fixtures
------------------------

Shared Fixtures (conftest.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @pytest.fixture
   def app():
       """Create a test Flask app with mocked dependencies."""
       # Returns Flask app instance

   @pytest.fixture
   def client(app):
       """Create test client for Flask app."""
       # Returns app.test_client()

Custom Test Doubles
~~~~~~~~~~~~~~~~~~~

Mock Query Function
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def mock_query(dbname=None):
       return {
           'q1': {'question': '...', 'query': '...', 'answer': 100},
           'q2': {'question': '...', 'query': '...', 'answer': '50.00%'},
           # ... more queries
       }

Mock Scraper Function
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def mock_scraper(dbname=None, max_pages=None):
       return {'status': 'started', 'records_added': 5}

Mock Status Function
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def mock_status():
       return {
           'is_running': False,
           'status_message': 'Ready',
           'records_added': 0
       }

Database Fixture
^^^^^^^^^^^^^^^^

.. code-block:: python

   @pytest.fixture
   def test_db():
       """Create test database with schema, yield connection, teardown."""
       # Setup: Create database and table
       conn = psycopg2.connect(...)
       yield conn
       # Teardown: Drop table and close connection

Expected Selectors
------------------

HTML Test Selectors
~~~~~~~~~~~~~~~~~~~

The application uses the following ``data-testid`` attributes for testing:

.. code-block:: html

   <!-- Pull Data Button -->
   <button data-testid="pull-data-btn">Pull Data</button>

   <!-- Update Analysis Button -->
   <button data-testid="update-analysis-btn">Update Analysis</button>

   <!-- Switch Database Button -->
   <button data-testid="switch-database-btn">Switch Database</button>

CSS Classes
~~~~~~~~~~~

Tests also use the following CSS classes:

- ``.answer-box``: Container for answer display
- ``.answer-value``: The answer value itself
- ``.answer-label-prefix``: "Answer:" label text
- ``.result-card``: Individual question card
- ``.question``: Question text

Writing New Tests
-----------------

Test Template
~~~~~~~~~~~~~

Use this template for new tests:

.. code-block:: python

   import pytest
   from module_4.src.app import create_app

   @pytest.mark.your_marker
   def test_your_feature():
       """Brief description of what this test verifies."""
       # Arrange: Set up test data and mocks
       def mock_func():
           return {'expected': 'data'}
       
       app = create_app(query_func=mock_func)
       client = app.test_client()
       
       # Act: Perform the action
       response = client.get('/some-route')
       
       # Assert: Verify expectations
       assert response.status_code == 200
       assert 'expected text' in response.data.decode('utf-8')

Testing Best Practices
~~~~~~~~~~~~~~~~~~~~~~~

1. **Use descriptive test names**: ``test_pull_data_returns_409_when_busy``
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per concept**: Don't test multiple unrelated things
4. **Use appropriate markers**: Every test must have at least one marker
5. **Mock external dependencies**: Don't hit real databases or networks in unit tests
6. **Keep tests fast**: Unit tests should run in milliseconds
7. **Make tests deterministic**: No random values or time dependencies

Testing Checklist
~~~~~~~~~~~~~~~~~

Before submitting code, verify:

- [ ] All new code is covered by tests
- [ ] All tests pass: ``pytest -m "web or buttons or analysis or db or integration"``
- [ ] Coverage is 100%: ``pytest --cov=src --cov-report=term-missing --cov-fail-under=100``
- [ ] All tests have markers
- [ ] No tests depend on external services (use mocks)
- [ ] Tests are fast (< 1 second per test)
- [ ] Test names are descriptive

Continuous Integration
----------------------

GitHub Actions
~~~~~~~~~~~~~~

The project uses GitHub Actions for CI. The workflow:

1. Sets up Python 3.10
2. Installs dependencies
3. Starts PostgreSQL service
4. Creates test databases
5. Runs pytest with coverage
6. Generates coverage report

**Workflow File**: ``.github/workflows/tests.yml``

To trigger CI:

.. code-block:: bash

   git push origin main

Local CI Simulation
~~~~~~~~~~~~~~~~~~~~

Simulate CI environment locally:

.. code-block:: bash

   # Start PostgreSQL
   brew services start postgresql@15  # macOS
   
   # Create test database
   createdb gradcafe_test
   
   # Run tests like CI does
   export DATABASE_URL="postgresql://postgres@localhost/gradcafe_test"
   pytest -m "web or buttons or analysis or db or integration" \
          --cov=src --cov-report=term-missing --cov-fail-under=100

Troubleshooting Tests
---------------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**

If you see ``ModuleNotFoundError``:

.. code-block:: bash

   # Ensure you're in the module_4 directory
   cd module_4
   
   # Or add to PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

**Database Connection Errors**

If database tests fail:

1. Ensure PostgreSQL is running
2. Create test database: ``createdb gradcafe_test``
3. Set DATABASE_URL: ``export DATABASE_URL="postgresql://user@localhost/gradcafe_test"``

**BeautifulSoup Not Found**

Install test dependencies:

.. code-block:: bash

   pip install beautifulsoup4 lxml

**Coverage Below 100%**

To find uncovered lines:

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Look for lines with missing coverage (marked with ``!!!``).

Running Individual Tests
~~~~~~~~~~~~~~~~~~~~~~~~

Run a specific test file:

.. code-block:: bash

   pytest tests/test_flask_page.py

Run a specific test function:

.. code-block:: bash

   pytest tests/test_flask_page.py::test_analysis_page_returns_200

Debug mode with output:

.. code-block:: bash

   pytest -s -vv tests/test_flask_page.py::test_analysis_page_returns_200

Code Coverage Report
--------------------

The coverage report should be saved to ``module_4/coverage_summary.txt``:

.. code-block:: bash

   pytest --cov=src --cov-report=term > coverage_summary.txt

Expected output format:

.. code-block:: text

   ============================= test session starts ==============================
   collected 25 items

   tests/test_flask_page.py .....                                           [ 20%]
   tests/test_buttons.py .......                                            [ 48%]
   tests/test_analysis_format.py ....                                       [ 64%]
   tests/test_db_insert.py .....                                            [ 84%]
   tests/test_integration_end_to_end.py ....                                [100%]

   ----------- coverage: platform darwin, python 3.10.0 -----------
   Name                  Stmts   Miss  Cover   Missing
   ---------------------------------------------------
   src/app.py               45      0   100%
   src/query_data.py       120      0   100%
   src/load_data.py         85      0   100%
   src/data_updater.py     150      0   100%
   ---------------------------------------------------
   TOTAL                   400      0   100%

   ========================= 25 passed in 2.34s ================================
