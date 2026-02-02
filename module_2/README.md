Name: Zhendong Zhang - 8A80D7

Module Info: Module 2 - Web Scraping Assignment: Grad Cafe Data Collection
Due Date: Feb 1st - 2026

Approach:

1. WEB SCRAPING IMPLEMENTATION (scrape.py):

   Data Structures:
   - GradCafeScraper class: Main scraper encapsulating all scraping logic
   - self.data: List to store all scraped entry dictionaries
   - self.found_urls: Set to track all result URLs discovered during scraping
   - self.processed_urls: Set to track which URLs have been fetched for details
   - self.edge_cases: List to log entries that failed standard parsing

   Core Algorithm:
   a) Page-by-page scraping:
      - Construct URL with page parameter: base_url?page={page_number}
      - Fetch HTML using urllib.request with SSL context (handles certificate issues)
      - Parse HTML with BeautifulSoup (html.parser)
      - Extract table rows containing applicant entries
      - Continue until no more entries found or max_pages reached
      - 2-second delay between requests to respect server resources

   b) Entry extraction (_extract_entry_data):
      - Find all <td> cells in each table row
      - Extract season BEFORE filtering cells (season might be in "empty" cells)
      - Look ahead to next row for season information (season appears after data row)
      - Filter out empty cells for regular data extraction
      - Extract from cells:
        * Cell 0: University name (from div.tw-font-medium)
        * Cell 1: Program name and degree (from spans, split by bullet •)
        * Cell 2: Date information
        * Cell 3: Application status (Accepted/Rejected/Interview/etc)
      - Extract URL from <a> tag within the row

   c) Detailed data fetching (_fetch_detailed_data):
      - For each entry with a URL, fetch the individual result page
      - Use regex patterns to extract from result page text:
        * GRE Verbal: Pattern "GRE\s+Verbal\s*:\s*(\d{2,3})"
        * GRE Quantitative: Pattern "Quantitative\s*:\s*(\d{2,3})"
        * GRE General (if Quant not found): Pattern "GRE\s+General\s*:\s*(\d{2,3})"
        * GRE Analytical Writing: Pattern "Analytical\s+Writing\s*:\s*(\d+\.\d+)"
        * GPA: Pattern "Undergrad\s+GPA\s*[:\s]*([0-4](?:\.\d{1,2})?)"
        * Notes: Search for sections containing "note" (case-insensitive)
        * Comments: Search for sections containing "comment"
        * Country of Origin: Pattern "Degree'?s?\s+Country\s+of\s+Origin\s*:\s*([^\n]+)"

   d) Edge case recovery (_recover_edge_cases):
      - Identify URLs found in HTML but not successfully parsed
      - Attempt to extract data directly from result pages for these entries
      - Use regex to find university/program patterns in plain text
      - Merge with detailed data if successful

   e) Season extraction challenge:
      - Initial approach tried extracting from filtered cells - failed
      - Issue: Season badges in divs with "tw-bg-orange" class appeared in cells
        that get_text(strip=True) returned empty, so they were filtered out
      - Solution: Extract season from ALL cells BEFORE filtering
      - Additional challenge: Season information in separate row AFTER data row
      - Final solution: Look ahead to next entry (idx+1) to find season

2. DATA CLEANING IMPLEMENTATION (clean.py):

   Data Structures:
   - GradCafeDataCleaner class: Handles all cleaning operations
   - self.data: List of raw entries loaded from JSON
   - self.cleaned_data: List of cleaned/standardized entries

   Cleaning Algorithm:
   a) Text cleaning (_clean_text):
      - Remove HTML tags and entities
      - Normalize whitespace (collapse multiple spaces)
      - Strip leading/trailing whitespace

   b) Field standardization:
      - Rename 'season' field to 'term' for consistency
      - Map 'applicant_status' to 'status'
      - Format date_added as "Added on YYYY-MM-DD"
      - Convert numeric fields (GRE, GPA) to proper types

   c) Validation:
      - Check GRE scores are in valid range (130-170)
      - Check GPA is in valid range (0.0-4.0)
      - Check Analytical Writing in valid range (0.0-6.0)

   d) Output ordering:
      - Define specific field order for consistent JSON output
      - Include: university, program, degree, status, term, scores, demographics

3. SSL CERTIFICATE HANDLING:
   - Issue: macOS often has SSL certificate verification problems
   - Solution: Create SSL context with verification disabled
   - Implementation: ssl.create_default_context() with CERT_NONE mode

4. ROBOTS.TXT COMPLIANCE:
   - Verified /survey/ pages are not disallowed
   - Implemented 2-second delay between requests
   - Set proper User-Agent header
   - Limited concurrent requests (sequential processing)

5. DATA PERSISTENCE:
   - Raw data saved to applicant_data.json after scraping
   - Cleaned data saved to applicant_data_cleaned.json after cleaning
   - JSON format with indent=2 for readability

Known Bugs:

1. Incomplete Notes Extraction:
   - Issue: The notes extraction looks for sections containing "note" but the
     actual HTML structure on result pages may vary
   - Impact: Notes field may be null even when notes exist on the page
   - Fix: Need to inspect actual result pages more thoroughly to identify
     the correct HTML structure for notes sections (likely specific div classes
     or data attributes)

3. SSL Certificate Warning:
   - Issue: Disabling SSL verification (ssl.CERT_NONE) is a security risk
   - Impact: Could be vulnerable to MITM attacks (though unlikely for this use)
   - Fix: Install proper SSL certificates on the system, or use certifi library
     to provide certificate bundle. For production, should never disable verification.

4. Rate Limiting Not Detected:
   - Issue: If Grad Cafe implements rate limiting, the scraper will fail silently
     or collect incomplete data
   - Impact: May stop collecting data prematurely
   - Fix: Implement detection of HTTP 429 responses and exponential backoff retry logic

5. Memory Usage for Large Datasets:
   - Issue: All data stored in memory (self.data list) before saving to disk
   - Impact: For very large scrapes (100k+ entries), could cause memory issues
   - Fix: Implement streaming/chunked writing to JSON file, periodically flushing
     data to disk and clearing the in-memory list
