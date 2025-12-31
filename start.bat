@echo off
cd /d "%~dp0"

where pythonw >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

pythonw -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    pip install PyQt6 -q
)

start "" pythonw main.py
