# Module 4 Test Suite Summary

## Test Coverage

This test suite provides comprehensive coverage of the GradCafe Analysis Application.

### Test Files

1. **test_flask_page.py** - Web interface tests (@pytest.mark.web)
   - App factory pattern
   - Route existence
   - Page rendering
   - Button presence
   - Required text elements

2. **test_buttons.py** - Button behavior tests (@pytest.mark.buttons)
   - Pull data endpoint
   - Update analysis endpoint
   - Busy-state handling (409 responses)
   - Concurrency control

3. **test_analysis_format.py** - Formatting tests (@pytest.mark.analysis)
   - Answer labels
   - Percentage formatting (XX.XX%)
   - Consistent display

4. **test_db_insert.py** - Database tests (@pytest.mark.db)
   - Row insertion
   - Required fields
   - Idempotency
   - Uniqueness constraints
   - Query result format

5. **test_integration_end_to_end.py** - Integration tests (@pytest.mark.integration)
   - Pull -> Update -> Render flow
   - Multiple pulls with overlapping data
   - Busy state during operations

6. **test_query_functions.py** - Query function tests (@pytest.mark.db)
   - All 11 question functions
   - run_all_queries
   - Database connection

7. **test_data_updater.py** - Data transformation tests (@pytest.mark.db)
   - Date parsing
   - Numeric extraction
   - String cleaning
   - URL tracking

8. **test_load_data.py** - Data loading tests (@pytest.mark.db)
   - Table creation
   - Data insertion
   - Date handling

9. **test_setup_databases.py** - Setup utility tests (@pytest.mark.db)
   - Command execution
   - Error handling

### Running Tests

```bash
# Run all tests
pytest -m "web or buttons or analysis or db or integration"

# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=100

# Generate coverage report
pytest --cov=src --cov-report=term > coverage_summary.txt
```

### Coverage Requirements

- **Target**: 100% code coverage
- **Tool**: pytest-cov
- **Report**: coverage_summary.txt

### Test Markers

All tests must have at least one marker:
- `web`: Flask route/page tests
- `buttons`: Button endpoints & busy-state behavior
- `analysis`: Formatting/rounding of analysis output
- `db`: Database schema/inserts/selects
- `integration`: End-to-end flows

### CI/CD

GitHub Actions workflow automatically runs tests on push/PR.

Location: `.github/workflows/tests.yml`

## Documentation

Sphinx documentation is available in `docs/`:

```bash
cd docs
make html
open _build/html/index.html
```

## Notes

- All tests use mocking for external dependencies
- Database tests use `gradcafe_test` database
- No tests depend on live internet or long-running operations
- Tests are fast (< 5 seconds total)
- No unmarked tests (policy enforced)
