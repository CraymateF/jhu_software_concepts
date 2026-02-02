"""
Grad Cafe Web Scraper Module

This module provides functionality to scrape graduate admissions data from The Grad Cafe.
It uses urllib for HTTP requests and BeautifulSoup for HTML parsing.

Author: Student
Date: 2026-02-01
"""

import urllib.request
import urllib.error
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
import ssl


class GradCafeScraper:
    """
    A class to scrape graduate admissions data from The Grad Cafe website.
    
    This scraper extracts applicant data including program, university, status,
    scores, and other relevant information from applicant postings.
    """
    
    def __init__(self, base_url: str = "https://www.thegradcafe.com/survey/index.php"):
        """
        Initialize the scraper with the base URL of Grad Cafe.
        
        Args:
            base_url: The base URL for Grad Cafe survey
        """
        self.base_url = base_url
        self.data = []
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.request_delay = 2  # seconds between requests to be respectful
        self.result_base_url = "https://www.thegradcafe.com"
        self.found_urls = set()  # Track all URLs found on survey pages
        self.processed_urls = set()  # Track which URLs have been processed
        self.edge_cases = []  # Log entries that failed standard parsing
        
    def scrape_data(self, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrape applicant data from Grad Cafe.
        
        This method fetches multiple pages of applicant postings and extracts
        structured data from each entry.
        
        Args:
            max_pages: Maximum number of pages to scrape (None for all available)
            
        Returns:
            List of dictionaries containing applicant data
        """
        print("Starting Grad Cafe scraper...")
        page = 0
        
        while True:
            try:
                # Construct URL with page parameter
                page_url = f"{self.base_url}?page={page}"
                print(f"Scraping page {page}: {page_url}")
                
                # Fetch the page
                html_content = self._fetch_page(page_url)
                if not html_content:
                    print(f"No content retrieved for page {page}. Stopping.")
                    break
                
                # Parse the HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all applicant entries - try multiple selectors
                entries = soup.find_all('tr', class_='tr_')
                
                # If no entries with 'tr_' class, try alternative selectors
                if not entries:
                    # Try finding all tr elements in the main table
                    table = soup.find('table', class_='table')
                    if table:
                        entries = table.find_all('tr')[1:]  # Skip header row
                    
                if not entries:
                    # Try any table with survey data
                    tables = soup.find_all('table')
                    if tables and len(tables) > 0:
                        # Usually the data is in one of the first few tables
                        for table in tables[:3]:
                            candidate_rows = table.find_all('tr')[1:]
                            if candidate_rows and len(candidate_rows) > 0:
                                entries = candidate_rows
                                break
                
                if not entries:
                    print(f"No entries found on page {page}. Stopping.")
                    break
                
                # Extract data from each entry
                page_data = self._parse_entries(entries)
                if page_data:
                    self.data.extend(page_data)
                    print(f"Extracted {len(page_data)} entries from page {page}. Total: {len(self.data)}")
                else:
                    print(f"Failed to parse entries on page {page}. Stopping.")
                    break
                
                # Also scan the page for any result URLs that might have been missed
                # This catches edge cases with unusual HTML structures
                self._find_all_result_urls(html_content)
                
                # Check if we've reached max pages
                if max_pages and page >= max_pages - 1:
                    print(f"Reached maximum pages ({max_pages}). Stopping.")
                    break
                
                page += 1
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"Error on page {page}: {str(e)}")
                break
        
        # Recover edge case entries that failed standard parsing
        self._recover_edge_cases()
        
        print(f"Scraping complete. Total entries: {len(self.data)}")
        if self.edge_cases:
            print(f"Edge cases encountered: {len(self.edge_cases)}")
            print(f"  Successfully recovered: {sum(1 for e in self.edge_cases if e['recovered'])}")
            print(f"  Failed recovery: {sum(1 for e in self.edge_cases if not e['recovered'])}")
        
        return self.data
    
    def _find_all_result_urls(self, html_content: str) -> None:
        """
        Scan page HTML for all result page URLs.
        This catches entries with unusual HTML structures that might be missed by table parsing.
        
        Args:
            html_content: Raw HTML content of survey page
        """
        try:
            # Find all links to result pages: /result/[0-9]+
            result_pattern = r'https?://www\.thegradcafe\.com/result/(\d+)'
            matches = re.findall(result_pattern, html_content, re.IGNORECASE)
            
            for match in matches:
                url = f"https://www.thegradcafe.com/result/{match}"
                self.found_urls.add(url)
        except Exception:
            pass
    
    def _recover_edge_cases(self) -> None:
        """
        Attempt to recover edge case entries that failed standard parsing.
        
        This method:
        1. Identifies URLs found on survey pages but not processed
        2. Fetches each URL and attempts to reconstruct entry data
        3. Logs success/failure for transparency
        
        Edge cases typically occur when:
        - HTML structure doesn't match expected patterns
        - University/program in unusual HTML elements
        - Malformed or incomplete entry HTML
        """
        # Find URLs that were discovered but not processed
        unprocessed_urls = self.found_urls - self.processed_urls
        
        if not unprocessed_urls:
            return
        
        print(f"\nAttempting to recover {len(unprocessed_urls)} edge case entries...")
        
        recovered_count = 0
        for url in unprocessed_urls:
            try:
                # Fetch the full result page
                html_content = self._fetch_page(url)
                if not html_content:
                    continue
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Try to extract basic info from the result page
                entry_data = self._extract_entry_from_result_page(url, soup)
                
                if entry_data and (entry_data.get('university') or entry_data.get('program')):
                    # Try to get detailed data as well
                    detailed = self._fetch_detailed_data(url)
                    if detailed:
                        entry_data.update(detailed)
                    
                    self.data.append(entry_data)
                    recovered_count += 1
                    
                    # Update edge case log
                    for edge in self.edge_cases:
                        if edge['url'] == url:
                            edge['recovered'] = True
                            break
                    
                    print(f"  ✓ Recovered: {url}")
                
                time.sleep(self.request_delay)
            except Exception as e:
                # Silently continue
                continue
        
        if recovered_count > 0:
            print(f"Successfully recovered {recovered_count} edge case entries")
    
    def _extract_entry_from_result_page(self, url: str, soup) -> Optional[Dict]:
        """
        Extract entry data directly from a result page (fallback method).
        This is used when standard row parsing fails.
        
        Args:
            url: The result page URL
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with entry data, or None if extraction fails
        """
        try:
            entry = {
                'university': None,
                'program': None,
                'degree': None,
                'applicant_status': None,
                'status_date': 'February 01, 2026',  # Default fallback
                'comments': None,
                'comments_date': None,
                'season': None,
                'GRE_Verbal': 0,
                'GRE_Quantitative': 0,
                'GRE_General': 0,
                'GRE_Analytical_Writing': 0.0,
                'GPA': 0.0,
                'comments_full': None,
                'url': url,
                'data_added_date': datetime.now().isoformat(),
                'degrees_country_of_origin': None,
            }
            
            text = soup.get_text()
            
            # Try to find university - look for common patterns
            uni_patterns = [
                r'(?:University|University of|College|Institute)\s+(?:of\s+)?([^:\n]+?)(?:\n|:)',
            ]
            for pattern in uni_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entry['university'] = self._clean_text(match.group(1))
                    break
            
            # Try to find program name - usually after university
            # Look for text between common program indicators
            if entry['university']:
                # Find program after university mention
                uni_pos = text.find(entry['university'])
                if uni_pos >= 0:
                    program_section = text[uni_pos:uni_pos+500]
                    # Look for program on new line or after delimiter
                    program_match = re.search(r'\n\s*([A-Z][^:\n]{5,60}?)(?:\n|:)', program_section)
                    if program_match:
                        entry['program'] = self._clean_text(program_match.group(1))
            
            # If still no program, try generic pattern
            if not entry['program']:
                # Look for capitalized text that looks like a program
                program_match = re.search(r'(?:Program|Major)[\s:]+([^:\n]+?)(?:\n|$)', text, re.IGNORECASE)
                if program_match:
                    entry['program'] = self._clean_text(program_match.group(1))
            
            # Extract degree
            if 'phd' in text.lower():
                entry['degree'] = 'PhD'
            elif 'master' in text.lower() or 'ma ' in text.lower():
                entry['degree'] = 'Masters'
            elif 'doctoral' in text.lower():
                entry['degree'] = 'PhD'
            
            # Extract status
            status_keywords = {
                'Accepted': ['accept', 'admitted'],
                'Rejected': ['reject', 'denied', 'declined'],
                'Interview': ['interview', 'interview phase'],
                'Waitlisted': ['waitlist', 'waitlisted'],
                'Pending': ['pending', 'under review']
            }
            for status, keywords in status_keywords.items():
                for keyword in keywords:
                    if keyword in text.lower():
                        entry['applicant_status'] = status
                        break
                if entry['applicant_status']:
                    break
            
            return entry
            
        except Exception as e:
            return None
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a single page from Grad Cafe.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        try:
            # Create SSL context that doesn't verify certificates
            # This is needed on some systems where SSL certificates aren't properly installed
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            request = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )
            with urllib.request.urlopen(request, timeout=10, context=ssl_context) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.URLError as e:
            print(f"URL Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def _parse_entries(self, entries) -> List[Dict]:
        """
        Parse HTML entries into structured data.
        Track all URLs found and recover edge cases afterward.
        
        Args:
            entries: BeautifulSoup ResultSet of entry elements
            
        Returns:
            List of parsed entry dictionaries
        """
        parsed_entries = []
        
        for entry in entries:
            try:
                # First, track the URL if this entry has one (for edge case recovery)
                url = self._extract_url(entry)
                if url:
                    self.found_urls.add(url)
                
                data = self._extract_entry_data(entry)
                if data:
                    # Fetch detailed data from result page to get GRE scores, GPA, and season
                    # This fetches each result page to extract additional information
                    if data.get('url'):
                        detailed = self._fetch_detailed_data(data['url'])
                        if detailed:
                            data.update(detailed)
                        time.sleep(self.request_delay)
                        self.processed_urls.add(data['url'])
                    
                    parsed_entries.append(data)
                elif url:
                    # Entry parsing failed but URL was found - log as edge case
                    self.edge_cases.append({
                        'url': url,
                        'reason': 'Failed standard parsing (unusual HTML structure)',
                        'recovered': False
                    })
            except Exception as e:
                print(f"Error parsing entry: {str(e)}")
                continue
        
        return parsed_entries
    
    def _extract_entry_data(self, entry) -> Optional[Dict]:
        """
        Extract data from a single entry element.
        
        The current Grad Cafe uses Tailwind CSS classes and nested divs.
        Structure: tr -> td -> div with actual content
        
        Args:
            entry: BeautifulSoup element representing one applicant entry (tr)
            
        Returns:
            Dictionary with structured applicant data, or None if parsing fails
        """
        try:
            # Find all cells in the row
            cells = entry.find_all('td')
            
            # Filter out empty cells
            cells = [c for c in cells if c.get_text(strip=True)]
            
            # Need at least 3 cells to process
            if len(cells) < 3:
                return None
            
            # Extract data based on current Grad Cafe structure
            # The structure is typically: [University/Program] [Program/Degree] [Date] [Status] [Comments/Actions]
            
            data = {}
            
            # Cell 0: University and Program info
            if len(cells) > 0:
                cell0_text = cells[0].get_text(strip=True)
                # University is in a div.tw-font-medium
                uni_div = cells[0].find('div', class_='tw-font-medium')
                data['university'] = self._clean_text(uni_div.get_text() if uni_div else cell0_text)
                data['program'] = None
            
            # Cell 1: Program details (program name and degree)
            if len(cells) > 1:
                cell1_text = cells[1].get_text(strip=True)
                # Program and degree are often separated by a bullet point (•) or SVG
                # "Medical Physics • PhD" -> split on this pattern
                program_text = cell1_text.split('•')[0].strip() if '•' in cell1_text else cell1_text
                
                # Extract spans for cleaner data
                spans = cells[1].find_all('span')
                if len(spans) >= 1:
                    data['program'] = self._clean_text(spans[0].get_text())
                else:
                    data['program'] = self._clean_text(program_text.split('\n')[0])
                
                # Extract degree
                if 'phd' in cell1_text.lower() or 'doctorate' in cell1_text.lower():
                    data['degree'] = 'PhD'
                elif 'master' in cell1_text.lower() or 'ma' in cell1_text.lower() or 'ms' in cell1_text.lower():
                    data['degree'] = 'Masters'
                elif len(spans) >= 2:
                    data['degree'] = self._extract_degree(spans[-1].get_text())
                else:
                    data['degree'] = None
            
            # Cell 2: Date (typically decision/added date)
            if len(cells) > 2:
                data['status_date'] = self._extract_date(cells[2].get_text())
            
            # Cell 3: Status (Accepted, Rejected, Interview, etc.)
            if len(cells) > 3:
                status_text = cells[3].get_text(strip=True)
                data['applicant_status'] = self._extract_status(status_text)
            
            # Additional fields with defaults
            data['comments'] = None
            data['comments_date'] = None
            data['season'] = None
            data['GRE_Verbal'] = 0
            data['GRE_Quantitative'] = 0
            data['GRE_General'] = 0
            data['GRE_Analytical_Writing'] = 0.0
            data['GPA'] = 0.0
            data['comments_full'] = None
            data['url'] = self._extract_url(entry)
            data['data_added_date'] = datetime.now().isoformat()
            data['degrees_country_of_origin'] = None
            
            # Accept entry if it has EITHER university OR program (more lenient)
            # AND has a URL (so we can fetch details later)
            if (data.get('university') or data.get('program')) and data.get('url'):
                return data
            
            # Accept if we have url even with minimal info (edge case recovery)
            if data.get('url'):
                return data
            
            return None
            
        except Exception as e:
            print(f"Error extracting entry data: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> Optional[str]:
        """
        Clean and normalize text from HTML elements.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text or None if empty
        """
        if not text:
            return None
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        # Remove common HTML remnants
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        return cleaned.strip() if cleaned.strip() else None
    
    def _extract_status(self, text: str) -> Optional[str]:
        """
        Extract applicant status (Accepted, Rejected, Waitlisted, etc.).
        
        Args:
            text: Raw status text
            
        Returns:
            Standardized status string
        """
        text = text.lower().strip()
        if 'accept' in text:
            return 'Accepted'
        elif 'reject' in text:
            return 'Rejected'
        elif 'waitlist' in text:
            return 'Waitlisted'
        elif 'interview' in text:
            return 'Interview'
        elif 'pending' in text:
            return 'Pending'
        else:
            return text if text else None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """
        Extract and standardize dates from text.
        
        Args:
            text: Raw date text
            
        Returns:
            Standardized date string or None
        """
        text = self._clean_text(text)
        if not text:
            return None
        # Match various date formats
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|([A-Za-z]+ \d{1,2}, \d{4})'
        match = re.search(date_pattern, text)
        return match.group(0) if match else None
    
    def _extract_score(self, text: str) -> int:
        """
        Extract numerical GRE scores.
        
        Args:
            text: Raw score text
            
        Returns:
            Integer score, or 0 if not found
        """
        text = self._clean_text(text)
        if not text:
            return 0
        # Match integer scores (typically 130-170 for new GRE)
        match = re.search(r'\b(\d{2,3})\b', text)
        if match:
            score = int(match.group(1))
            return score
        return 0
    
    def _extract_aw_score(self, text: str) -> float:
        """
        Extract GRE Analytical Writing scores.
        
        Args:
            text: Raw AW score text
            
        Returns:
            Float score, or 0.0 if not found
        """
        text = self._clean_text(text)
        if not text:
            return 0.0
        # Match decimal scores (typically 0-6)
        match = re.search(r'\b([0-6](?:\.\d)?)\b', text)
        if match:
            score = float(match.group(1))
            return score
        return 0.0
    
    def _extract_gpa(self, text: str) -> float:
        """
        Extract GPA values.
        
        Args:
            text: Raw GPA text
            
        Returns:
            Float GPA, or 0.0 if not found
        """
        text = self._clean_text(text)
        if not text:
            return 0.0
        # Match GPA format (typically 0.0 to 4.0)
        match = re.search(r'\b([0-4](?:\.\d{1,2})?)\b', text)
        if match:
            gpa = float(match.group(1))
            return gpa
        return 0.0
    
    def _extract_degree(self, text: str) -> Optional[str]:
        """
        Extract degree type (Masters, PhD).
        
        Args:
            text: Raw degree text
            
        Returns:
            Standardized degree type
        """
        text = text.lower().strip()
        if 'phd' in text or 'doctorate' in text or 'phd/md' in text:
            return 'PhD'
        elif 'master' in text or 'ma' in text or 'ms' in text or 'msc' in text:
            return 'Masters'
        else:
            return text if text else None
    
    def _extract_international_status(self, comments: str) -> Optional[str]:
        """
        Infer international status from comments.
        
        Args:
            comments: Comment text
            
        Returns:
            'International' or 'American' or None
        """
        if not comments:
            return None
        comments_lower = comments.lower()
        if 'international' in comments_lower:
            return 'International'
        elif 'us' in comments_lower or 'american' in comments_lower or 'usa' in comments_lower:
            return 'American'
        return None
    
    def _extract_url(self, entry) -> Optional[str]:
        """
        Extract the URL link to the applicant entry.
        
        Args:
            entry: BeautifulSoup entry element
            
        Returns:
            URL string or None
        """
        try:
            link = entry.find('a', href=True)
            if link:
                href = link.get('href')
                # Make it absolute URL if needed
                if href and not href.startswith('http'):
                    return urljoin(self.result_base_url, href)
                return href
        except Exception:
            pass
        return None
    
    def _fetch_detailed_data(self, url: str) -> Optional[Dict]:
        """
        Fetch detailed data from an individual result page.
        
        This method attempts to extract GRE scores, GPA, comments, and other
        detailed information from the full result page.
        
        Patterns Updated (Feb 2026):
        - Handles flexible whitespace between labels and values (newlines, tabs)
        - Supports "Undergrad GPA" format (without colon)
        - Extracts Analytical Writing as decimal (3.50)
        - Handles both "GRE Verbal:" and "Verbal:" formats
        - Tested against actual result pages (e.g., result/994245)
        
        Note: GRE Quantitative may not always be available separately.
        Some pages show only "GRE General: 332" (combined V+Q score).
        When only General score is shown, GRE_Quantitative remains 0.
        
        Args:
            url: URL to the individual result page
            
        Returns:
            Dictionary with additional detailed fields or None
        """
        if not url:
            return None
        
        try:
            html_content = self._fetch_page(url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            details = {
                'GRE_Verbal': 0,
                'GRE_Quantitative': 0,
                'GRE_General': 0,
                'GRE_Analytical_Writing': 0.0,
                'GPA': 0.0,
                'season': None,
                'comments': None,
                'degrees_country_of_origin': None,
            }
            
            # Extract text content
            text = soup.get_text()
            
            # Look for GRE scores - try multiple patterns including whitespace handling
            # Pattern 1: "GRE Verbal: 165" with flexible whitespace
            gre_v_match = re.search(r'GRE\s+Verbal\s*:\s*(\d{2,3})', text, re.IGNORECASE)
            if not gre_v_match:
                # Pattern 2: Just "Verbal: 165" (with more flexible whitespace)
                gre_v_match = re.search(r'(?<!GRE\s)Verbal\s*:\s*(\d{2,3})', text, re.IGNORECASE)
            if gre_v_match:
                score = int(gre_v_match.group(1))
                details['GRE_Verbal'] = score
            
            # Pattern for GRE Quantitative or GRE General
            # First look for explicit "Quantitative: 160"
            gre_q_match = re.search(r'(?:GRE\s+)?Quantitative\s*:\s*(\d{2,3})', text, re.IGNORECASE)
            if not gre_q_match:
                # Try "Quant: 160"
                gre_q_match = re.search(r'Quant\s*:\s*(\d{2,3})', text, re.IGNORECASE)
            if gre_q_match:
                score = int(gre_q_match.group(1))
                details['GRE_Quantitative'] = score
            else:
                # If Quantitative not found, look for GRE General (combined V+Q score)
                gre_general_match = re.search(r'GRE\s+General\s*:\s*(\d{2,3})', text, re.IGNORECASE)
                if gre_general_match:
                    score = int(gre_general_match.group(1))
                    details['GRE_General'] = score
            
            # Pattern for GRE Analytical Writing: "Analytical Writing: 4.5"
            gre_aw_match = re.search(r'Analytical\s+Writing\s*:\s*(\d+\.\d+)', text, re.IGNORECASE)
            if not gre_aw_match:
                # Try "AW: 4.5" pattern
                gre_aw_match = re.search(r'\bAW\s*:\s*([0-6](?:\.\d+)?)', text, re.IGNORECASE)
            if gre_aw_match:
                try:
                    score = float(gre_aw_match.group(1))
                    details['GRE_Analytical_Writing'] = score
                except ValueError:
                    pass
            
            # Look for GPA - multiple patterns with flexible whitespace
            # Pattern 1: "Undergrad GPA" followed by number (allows whitespace/newlines between)
            gpa_match = re.search(r'Undergrad\s+GPA\s*[:\s]*([0-4](?:\.\d{1,2})?)', text, re.IGNORECASE)
            if not gpa_match:
                # Pattern 2: Just "GPA: 3.95"
                gpa_match = re.search(r'GPA\s*:\s*([0-4](?:\.\d{1,2})?)', text, re.IGNORECASE)
            if gpa_match:
                gpa = float(gpa_match.group(1))
                details['GPA'] = gpa
            
            # Look for season
            season_match = re.search(r'(Fall|Spring|Summer|Winter)', text)
            print("Test !")
            print(season_match)
            if season_match:
                details['season'] = f"{season_match.group(1)} {season_match.group(2)}"
            
            # Look for comments
            comments_section = soup.find(string=re.compile(r'comment', re.IGNORECASE))
            if comments_section:
                parent = comments_section.find_parent()
                if parent:
                    comments_text = parent.get_text(strip=True)
                    details['comments'] = self._clean_text(comments_text[:500])
            
            # Check for Degree's Country of Origin
            # Look for explicit label "Degree's Country of Origin: ..."
            country_match = re.search(r"Degree'?s?\s+Country\s+of\s+Origin\s*:\s*([^\n]+)", text, re.IGNORECASE)
            if country_match:
                details['degrees_country_of_origin'] = self._clean_text(country_match.group(1))
            elif 'international' in text.lower():
                details['degrees_country_of_origin'] = 'International'
            elif 'us' in text.lower() or 'usa' in text.lower():
                details['degrees_country_of_origin'] = 'American'
            
            return details
            
        except Exception as e:
            # Silently fail - detailed data is optional
            return None
    
    def save_data(self, filename: str = 'raw_data.json') -> bool:
        """
        Save scraped data to a JSON file in sample_data.json format.
        
        Format:
        {
            "university": "University Name",
            "program": "Program Name",
            "status": "Accepted|Rejected|Wait listed",
            "term": "Date or semester info",
            "date_added": "Added on YYYY-MM-DD",
            "url": "URL to Grad Cafe entry",
            "US/International": "American|International",
            "Degree": "Masters|PhD|etc",
            "GPA": "GPA X.XX",
            "comments": "User comments"
        }
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            formatted_data = []
            
            for entry in self.data:
                # Start with empty output entry
                output = {}
                
                # Combine university and program into single "program" field
                university = entry.get('university')
                program = entry.get('program')
                output['program'] = program
                if university:
                    output['university'] = university
                if program:
                    output['program'] = program
                
                # Map applicant_status to status
                status = entry.get('applicant_status')
                if status:
                    output['status'] = status
                
                # Map status_date to term
                # term = entry.get('status_date')
                # if term:
                #     output['term'] = term
                
                # Map data_added_date to date_added with formatting
                data_added = entry.get('data_added_date')
                if data_added:
                    # Format as "Added on YYYY-MM-DD"
                    if isinstance(data_added, str):
                        # Extract just the date part if it's a timestamp
                        date_part = data_added.split('T')[0] if 'T' in data_added else data_added
                        output['date_added'] = f"Added on {date_part}"
                    else:
                        output['date_added'] = f"Added on {data_added}"
                
                # URL
                url = entry.get('url')
                if url:
                    output['url'] = url
                
                # Map degrees_country_of_origin to US/International
                country = entry.get('degrees_country_of_origin')
                if country:
                    output['US/International'] = country
                
                # Degree
                degree = entry.get('degree')
                if degree:
                    output['Degree'] = degree
                
                # GPA - format as "GPA X.XX" string if numeric
                gpa = entry.get('GPA')
                if gpa and gpa !=0:
                   output['GPA'] = gpa
                # Comments (default to empty string if missing)

                comments = entry.get('comments')
                if comments:
                    output['comments'] = comments
                
                gre_verbal = entry.get('GRE_Verbal')
                if gre_verbal and gre_verbal !=0:
                    output['GRE Verbal'] = gre_verbal
                
                gre_quantitative = entry.get('GRE_Quantitative')
                if gre_quantitative and gre_quantitative !=0:
                    output['GRE Quantitative'] = gre_quantitative
                
                gre_general = entry.get('GRE_General')
                if gre_general and gre_general !=0:
                    output['GRE General'] = gre_general
                
                gre_aw = entry.get('GRE_Analytical_Writing')
                if gre_aw and gre_aw !=0.0:
                    output['GRE Analytical Writing'] = gre_aw
                
                # Season - add if available
                season = entry.get('season')
                if season:
                    output['season'] = season
                
                formatted_data.append(output)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False
    
    def load_data(self, filename: str) -> bool:
        """
        Load previously scraped data from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Data loaded from {filename}. Total entries: {len(self.data)}")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False


def main():
    """Main entry point for the scraper."""
    scraper = GradCafeScraper()
    
    # Scrape data (set max_pages to a smaller number for testing)
    # For full data, set max_pages=None
    # Each page has ~20 entries, so:
    # - 1 page = ~20 entries (quick test)
    # - 50 pages = ~1,000 entries (medium test, ~3-5 min)
    # - 150 pages = ~3,000 entries (~10 min)
    # - 1500 pages = 30,000+ entries (~6-10 hours)
    
    # Uncomment the desired scraping strategy:
    
    # Option 1: Quick test (1 page = ~20 entries)
    scraper.scrape_data(max_pages=1)
    
    # Option 2: Medium collection (50 pages = ~1,000 entries, ~3-5 min)
    # scraper.scrape_data(max_pages=50)
    
    # Option 3: Full collection (150 pages = ~3,000 entries, ~10 min)
    # scraper.scrape_data(max_pages=150)
    
    # Option 4: Complete collection (1500+ pages = 30,000+ entries, ~6-10 hours)
    # scraper.scrape_data(max_pages=None)
    
    # Save the raw scraped data to applicant_data.json
    scraper.save_data('applicant_data.json')
    
    print(f"\nScraping complete!")
    print(f"Total entries collected: {len(scraper.data)}")


if __name__ == "__main__":
    main()
