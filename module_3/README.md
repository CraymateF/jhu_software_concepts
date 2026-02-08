# GradCafe Database Analysis System

A comprehensive web-based application for analyzing graduate school admissions data from GradCafe. This system provides SQL-based analytics, automated data scraping, and multi-database support with an intuitive web interface.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Functionality
- **11 SQL Analytics Queries**: Comprehensive analysis of admissions data including acceptance rates, GPA statistics, and university comparisons
- **Dual Database Support**: Switch between "My Dataset" (Module 2 - 30,001 records) and "Provided Dataset" (Module 3 - 49,960 records)
- **Live Data Scraping**: Automated scraping of new GradCafe entries with background processing
- **Dual Format Support**: Handles both old and new JSON data formats automatically
- **Interactive Web Interface**: Modern, responsive UI with gradient design and real-time updates

### Data Processing
- **Format Detection**: Automatically identifies and processes two different JSON formats
- **Date Parsing**: Supports multiple date formats (DD/MM/YYYY and "Month DD, YYYY")
- **Numeric Extraction**: Parses values from strings (e.g., "GPA 3.74" → 3.74)
- **Data Cleaning**: Removes null bytes and handles missing values
- **Duplicate Prevention**: Filters existing URLs to avoid duplicate entries

### Analytics
1. Total entries for Fall 2026
2. International student percentage
3. Average GPA, GRE, GRE Verbal, and GRE Analytical Writing scores
4. American student GPA averages
5. Acceptance rates for Fall 2026
6. Accepted student GPA averages
7. Johns Hopkins CS Masters applications
8. Georgetown/MIT/Stanford/CMU PhD CS acceptances
9. LLM-enhanced query comparison
10. CS PhD acceptance rates
11. Top universities by accepted student GPA

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **PostgreSQL**: 13 or higher
- **Operating System**: macOS, Linux, or Windows
- **RAM**: 4GB minimum (8GB recommended for large datasets)
- **Disk Space**: 500MB for application and datasets

### Python Dependencies
```
Flask==3.x
psycopg2-binary==2.9.x
beautifulsoup4==4.x
requests==2.x
```

## 📦 Installation

### 1. Clone the Repository
```bash
cd /path/to/your/workspace
git clone <repository-url>
cd jhu_software_concepts/module_3
```

### 2. Set Up Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv ../.venv

# Activate virtual environment
source ../.venv/bin/activate  # On macOS/Linux
# or
..\.venv\Scripts\activate     # On Windows
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and Configure PostgreSQL
```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create PostgreSQL user (if needed)
createuser -s fadetoblack  # Replace with your username
```

### 5. Set Up Databases
```bash
# Run the automated setup script
python setup_databases.py
```

This will:
- Create `gradcafe` and `gradcafe_sample` databases
- Load data from both Module 2 and Module 3 datasets
- Display setup progress and results

## 🚀 Quick Start

### Start the Application
```bash
# Make sure you're in the module_3 directory
cd /path/to/jhu_software_concepts/module_3

# Activate virtual environment
source ../.venv/bin/activate

# Start Flask server
python app.py
# or
FLASK_APP=app.py python -m flask run --port 8080
```

### Access the Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:8080
```

## 📖 Usage Guide

### Viewing Analytics
1. **Homepage**: Displays all 11 query results with visualizations
2. **SQL Queries**: Click "View SQL Query" under each result to see the underlying SQL
3. **Database Indicator**: Shows which database is currently active (top of page)

### Switching Databases
1. Click the **"Switch Database"** button in the header
2. Confirm the switch in the dialog
3. Page will reload with data from the selected database

### Pulling New Data
1. Click the **"Pull Data"** button
2. System will scrape new GradCafe entries in the background
3. Status updates appear in real-time
4. Notification appears when scraping completes
5. Choose to refresh the page to see updated analytics

### Updating Analysis
1. Click **"Update Analysis"** button
2. Page refreshes with latest data from the current database
3. Cannot update while data pull is in progress

## 📁 Project Structure

```
module_3/
├── app.py                      # Flask application & routing
├── query_data.py              # SQL query functions (11 queries)
├── load_data.py               # Data loading & format handling
├── data_updater.py            # Background scraping & updates
├── setup_databases.py         # Database initialization script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── limitations.md             # Known limitations
│
├── templates/
│   └── results.html           # Main web interface
│
├── static/
│   └── style.css              # Styling & gradients
│
├── module_2_code/             # Scraping modules from Module 2
│   ├── scrape.py
│   └── clean.py
│
└── sample_data/
    └── llm_extend_applicant_data.json  # Sample dataset (49,960 records)
