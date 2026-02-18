@echo off
setlocal

cd /d "%~dp0\.."

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
if errorlevel 1 exit /b 1

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

pip install -r requirements.txt
if errorlevel 1 exit /b 1

python -m presentacion
exit /b %errorlevel%
