$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Dependencies are not set up. Run .\setup-local.ps1 first."
}
if (-not (Test-Path "frontend\node_modules")) {
    throw "Frontend dependencies are missing. Run .\setup-local.ps1 first."
}

$python = Join-Path $Root ".venv\Scripts\python.exe"
$backend = Start-Process -FilePath $python -ArgumentList @("-m", "uvicorn", "backend.swasthyaai.main:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $Root -PassThru
try {
    Start-Sleep -Seconds 2
    if ($backend.HasExited) {
        throw "Backend stopped during startup. Check backend imports and dependencies."
    }
    Push-Location (Join-Path $Root "frontend")
    try {
        Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor Green
        Write-Host "Frontend URL will appear below. Press Ctrl+C to stop." -ForegroundColor Green
        npm run dev -- --host 127.0.0.1
    } finally {
        Pop-Location
    }
} finally {
    if ($backend -and -not $backend.HasExited) {
        Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
    }
}
