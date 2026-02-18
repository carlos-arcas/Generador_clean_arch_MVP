@echo off
setlocal

cd /d "%~dp0\.."

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto fallo

python -m pip install --upgrade pip
if errorlevel 1 goto fallo

pip install -r requirements.txt
if errorlevel 1 goto fallo

pytest -q --maxfail=1
if errorlevel 1 goto fallo

pytest --cov=. --cov-report=term-missing --cov-fail-under=85
if errorlevel 1 goto fallo

echo TODO OK
exit /b 0

:fallo
echo FALLOS EN TESTS
exit /b 1
