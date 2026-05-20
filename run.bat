@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Python is not installed or is not added to PATH.
        echo Install Python from https://www.python.org/downloads/ and enable "Add python.exe to PATH".
        pause
        exit /b 1
    )

    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    set "PYTHON=.venv\Scripts\python.exe"
)

echo Installing dependencies...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Starting application...
"%PYTHON%" main.py
pause
