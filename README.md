# FastAPI Practice

Учебный проект на FastAPI с настроенным CI/CD.

## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
uvicorn main:app --reload

black --check .
isort --check-only .
flake8 .
mypy .
pytest -v

### 4.8. `.github/workflows/ci.yml`

```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: isort
        run: isort --check-only --diff .
      - name: black
        run: black --check --diff .
      - name: flake8
        run: flake8 .
      - name: mypy
        run: mypy .
      - name: pytest
        run: pytest -v
