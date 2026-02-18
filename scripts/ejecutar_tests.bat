@echo off
setlocal

cd /d "%~dp0\.."
if errorlevel 1 (
  echo FALLOS EN TESTS
  exit /b 1
)

set "PROJECT_DIR=%CD%"

if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
  python -m venv "%PROJECT_DIR%\.venv"
  if errorlevel 1 (
    echo FALLOS EN TESTS
    exit /b 1
  )
)

call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
if errorlevel 1 (
  echo FALLOS EN TESTS
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 (
  echo FALLOS EN TESTS
  exit /b 1
)

pip install -r "%PROJECT_DIR%\requirements.txt"
if errorlevel 1 (
  echo FALLOS EN TESTS
  exit /b 1
)

pytest -q --maxfail=1 --cov=. --cov-report=term-missing --cov-fail-under=85
set "TEST_EXIT=%ERRORLEVEL%"

if "%TEST_EXIT%"=="0" (
  echo TODO OK
  exit /b 0
) else (
  echo FALLOS EN TESTS
  exit /b 1
)
