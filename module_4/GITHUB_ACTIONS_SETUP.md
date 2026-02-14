# GitHub Actions Setup Instructions

## Overview

The GitHub Actions workflow (`.github/workflows/tests.yml`) automatically runs the test suite when you push to the repository.

## What the Workflow Does

1. Sets up Python 3.10
2. Starts PostgreSQL service
3. Installs dependencies
4. Creates test databases
5. Runs pytest with all markers
6. Generates coverage report

## Steps to Get It Working

### 1. Commit and Push Your Code

```bash
cd /Users/fadetoblack/repo/jhu_software_concepts
git add .
git commit -m "Add Module 4 test suite with 100% coverage"
git push origin main
```

### 2. Check GitHub Actions Tab

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. You should see a workflow run for your latest commit

### 3. Verify Success

The workflow should show:
- ✓ Set up Python
- ✓ Install dependencies
- ✓ Set up test database
- ✓ Run pytest suite
- ✓ Generate coverage report

### 4. Take Screenshot

Once the workflow succeeds:
1. Click on the successful workflow run
2. Take a screenshot showing all green checkmarks
3. Save as `module_4/actions_success.png`

## Troubleshooting

### If Tests Fail in CI

1. **Check the logs**: Click on the failed step to see error details
2. **Run locally first**: Make sure tests pass on your machine
3. **Database issues**: Ensure PostgreSQL connection string is correct
4. **Missing dependencies**: Check if all packages are in requirements.txt

### Common Issues

**Import errors:**
- Make sure `PYTHONPATH` is set correctly in workflow
- Check that all `__init__.py` files exist

**Database connection errors:**
- Verify PostgreSQL service is configured correctly in workflow
- Check database names match (gradcafe_test)

**Coverage below 100%:**
- Run locally: `pytest --cov=src --cov-report=term-missing`
- Add tests for uncovered lines

## Local Testing Before Push

Always test locally before pushing:

```bash
cd module_4

# Create test database
createdb gradcafe_test

# Run tests
pytest -m "web or buttons or analysis or db or integration" \
       --cov=src --cov-report=term-missing --cov-fail-under=100

# If successful, commit and push
```

## After Success

1. Take screenshot of successful GitHub Actions run
2. Save as `module_4/actions_success.png`
3. Commit the screenshot:

```bash
git add module_4/actions_success.png
git commit -m "Add GitHub Actions success screenshot"
git push
```

## Coverage Report

The workflow generates `module_4/coverage_summary.txt` with test results and coverage statistics.

To view it:

```bash
cat module_4/coverage_summary.txt
```

Expected output:
```
============================= test session starts ==============================
...
tests passed
...
---------- coverage: platform linux, python 3.10.x -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/app.py                 50      0   100%
src/query_data.py         150      0   100%
src/load_data.py          100      0   100%
src/data_updater.py       180      0   100%
-----------------------------------------------------
TOTAL                     480      0   100%
```
