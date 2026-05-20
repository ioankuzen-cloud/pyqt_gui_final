$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Python is not installed or is not added to PATH."
        Write-Host "Install Python from https://www.python.org/downloads/ and enable 'Add python.exe to PATH'."
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing dependencies..."
& $python -m pip install -r requirements.txt

Write-Host "Starting application..."
& $python main.py
