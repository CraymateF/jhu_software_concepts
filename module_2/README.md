# Grad Cafe Data Scraper - Module 2

## Overview

This project scrapes graduate admissions data from The Grad Cafe (https://www.thegradcafe.com) and processes it into a clean, standardized JSON format. The scraper collects information about graduate program applicants, including their academic scores, application status, and program details.

## Project Structure

```
module_2/
├── scrape.py                 # Web scraper implementation
├── clean.py                  # Data cleaning and standardization
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── applicant_data.json       # Final cleaned output (generated)
├── raw_data.json            # Raw scraped data (generated)
└── llm_hosting/             # LLM-based data standardization
    ├── requirements.txt
    ├── app.py
    └── ...
```

## Requirements Met

### SHALL Requirements
- ✅ Programmatically pulls data from Grad Cafe using Python
- ✅ Relies only on libraries covered in module 2 lecture (urllib, BeautifulSoup, regex, json)
- ✅ Extracts all required data categories:
  - Program Name
  - University
  - Comments (if available)
  - Date of Information Added to Grad Café
  - URL link to applicant entry
  - Applicant Status
  - Acceptance/Rejection Dates
  - Semester and Year of Program Start (if available)
  - International / American Student (if available)
  - GRE Score (V and Q)
  - Masters or PhD (if available)
  - GPA (if available)
  - GRE AW (if available)
- ✅ Uses urllib for URL management
- ✅ Uses JSON to store data in applicant_data.json with reasonable keys
- ✅ Collects at least 30,000 grad applicant entries
- ✅ Includes README and requirements.txt
- ✅ Complies with robots.txt
- ✅ Uses Python 3.10+

### SHOULD Requirements
- ✅ Uses BeautifulSoup and regex for data parsing
- ✅ Implements required functions:
  - `scrape_data()`: Pulls data from Grad Cafe
  - `clean_data()`: Converts data into structured format
  - `save_data()`: Saves cleaned data to JSON
  - `load_data()`: Loads data from JSON
  - Private methods marked with `_` prefix
- ✅ Scraping in scrape.py, cleaning in clean.py
- ✅ Removes HTML remnants
- ✅ Uses consistent format for unavailable data (None or empty string)
- ✅ Handles messy and unexpected information
- ✅ Extracts accurate information
- ✅ Well-commented and clearly named variables

## Installation

### Step 1: Install Python Dependencies
```bash
cd module_2
pip install -r requirements.txt
```

### Step 2: (Optional) Set up LLM Hosting for Data Cleaning
The LLM hosting component helps standardize program and university names. To use it:

```bash
cd llm_hosting
pip install -r requirements.txt
cd ..
```

Note: The LLM component requires additional setup. See [llm_hosting/README.md](llm_hosting/README.md) for details.

## Usage

### Step 1: Scrape Data from Grad Cafe

```bash
python scrape.py
```

This will:
- Fetch applicant data from Grad Cafe survey pages
- Parse HTML using BeautifulSoup
- Extract structured information from each entry
- Save raw data to `raw_data.json`
- Display progress and total entries collected

The scraper respects robots.txt guidelines and includes appropriate delays between requests.

### Step 2: Clean and Standardize Data

```bash
python clean.py
```

This will:
- Load raw data from `raw_data.json`
- Apply basic cleaning (remove HTML, normalize text)
- Save cleaned data to `applicant_data.json`
- Display summary statistics

### Step 3: (Optional) Apply LLM-Based Standardization

For enhanced program and university name standardization using a local LLM:

```python
# Python API
from clean import apply_llm_standardization

# Apply to cleaned data
apply_llm_standardization('applicant_data.json')

# Or save to a different file
apply_llm_standardization('applicant_data.json', output_file='standardized.json')
```

Alternatively, use the llm_hosting Flask API for more advanced features:

```bash
# Start Flask API server
cd llm_hosting
python app.py --serve

# Or process files from CLI
python app.py --file data.json --stdout
```

For more details on the LLM hosting component, see [llm_hosting/README.md](llm_hosting/README.md).

### Step 4: Analyze the Results

The final dataset is saved in `applicant_data.json` with the following structure:

```json
[
  {
    "program": "Computer Science",
    "university": "Johns Hopkins University",
    "program_clean": "Computer Science",
    "university_clean": "Johns Hopkins University",
    "applicant_status": "Accepted",
    "status_date": "03/15/2025",
    "comments": "Received acceptance with full funding",
    "comments_date": "03/15/2025",
    "season": "Fall 2025",
    "degree": "PhD",
    "gre_v": 162,
    "gre_q": 168,
    "gre_aw": 4.5,
    "gpa": 3.87,
    "international": "American",
    "url": "https://www.thegradcafe.com/survey/...",
    "data_added_date": "2026-02-01T..."
  },
  ...
]
```

## Robots.txt Compliance

### Verification

Before scraping, we verified that Grad Cafe permits data collection:

```bash
# To check robots.txt yourself:
curl https://www.thegradcafe.com/robots.txt
```

### Key Findings

- ✅ Grad Cafe allows crawling of survey pages for research purposes
- ✅ The `/survey/index.php` endpoint is not explicitly disallowed
- ✅ A 2-second delay is included between requests to minimize server load
- ✅ User-Agent is properly identified

**Evidence**: See `robots_verification.txt` in this directory for the full robots.txt content.

## Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| program | string | Name of the graduate program |
| program_clean | string | Standardized program name (after LLM cleaning) |
| university | string | Name of the university |
| university_clean | string | Standardized university name (after LLM cleaning) |
| applicant_status | string | Application status (Accepted, Rejected, Waitlisted, etc.) |
| status_date | string | Date of status change |
| comments | string | Applicant comments about the program |
| comments_date | string | Date comments were posted |
| season | string | Application season (Fall 2025, Spring 2026, etc.) |
| degree | string | Degree type (PhD, Masters) |
| gre_v | integer | GRE Verbal score (130-170) |
| gre_q | integer | GRE Quantitative score (130-170) |
| gre_aw | float | GRE Analytical Writing score (0.0-6.0) |
| gpa | float | Undergraduate GPA |
| international | string | Student status (International, American) |
| url | string | Direct link to applicant entry on Grad Cafe |
| data_added_date | string | ISO format timestamp when data was scraped |

## Error Handling

The scraper includes robust error handling:
- Connection timeouts are caught and logged
- Malformed HTML entries are skipped
- Missing data fields are set to None
- Empty entries are filtered out during cleaning

## Performance

- Typical scraping time: 2-6 hours for full dataset (30,000+ entries)
- Data processing: 5-15 minutes for cleaning and standardization
- Output file size: 15-25 MB (JSON format)

## Troubleshooting

### Issue: "Connection refused" error
**Solution**: Check your internet connection and ensure Grad Cafe is accessible. The scraper may also be rate-limited; try again after a few minutes.

### Issue: Few entries collected
**Solution**: Grad Cafe may have changed its HTML structure. Inspect the page source and update the CSS selectors in `_parse_entries()`.

### Issue: LLM cleaning not working
**Solution**: Ensure you've set up the llm_hosting directory and installed its dependencies. See [llm_hosting/README.md](llm_hosting/README.md).

### Issue: "ModuleNotFoundError" for BeautifulSoup
**Solution**: Install requirements: `pip install -r requirements.txt`

## Data Cleaning Notes

The cleaning process handles several common issues:
1. **Name Variations**: "JHU", "Johns Hopkins", "Johns Hopkins University" → "Johns Hopkins University"
2. **Abbreviations**: Program names are expanded and standardized
3. **Typos**: Common misspellings are corrected using fuzzy matching
4. **HTML Remnants**: All HTML tags and entities are removed
5. **Missing Data**: Consistently represented as None or empty strings
6. **Whitespace**: Extra spaces and line breaks are normalized

## Future Improvements

1. Add database storage (SQLite/PostgreSQL)
2. Implement incremental scraping (avoid re-scraping known entries)
3. Add visualization dashboard for statistics
4. Expand LLM cleaning with more canonical program lists
5. Add progress persistence for long-running scrapes

## Academic Integrity

This project was created for educational purposes as part of the JHU Software Concepts course. All data collected is from publicly available sources and used solely for academic analysis.

## License

Educational use only. See course syllabus for terms.

## Author

Student
Course: JHU Software Concepts - Module 2
Date: February 2026
