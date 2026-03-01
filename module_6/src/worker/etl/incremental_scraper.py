"""
incremental_scraper.py – ETL entry point for incremental GradCafe scraping.

This module wraps GradCafeScraper and GradCafeDataCleaner into a single
callable used by the worker's handle_scrape_new_data handler.
The actual consumer logic lives in consumer.py; this module is kept for
reference and standalone CLI use.
"""
import json
import os
import sys
import tempfile

# Ensure module_2_code is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "module_2_code"))

from scrape import GradCafeScraper       # noqa: E402
from clean import GradCafeDataCleaner    # noqa: E402


def run_incremental_scrape(max_pages: int = 2, since: str | None = None) -> list[dict]:
    """
    Scrape up to *max_pages* pages from GradCafe and clean the results.

    Args:
        max_pages: Maximum number of survey pages to scrape.
        since:     Optional ISO date string; records older than this are
                   discarded (not yet enforced by the scraper itself but
                   used by the consumer's watermark logic).

    Returns:
        List of cleaned record dicts.
    """
    scraper  = GradCafeScraper()
    raw_data = scraper.scrape_data(max_pages=max_pages)

    if not raw_data:
        return []

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(raw_data, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    cleaner      = GradCafeDataCleaner()
    cleaned_data = cleaner.clean_data(tmp_path) or []
    os.unlink(tmp_path)

    if since:
        cleaned_data = [
            r for r in cleaned_data
            if (r.get("date_added") or "") >= since
        ]

    return cleaned_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run an incremental scrape of GradCafe.")
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--since", type=str, default=None,
                        help="ISO date string (YYYY-MM-DD); skip older records.")
    parser.add_argument("--output", type=str, default="incremental_scraped.json")
    args = parser.parse_args()

    results = run_incremental_scrape(max_pages=args.max_pages, since=args.since)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(results)} records to {args.output}")
