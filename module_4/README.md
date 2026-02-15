# Module 4: GradCafe Analysis Application

A Flask-based web application for analyzing graduate school admissions data from GradCafe.

## Features

- **Web Interface**: View statistical analysis of admissions data
- **Data Scraping**: Automated collection of GradCafe data
- **Database Integration**: PostgreSQL backend for data storage
- **Real-time Updates**: Background processing for data collection
- **Comprehensive Testing**: 100% test coverage with pytest

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
createdb gradcafe_sample
python src/setup_databases.py

# Run the application
cd src
python app.py
```

Visit `http://localhost:8080` to access the application.

### Running Tests

```bash
# Run all tests
cd module_4
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
Vist 'https://jhu-software-projects.readthedocs.io/en/latest/'
