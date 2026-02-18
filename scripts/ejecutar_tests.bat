@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install -r requirements.txt
pytest --cov=. --cov-report=term-missing --cov-fail-under=85