```

## 🗄️ Database Schema

### Table: `gradcafe_main`

| Column | Type | Description |
|--------|------|-------------|
| p_id | SERIAL | Primary key (auto-increment) |
| program | TEXT | Combined program and university |
| comments | TEXT | Applicant notes/comments |
| date_added | DATE | Date entry was added |
| url | TEXT | Source URL from GradCafe |
| status | TEXT | Accepted/Rejected/Interview/Wait listed |
| term | TEXT | Application term (e.g., "Fall 2026") |
| us_or_international | TEXT | American/International |
| gpa | FLOAT | Grade point average |
| gre | FLOAT | GRE general score |
| gre_v | FLOAT | GRE verbal score |
| gre_aw | FLOAT | GRE analytical writing score |
| degree | TEXT | PhD/Masters/PsyD |
| llm_generated_program | TEXT | LLM-standardized program name |
| llm_generated_university | TEXT | LLM-standardized university name |
| raw_data | JSONB | Original JSON record |

### Databases

1. **gradcafe** - "My Dataset (Module 2)"
   - Source: `module_2/llm_extend_applicant_data.json`
   - Records: ~30,001
   - Format: Old format with separate University/Program fields

2. **gradcafe_sample** - "Provided Dataset (Module 3)"
   - Source: `module_3/sample_data/llm_extend_applicant_data.json`
   - Records: ~49,960
   - Format: New format with combined program field

## 🔌 API Endpoints

### GET `/`
Main page displaying all query results
- **Query Parameter**: `db` (optional) - Database name (`gradcafe` or `gradcafe_sample`)
- **Returns**: HTML page with analytics results

### POST `/pull_data`
Trigger background data scraping
- **Request Body**: 
  ```json
  {
    "dbname": "gradcafe",
    "max_pages": 2
  }
  ```
- **Returns**: 
  ```json
  {
    "success": true,
    "message": "Scraping started in background for gradcafe"
  }
  ```

### GET `/scraping_status`
Check scraping progress
- **Returns**:
  ```json
  {
    "is_running": false,
    "status_message": "Successfully added 15 new records!",
    "records_added": 15,
    "last_run": "2026-02-08 01:30:00"
  }
  ```

## 🛠️ Development

### Adding New Queries

1. Add function to `query_data.py`:
```python
def question_12(dbname=None):
    """Your question description"""
    conn = get_db_connection(dbname)
    cur = conn.cursor()
    
    query = """
        SELECT ...
        FROM gradcafe_main
        WHERE ...
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "question": "Your question text",
        "query": query.strip(),
        "answer": result[0]
    }
```

2. Add to `run_all_queries()` in same file
3. Add display section in `templates/results.html`

### Manual Data Loading

Load specific data into a specific database:
```bash
python load_data.py [database_name] [file_path]

# Examples:
python load_data.py gradcafe module_2/llm_extend_applicant_data.json
python load_data.py gradcafe_sample module_3/sample_data/llm_extend_applicant_data.json
```

### Database Management

```bash
# Drop and recreate database
dropdb gradcafe
createdb gradcafe
python load_data.py gradcafe module_2/llm_extend_applicant_data.json

# Check database contents
psql gradcafe -c "SELECT COUNT(*) FROM gradcafe_main;"
psql gradcafe -c "SELECT * FROM gradcafe_main LIMIT 5;"
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use a different port
python -m flask run --port 8081
```

### Database Connection Errors
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql # Linux
```

### Missing Python Packages
```bash
pip install -r requirements.txt
```

### Empty Query Results
- Ensure database is populated: `python setup_databases.py`
- Check database has data: `psql gradcafe -c "SELECT COUNT(*) FROM gradcafe_main;"`
- Verify you're querying the correct database

### Division by Zero Errors
- These are now handled with `NULLIF()` in queries
- Returns "N/A" for empty datasets
- Update to latest code if still seeing errors

## 📝 Notes

- **Data Privacy**: This system works with publicly available GradCafe data
- **Scraping Rate**: Limited to avoid overwhelming GradCafe servers (2 pages default)
- **Background Processing**: Scraping runs in separate thread to keep UI responsive
- **Database Persistence**: Data persists across application restarts
- **Format Compatibility**: Automatically handles both old and new data formats

## 🤝 Contributing

This is a course project for JHU Software Concepts. For questions or issues, please contact the course instructor or TA.

## 📄 License

This project is created for educational purposes as part of JHU Software Concepts coursework.

---

**Course**: JHU Software Concepts  
**Module**: Module 3 - Database Integration  
**Author**: FadeToBlack  
**Date**: February 2026
