@echo off
setlocal

cd /d "%~dp0\.."
if errorlevel 1 goto :fallo

set "PROJECT_DIR=%CD%"

if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
  python -m venv "%PROJECT_DIR%\.venv"
  if errorlevel 1 goto :fallo
)

call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
if errorlevel 1 goto :fallo

python -m pip install --upgrade pip
if errorlevel 1 goto :fallo

pip install -r "%PROJECT_DIR%\requirements.txt"
if errorlevel 1 goto :fallo

python -m herramientas.auditar_completitud_producto
if errorlevel 1 goto :fallo

pytest -q --maxfail=1
if errorlevel 1 goto :fallo

pytest --cov=. --cov-report=term-missing --cov-fail-under=85
if errorlevel 1 goto :fallo

echo PRODUCTO VALIDADO 100%
exit /b 0

:fallo
echo VALIDACIÓN FALLIDA
exit /b 1
