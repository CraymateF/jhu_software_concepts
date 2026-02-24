# Module 5: Software Assurance & Security

This module includes security hardening, dependency analysis, CI enforcement, and SQL injection defenses for the GradCafe analysis app.

## Fresh Install (pip + venv)

```bash
cd module_5
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Fresh Install (uv)

```bash
cd module_5
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip sync requirements.txt
```

## Environment Variables

Copy the template and set your values:

```bash
cp .env.example .env
```

Required variables:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Run App

```bash
cd src
python app.py
```

Then open: `http://127.0.0.1:8080`

## Run Pylint (Required 10/10)

```bash
cd module_5
source venv/bin/activate
pylint src/*.py --fail-under=10 --max-line-length=120
```

Expected result:

```text
Your code has been rated at 10.00/10
```

## Run Tests with Coverage

```bash
cd module_5
source venv/bin/activate
pytest --cov=src --cov-report=term-missing --cov-fail-under=100
```

## Generate Dependency Graph

```bash
cd module_5
source venv/bin/activate
pydeps src/app.py --noshow -T svg -o dependency.svg
```

Output artifact: `dependency.svg`

## Why setup.py is included

`setup.py` makes the project installable, supports editable installs (`pip install -e .`), and improves reproducibility across local environments and CI.
