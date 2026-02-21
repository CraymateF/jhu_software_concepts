# Pylint Usage and Verification for Module 5

## How to Run Pylint

### Quick Command (Recommended)

From the `module_5/` directory:

```bash
./venv/bin/pylint src/*.py --fail-under=10 --max-line-length=120
```

### Alternative: Activated Virtual Environment

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pylint src/*.py --fail-under=10 --max-line-length=120
```

### What This Command Does

- `src/*.py` - Lints all Python files in the src/ directory
- `--fail-under=10` - Requires a score of at least 10/10 (exits with error if lower)
- `--max-line-length=120` - Allows lines up to 120 characters (matches our .pylintrc)

## Expected Output

When all issues are fixed, you should see:

```
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

**Exit code:** 0 (success)

## Configuration

Pylint is configured via `.pylintrc` in the module_5/ root directory:

```ini
[MASTER]
init-hook='import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), "src", "module_2_code"))'

[MESSAGES CONTROL]
disable=
    duplicate-code,
    import-error

[FORMAT]
max-line-length=120

[DESIGN]
max-locals=50
max-statements=120
max-branches=20
max-attributes=15
```

This configuration:
- Adds module_2_code to the Python path (for imports)
- Disables duplicate-code warnings (intentional code reuse)
- Ignores import errors for module_2_code (dynamic path)
- Allows longer lines (120 chars) for readability
- Relaxes design constraints for data processing functions

## Files Linted

All Python files in `src/`:
- `app.py` - Flask application
- `query_data.py` - Database query functions
- `data_updater.py` - Scraping and updating logic
- `load_data.py` - Data loading utilities
- `setup_databases.py` - Database setup script
- `__init__.py` - Package initialization

## Common Issues Fixed

### Trailing Whitespace
**Issue:** Lines ending with spaces or tabs  
**Fix:** Removed all trailing whitespace

### Import Order
**Issue:** Imports not grouped standard → third-party → local  
**Fix:** Reorganized imports:
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import psycopg2
from flask import Flask

# Local
from query_data import run_all_queries
```

### Missing Docstrings
**Issue:** Modules missing module-level docstrings  
**Fix:** Added docstrings to all modules:
```python
"""
Module to query GradCafe database and return analysis results.
"""
```

### Long Lines
**Issue:** Lines exceeding 120 characters  
**Fix:** Used line continuation or string formatting:
```python
# Before (too long)
return {"question": "How many entries from 2026 are acceptances for Georgetown/MIT/Stanford/CMU PhD in CS?"}

# After (split appropriately)
return {
    "question": (
        "How many entries from 2026 are acceptances for "
        "Georgetown/MIT/Stanford/CMU PhD in CS?"
    )
}
```

### Broad Exception Catching
**Issue:** Catching `Exception` without specificity  
**Fix:** Added pylint disable comments where appropriate:
```python
except Exception as exc:  # pylint: disable=broad-exception-caught
    print(f"Error: {exc}")
```

### Variable Redefinition
**Issue:** Variable names reused from outer scope  
**Fix:** Renamed variables to avoid conflicts:
```python
# Before
def main():
    results = run_queries()
    for key, result in results.items():  # 'result' redefines outer scope
        ...

# After  
def main():
    all_results = run_queries()
    for key, query_result in all_results.items():
        ...
```

## Verification in CI/CD

The GitHub Actions workflow enforces Pylint 10/10:

```yaml
- name: Run Pylint (10/10 Required)
  run: |
    pylint src/*.py --fail-under=10 --max-line-length=120
```

If the score drops below 10/10, the build will fail, preventing merge.

## Troubleshooting

### Issue: "No module named 'scrape'"
**Solution:** The `.pylintrc` init-hook should handle this. Verify the file exists.

### Issue: "considered for refactoring"
**Solution:** These are INFO messages, not errors. They don't affect the score.

### Issue: Score is 9.98/10
**Solution:** There's still a small issue. Run without `--fail-under` to see all messages:
```bash
pylint src/*.py --max-line-length=120
```

### Issue: "Import outside toplevel"
**Solution:** For dynamic imports after sys.path modification, use:
```python
# pylint: disable=wrong-import-position
from scrape import GradCafeScraper
# pylint: enable=wrong-import-position
```

## Best Practices

1. **Run Pylint frequently** during development to catch issues early
2. **Use the same command** as CI/CD to ensure consistency  
3. **Keep .pylintrc in version control** so all developers use the same rules
4. **Don't disable warnings globally** - only use inline comments where truly necessary
5. **Aim for 10/10** - it's achievable and ensures high code quality

## Score Breakdown

Pylint scores are calculated as:
```
10.0 - (number_of_errors + number_of_warnings) / number_of_statements
```

To maintain 10/10:
- **0 errors** - Critical issues that must be fixed
- **0 warnings** - Style/convention issues that should be fixed

## Additional Resources

- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Pylint Message Reference](https://pylint.pycqa.org/en/latest/messages/messages_overview.html)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)

---

**Last Verified:** February 21, 2026  
**Score Achieved:** **10.00/10** ✓
