"""
Data Cleaning Module for Grad Cafe Data

This module provides functionality to clean and standardize raw Grad Cafe data.
For LLM-based standardization, see llm_hosting/app.py.

Author: Student
Date: 2026-02-01
"""

import json
import re
from typing import List, Dict, Optional, Any


class GradCafeDataCleaner:
    """
    A class to clean and standardize graduate admissions data from Grad Cafe.
    
    Performs data validation and standardization.
    """
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.data = []
        self.cleaned_data = []
        
    def clean_data(self, input_file: str, output_file: str = 'applicant_data.json') -> List[Dict]:
        """
        Load, clean, and save applicant data.
        
        Args:
            input_file: Path to raw JSON data file
            output_file: Path to save cleaned JSON data
            
        Returns:
            List of cleaned data dictionaries
        """
        print(f"Loading data from {input_file}...")
        if not self.load_data(input_file):
            return []
        
        print(f"Cleaning {len(self.data)} entries...")
        
        # Apply basic cleaning to all entries
        self.cleaned_data = [self._clean_entry(entry) for entry in self.data]
        
        print(f"After basic cleaning: {len(self.cleaned_data)} entries")
        
        # Save cleaned data
        self.save_data(self.cleaned_data, output_file)
        
        print(f"Cleaning complete. Saved {len(self.cleaned_data)} entries to {output_file}")
        return self.cleaned_data
    
    def load_data(self, filename: str) -> bool:
        """
        Load raw data from JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Loaded {len(self.data)} entries")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def save_data(self, data: List[Dict], filename: str) -> bool:
        """
        Save cleaned data to JSON file.
        Filters out None/null values and 0/0.0 score values.
        Formats field names (underscore -> space, capitalize each word, GRE/GPA all caps).
        Reorders fields for better organization.
        
        Args:
            data: Data to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Define desired field order for output
            field_order = [
                'university', 'program', 'degree',
                'status', 'term', "date_added",
                'GRE_General', 'GRE_Verbal', 'GRE_Quantitative', 'GRE_Analytical_Writing', 'GPA',
                'degrees_country_of_origin',
                'comments', 'comments_date',
                'url', 'data_added_date', "notes",
            ]
            
            # Format and filter data
            cleaned_data = []
            for entry in data:
                # Filter out None values (null results not displayed)
                filtered = {}
                for k, v in entry.items():
                    if v is None:
                        continue
                    # Skip 0/0.0 for score fields
                    if k in ('GRE_Verbal', 'GRE_Quantitative', 'GRE_General', 'GRE_Analytical_Writing', 'GPA'):
                        if v in (0, 0.0):
                            continue
                    filtered[k] = v
                
                # Reorder fields
                ordered = {}
                for field in field_order:
                    if field in filtered:
                        ordered[field] = filtered[field]
                # Add any remaining fields not in order list
                for field in filtered:
                    if field not in ordered:
                        ordered[field] = filtered[field]
                
                # Format field names
                formatted = {}
                for key, value in ordered.items():
                    # Special handling for specific fields
                    if key == 'degrees_country_of_origin':
                        formatted_key = 'US/International'
                    else:
                        # Replace underscores with spaces and capitalize
                        formatted_key = key.replace('_', ' ').title()
                        # Fix GRE and GPA capitalization
                        if 'Gre' in formatted_key:
                            formatted_key = formatted_key.replace('Gre', 'GRE')
                        if 'Gpa' in formatted_key:
                            formatted_key = formatted_key.replace('Gpa', 'GPA')
                    formatted[formatted_key] = value
                
                cleaned_data.append(formatted)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(cleaned_data)} entries to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False
    
    def _clean_entry(self, entry: Dict) -> Optional[Dict]:
        """
        Apply basic cleaning to a single entry.
        
        Args:
            entry: Raw entry dictionary (may have formatted keys from scraper)
            
        Returns:
            Cleaned entry dictionary, or None if entry is invalid
        """
        try:
            # Handle both formatted keys (from new scraper) and original keys (if re-running)
            # Create a normalized key mapping
            def get_value(entry, *possible_keys):
                for key in possible_keys:
                    if key in entry:
                        return entry[key]
                return None
            
            cleaned = {}
            
            # Program name (may be 'program' or 'Program')
            cleaned['program'] = self._normalize_text(get_value(entry, 'program', 'Program'))
            
            # University name (may be 'university' or 'University')
            cleaned['university'] = self._normalize_text(get_value(entry, 'university', 'University'))
            
            # Status and dates
            cleaned['status'] = get_value(entry, 'status', 'Applicant Status')
            cleaned['date_added'] = get_value(entry, 'date_added', 'Date Addeda')
            
            # Comments
            cleaned['comments'] = self._clean_comments(get_value(entry, 'comments', 'Comments'))
            cleaned['comments_date'] = get_value(entry, 'comments_date', 'Comments Date')
            
            # Program timing
            cleaned['term'] = get_value(entry, 'season', 'Term')
            
            # Degree type
            cleaned['degree'] = get_value(entry, 'degree', 'Degree')
            
            # Scores (no boundary checks, keep as None if not provided)
            cleaned['GRE_Verbal'] = get_value(entry, 'GRE_Verbal', 'GRE Verbal')
            cleaned['GRE_Quantitative'] = get_value(entry, 'GRE_Quantitative', 'GRE Quantitative')
            cleaned['GRE_General'] = get_value(entry, 'GRE_General', 'GRE General')
            cleaned['GRE_Analytical_Writing'] = get_value(entry, 'GRE_Analytical_Writing', 'GRE Analytical Writing')
            cleaned['GPA'] = get_value(entry, 'GPA', 'Gpa')
            
            # Student type
            cleaned['degrees_country_of_origin'] = get_value(entry, 'degrees_country_of_origin', 'Degrees Country Of Origin', 'US/International')
            
            # URL and metadata
            cleaned['url'] = get_value(entry, 'url', 'Url')
            cleaned['data_added_date'] = get_value(entry, 'data_added_date', 'Data Added Date')
            
            return cleaned
            
        except Exception as e:
            print(f"Error cleaning entry: {str(e)}")
            return None
    
    def _normalize_text(self, text: Optional[str]) -> Optional[str]:
        """
        Normalize text by removing HTML, extra whitespace, and special characters.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text or None if empty
        """
        if not text:
            return None
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        
        return text.strip() if text.strip() else None
    
    def _clean_comments(self, comments: Optional[str]) -> Optional[str]:
        """
        Clean comment text, removing HTML and normalizing format.
        
        Args:
            comments: Raw comment text
            
        Returns:
            Cleaned comments or None if empty
        """
        if not comments:
            return None
        
        cleaned = self._normalize_text(comments)
        
        # Remove excessive punctuation
        if cleaned:
            # Keep reasonable length comments
            if len(cleaned) > 5000:
                cleaned = cleaned[:5000] + "..."
        
        return cleaned



