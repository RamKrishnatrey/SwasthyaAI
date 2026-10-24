$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== SwasthyaAI local setup ===" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python 3.11 or 3.12 and enable Add Python to PATH, then reopen PowerShell."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm was not found. Install Node.js LTS, then reopen PowerShell."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt

Push-Location frontend
try {
    npm ci
} finally {
    Pop-Location
}

New-Item -ItemType Directory -Force -Path ".local" | Out-Null
Write-Host ""
Write-Host "Setup complete. Start the app with: .\run-local.ps1" -ForegroundColor Green
Write-Host "Local database location: .local\swasthya.sqlite3"
