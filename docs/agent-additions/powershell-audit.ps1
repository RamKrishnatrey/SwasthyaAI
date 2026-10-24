$ErrorActionPreference = "Continue"

Write-Host "=== SwasthyaAI read-only local audit ===" -ForegroundColor Cyan
Write-Host "This script does not edit or delete application files."
Write-Host ""

$Root = (Get-Location).Path
Write-Host "Current directory: $Root"

Write-Host "`n=== Git status ===" -ForegroundColor Cyan
git status --short
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not in a Git working tree; open PowerShell inside the repository." -ForegroundColor Yellow
}

Write-Host "`n=== Python and package versions ===" -ForegroundColor Cyan
py --version
py -c "import pandas; print('pandas', pandas.__version__)" 2>$null
py -c "import sklearn; print('scikit-learn', sklearn.__version__)" 2>$null
py -c "import torch; print('PyTorch', torch.__version__); print('CUDA available', torch.cuda.is_available())" 2>$null

Write-Host "`n=== Existing project files (read-only) ===" -ForegroundColor Cyan
@(
  "README.md",
  "backend/requirements.txt",
  "backend/swasthyaai/agent/service.py",
  "backend/swasthyaai/agent/safety.py",
  "backend/swasthyaai/agent/matcher.py",
  "train_urgency_v2.py"
) | ForEach-Object {
    [PSCustomObject]@{
      Path = $_
      Exists = Test-Path (Join-Path $Root $_)
    }
} | Format-Table -AutoSize

Write-Host "`n=== Potential secret files (names only; contents are not read) ===" -ForegroundColor Cyan
Get-ChildItem -Path $Root -Force -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\(\.git|node_modules|\.venv|venv)\\' -and
    $_.Name -match '(^\.env($|\.)|secret|credential|token|api.?key)'
  } |
  Select-Object -ExpandProperty FullName

Write-Host "`nAudit complete. Review any unignored data or secret files before pushing." -ForegroundColor Green