# Module 5: Secure GradCafe Analysis Application

A Flask-based web application for analyzing graduate school admissions data from GradCafe with enhanced security features.

## Security Enhancements (Module 5)

- **SQL Injection Defense**: All queries use psycopg SQL composition with parameter binding
- **Database Hardening**: Environment-based configuration with least-privilege user support
- **Code Quality**: Pylint score of 10.00/10
- **Dependency Management**: Reproducible environments with pip and uv support  
- **Supply Chain Security**: Snyk vulnerability scanning

## Features

- **Web Interface**: View statistical analysis of admissions data
- **Data Scraping**: Automated collection of GradCafe data
- **Database Integration**: PostgreSQL backend for data storage
- **Real-time Updates**: Background processing for data collection
- **Comprehensive Testing**: 100% test coverage with pytest

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Graphviz (for dependency graphs)

### Fresh Install (Method 1: pip)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Set up database
createdb gradcafe_sample
python src/setup_databases.py

# Run the application
cd src
python app.py
```

### Fresh Install (Method 2: uv)

```bash
# Install uv if not already installed
pip install uv

# Create virtual environment and sync dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Set up database
createdb gradcafe_sample
python src/setup_databases.py

# Run the application
cd src
python app.py
```

### Editable Install (Development)

```bash
# Install package in editable mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

Visit `http://localhost:8080` to access the application.

## Code Quality

### Running Pylint

This project maintains a Pylint score of 10.00/10.

```bash
# Run Pylint on all source files
pylint src/*.py --fail-under=10
```

### Generating Dependency Graphs

```bash
# Generate dependency graph
pydeps src/app.py --noshow -T svg -o dependency.svg
```

## Database Security

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gradcafe_sample
DB_USER=gradcafe_user
DB_PASSWORD=your_secure_password_here
```

### Creating a Least-Privilege Database User

```sql
-- Create a read-only user for the application
CREATE USER gradcafe_user WITH PASSWORD 'your_secure_password';

-- Grant connection to database
GRANT CONNECT ON DATABASE gradcafe_sample TO gradcafe_user;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO gradcafe_user;

-- Grant SELECT on specific table (read-only)
GRANT SELECT ON gradcafe_main TO gradcafe_user;

-- If your app needs to insert/update data:
-- GRANT INSERT, UPDATE ON gradcafe_main TO gradcafe_user;
-- GRANT USAGE, SELECT ON SEQUENCE gradcafe_main_p_id_seq TO gradcafe_user;
```

## Running Tests

```bash
# Run all tests
cd module_5
pytest -m "web or buttons or analysis or db or integration"

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## Documentation

Full documentation is available at: [Read the Docs Link]

Or build locally:

```bash
cd docs
make html
open _build/html/index.html
```

## Project Structure

```
module_4/
├── src/                   # Application code
│   ├── app.py            # Flask application
│   ├── query_data.py     # Database queries
│   ├── load_data.py      # Data loading
│   ├── data_updater.py   # Scraping orchestration
│   ├── setup_databases.py
│   ├── templates/        # HTML templates
│   ├── static/          # CSS/JS/images
│   └── module_2_code/   # Scraper modules
├── tests/               # Test suite
│   ├── test_flask_page.py
│   ├── test_buttons.py
│   ├── test_analysis_format.py
│   ├── test_db_insert.py
│   └── test_integration_end_to_end.py
├── docs/                # Sphinx documentation
├── pytest.ini           # Pytest configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://fadetoblack@localhost/gradcafe_sample`)

## Testing

The test suite is organized into five categories:

- **web**: Flask route and page tests
- **buttons**: Button endpoints and busy-state behavior
- **analysis**: Formatting and rounding of analysis output
- **db**: Database schema, inserts, and selects
- **integration**: End-to-end flows

All tests use pytest markers and can be run selectively:

```bash
pytest -m web          # Run only web tests
pytest -m buttons      # Run only button tests
pytest -m analysis     # Run only analysis tests
pytest -m db           # Run only database tests
pytest -m integration  # Run only integration tests
```

### Coverage Requirements

The project requires 100% code coverage:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=100
```

Coverage report is saved to `coverage_summary.txt`.

## CI/CD

GitHub Actions automatically runs the test suite on push/PR. See `.github/workflows/tests.yml`.

## License

JHU Software Concepts - Module 4

## Author

Zhendong Zhang - 8A80D7

## Read the Docs Host:
Visit: https://jhu-software-projects.readthedocs.io/en/latest/
