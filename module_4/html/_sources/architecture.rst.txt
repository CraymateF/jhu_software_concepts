Architecture
============

System Architecture
-------------------

The GradCafe Analysis Application follows a three-tier architecture:

.. image:: _static/architecture_diagram.png
   :alt: Architecture Diagram
   :align: center

(Note: Create an architecture diagram showing Web → ETL → Database layers)

Architectural Layers
--------------------

Web Layer
~~~~~~~~~

**Responsibility**: Handle HTTP requests, render templates, manage user interactions

**Components**:

- **Flask Application** (``app.py``): Main application factory and route handlers
- **Templates** (``templates/``): Jinja2 HTML templates for rendering
- **Static Assets** (``static/``): CSS, JavaScript, images

**Key Features**:

- RESTful API endpoints for data operations
- Server-side rendering with Jinja2
- AJAX support for asynchronous operations
- Busy-state management to prevent concurrent operations

**Routes**:

- ``GET /`` or ``GET /analysis``: Display analysis page
- ``POST /pull-data``: Trigger data scraping
- ``POST /update-analysis``: Refresh analysis
- ``GET /scraping_status``: Check scraping status

ETL Layer
~~~~~~~~~

**Responsibility**: Extract, Transform, and Load data from GradCafe website

**Components**:

- **Scraper** (``module_2_code/scrape.py``): Web scraping logic
- **Cleaner** (``module_2_code/clean.py``): Data cleaning and standardization
- **Data Updater** (``data_updater.py``): Orchestrates scraping and database updates
- **Loader** (``load_data.py``): Batch data loading utilities

**ETL Pipeline**:

1. **Extract**: Scrape data from GradCafe using BeautifulSoup
2. **Transform**: Clean and standardize fields (dates, GPAs, GRE scores)
3. **Load**: Insert into PostgreSQL with duplicate detection

**Data Quality**:

- URL-based uniqueness constraint prevents duplicates
- NUL character removal for PostgreSQL compatibility
- Date format standardization
- Numeric value extraction and validation

Database Layer
~~~~~~~~~~~~~~

**Responsibility**: Persist and query admissions data

**Components**:

- **Query Module** (``query_data.py``): Parameterized SQL queries
- **PostgreSQL Database**: Relational storage with JSONB support
- **Setup Module** (``setup_databases.py``): Schema initialization

**Schema Design**:

The ``gradcafe_main`` table uses:

- **p_id**: Auto-incrementing primary key
- **url**: Unique constraint for idempotency
- **raw_data**: JSONB field for flexibility
- **Indexes**: On frequently queried fields (term, status, university)

**Query Functions**:

Each query function returns a dictionary with:

- ``question``: Human-readable question text
- ``query``: SQL statement executed
- ``answer``: Query result (scalar, dict, or list)

Design Patterns
---------------

Application Factory Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``create_app()`` factory allows dependency injection for testing:

.. code-block:: python

   def create_app(query_func=None, scraper_func=None, status_func=None):
       # Create Flask app with injected dependencies
       # Enables mocking in tests

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

All external dependencies (database, scraper, queries) can be injected:

- Facilitates unit testing without real database/network
- Allowsswapping implementations (e.g., test vs. production)
- Improves testability and modularity

Repository Pattern
~~~~~~~~~~~~~~~~~~

Database access is abstracted through query functions:

- Single responsibility: each function handles one query
- Consistent return format (dict with question/query/answer)
- Easy to test and modify

Background Processing
~~~~~~~~~~~~~~~~~~~~~~

Scraping runs in a separate thread:

- Non-blocking: users can continue browsing
- Status tracking: global state shows progress
- Busy gating: prevents concurrent scrapes

Data Flow
---------

Pull Data Flow
~~~~~~~~~~~~~~

1. User clicks "Pull Data" button
2. AJAX POST to ``/pull-data``
3. Backend checks if scraping already in progress
4. If free, starts background thread:
   
   a. Scrape GradCafe pages
   b. Clean and standardize data
   c. Check for existing URLs
   d. Insert new records to database

5. Return success response
6. Frontend polls ``/scraping_status`` for updates

Update Analysis Flow
~~~~~~~~~~~~~~~~~~~~

1. User clicks "Update Analysis" button
2. AJAX POST to ``/update-analysis``
3. Backend checks if scraping in progress
4. If free, return success
5. Frontend reloads page to fetch latest data
6. ``GET /analysis`` queries database and renders results

Query Flow
~~~~~~~~~~

1. Route handler calls ``run_all_queries()``
2. Each query function:
   
   a. Connects to database
   b. Executes SQL
   c. Formats result
   d. Returns dict

3. Template renders results with HTML

Operational Notes
-----------------

Busy-State Policy
~~~~~~~~~~~~~~~~~

To ensure data consistency:

- Only one scraping operation allowed at a time
- ``/update-analysis`` blocked during scraping
- ``/pull-data`` blocked if already scraping
- Enforced via global ``scraping_status`` variable

**HTTP Status Codes**:

- ``200``: Success
- ``409 Conflict``: Busy, try again later

Idempotency Strategy
~~~~~~~~~~~~~~~~~~~~~

Duplicate prevention via:

- ``url`` field has UNIQUE constraint
- ``get_existing_urls()`` checks before insert
- ``ON CONFLICT`` handling (if implemented)

**Result**: Running pull-data multiple times with same data won't create duplicates

Uniqueness Keys
~~~~~~~~~~~~~~~

Primary uniqueness identifier: **url**

- Each GradCafe post has unique URL
- Used to detect and skip duplicates
- Ensures data integrity across multiple pulls

Scalability Considerations
--------------------------

Current Limitations
~~~~~~~~~~~~~~~~~~~

- Single-threaded scraping
- Global state for busy tracking
- In-memory status (lost on restart)
- Blocking database queries

Future Improvements
~~~~~~~~~~~~~~~~~~~

- Message queue (Celery) for task management
- Redis for distributed state
- Connection pooling for database
- Async/await for non-blocking queries
- Pagination for large result sets
