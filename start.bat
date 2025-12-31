@echo off
title SQLMap GUI v2

echo ========================================
echo   SQLMap GUI v2 - SQL Injection Tool
echo ========================================
echo.

REM Switch to script directory
cd /d "%~dp0"

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check dependencies
echo [INFO] Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt6...
    pip install PyQt6 -q
)

REM Start program
echo [INFO] Starting SQLMap GUI v2...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with error
    pause
)
