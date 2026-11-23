@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" ejecutar_y_publicar.py
) else (
    python ejecutar_y_publicar.py
)

if errorlevel 1 exit /b 1
