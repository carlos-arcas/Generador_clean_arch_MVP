@echo off
setlocal

cd /d "%~dp0\.."
if errorlevel 1 (
  echo [ERROR] No se pudo cambiar al directorio del proyecto.
  pause
  exit /b 1
)

set "PROJECT_DIR=%CD%"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "DEBUG_LOG=%LOG_DIR%\launcher_debug.log"
set "STDOUT_LOG=%LOG_DIR%\launcher_stdout.log"
set "STDERR_LOG=%LOG_DIR%\launcher_stderr.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if errorlevel 1 (
  echo [ERROR] No se pudo crear el directorio de logs.
  pause
  exit /b 1
)

echo =============================================== > "%DEBUG_LOG%"
echo [INFO] Inicio lanzar_app.bat: %DATE% %TIME% >> "%DEBUG_LOG%"
echo [INFO] PROJECT_DIR=%PROJECT_DIR% >> "%DEBUG_LOG%"

if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
  echo [INFO] Creando entorno virtual .venv... >> "%DEBUG_LOG%"
  python -m venv "%PROJECT_DIR%\.venv" >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"
  if errorlevel 1 goto :fail_venv
)

call "%PROJECT_DIR%\.venv\Scripts\activate.bat" >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"
if errorlevel 1 goto :fail_activate

python -m pip install --upgrade pip >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"
if errorlevel 1 goto :fail_pip_upgrade

pip install -r "%PROJECT_DIR%\requirements.txt" >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"
if errorlevel 1 goto :fail_requirements

python -m presentacion >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"
if errorlevel 1 goto :fail_run

echo [INFO] Ejecucion finalizada correctamente. >> "%DEBUG_LOG%"
exit /b 0

:fail_venv
echo [ERROR] Fallo al crear el entorno virtual.
echo [ERROR] Fallo al crear el entorno virtual. Revisa %STDERR_LOG% >> "%DEBUG_LOG%"
pause
exit /b 2

:fail_activate
echo [ERROR] Fallo al activar el entorno virtual.
echo [ERROR] Fallo al activar entorno. Revisa %STDERR_LOG% >> "%DEBUG_LOG%"
pause
exit /b 3

:fail_pip_upgrade
echo [ERROR] Fallo al actualizar pip.
echo [ERROR] Fallo al actualizar pip. Revisa %STDERR_LOG% >> "%DEBUG_LOG%"
pause
exit /b 4

:fail_requirements
echo [ERROR] Fallo al instalar dependencias.
echo [ERROR] Fallo al instalar requirements. Revisa %STDERR_LOG% >> "%DEBUG_LOG%"
pause
exit /b 5

:fail_run
echo [ERROR] Fallo al ejecutar la aplicacion.
echo [ERROR] Fallo al ejecutar python -m presentacion. Revisa %STDERR_LOG% >> "%DEBUG_LOG%"
pause
exit /b 6