def apply_llm_standardization(input_file: str, output_file: Optional[str] = None) -> bool:
    """
    Apply LLM-based standardization to program/university names.
    
    This function standardizes abbreviated or combined program/university names
    using a local LLM and adds two new fields:
    - 'llm-generated-program': Standardized program name
    - 'llm-generated-university': Standardized university name
    
    This requires llm_hosting dependencies to be installed.
    If dependencies are missing, returns False without error.
    
    Args:
        input_file: Path to JSON file with cleaned applicant data
        output_file: Path to save standardized output (defaults to input_file)
        
    Returns:
        True if successful, False if dependencies missing or error occurred
        
    Example:
        >>> from clean import apply_llm_standardization
        >>> apply_llm_standardization('applicant_data.json')
    """
    try:
        import sys
        from pathlib import Path
        
        # Add llm_hosting to path
        llm_dir = Path(__file__).parent / 'llm_hosting'
        if not llm_dir.exists():
            print("⚠️  llm_hosting folder not found")
            return False
        
        sys.path.insert(0, str(llm_dir))
        
        # Try to import LLM functions
        try:
            from app import _call_llm
        except ImportError as e:
            print(f"⚠️  LLM dependencies not installed: {e}")
            print("   To use LLM standardization, run:")
            print("   pip install -r llm_hosting/requirements.txt")
            return False
        
        # Load input data
        input_path = Path(__file__).parent / input_file
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            return False
        
        print(f"Loading {input_file}...")
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("Error: Input must be a JSON array")
            return False
        
        print(f"Applying LLM standardization to {len(data)} entries...")
        print("(This may take several minutes depending on dataset size)")
        
        # Apply standardization to each entry
        standardized_data = []
        for i, entry in enumerate(data):
            # Get program and university from the entry
            # Handle both formatted keys ('Program', 'University') and internal keys
            program = entry.get('Program') or entry.get('program') or ""
            university = entry.get('University') or entry.get('university') or ""
            
            # Combine them as input to LLM (in case they're separated)
            program_text = f"{program}, {university}".strip()
            if program_text.endswith(','):
                program_text = program_text[:-1]
            
            # Call LLM to standardize
            result = _call_llm(program_text)
            
            # Add LLM-generated fields to entry (always present, even if empty)
            entry['LLM Generated Program'] = result.get('standardized_program', "") or ""
            entry['LLM Generated University'] = result.get('standardized_university', "") or ""
            
            standardized_data.append(entry)
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(data)} entries...")
        
        # Determine output file
        if output_file is None:
            output_file = input_file
        
        output_path = Path(__file__).parent / output_file
        
        # Save results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(standardized_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ LLM standardization complete!")
        print(f"   Added 'LLM Generated Program' and 'LLM Generated University' fields")
        print(f"   Saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the data cleaner."""
    cleaner = GradCafeDataCleaner()
    
    # Clean the raw data
    cleaner.clean_data('applicant_data.json')
    
    # Print summary statistics
    print("\n=== Cleaning Summary ===")
    print(f"Total entries cleaned: {len(cleaner.cleaned_data)}")
    
    if cleaner.cleaned_data:
        # Count by status
        statuses = {}
        for entry in cleaner.cleaned_data:
            status = entry.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print("\nEntries by Status:")
        for status, count in sorted(statuses.items()):
            print(f"  {status}: {count}")
        
        # Count by degree
        degrees = {}
        for entry in cleaner.cleaned_data:
            degree = entry.get('degree', 'Unknown')
            degrees[degree] = degrees.get(degree, 0) + 1
        
        print("\nEntries by Degree:")
        for degree, count in sorted(degrees.items()):
            print(f"  {degree}: {count}")

    apply_llm_standardization('applicant_data.json', output_file='llm_extend_applicant_data.json')



if __name__ == "__main__":
    main()