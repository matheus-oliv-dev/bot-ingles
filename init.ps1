if (Test-Path "venv\Scripts\Activate.ps1") {
    . "venv\Scripts\Activate.ps1"
}

Write-Host "Running Lint (flake8)..." -ForegroundColor Cyan
flake8 src tests main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Linting failed. Please fix the errors above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Running Tests (pytest)..." -ForegroundColor Cyan
python -m pytest tests/
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Tests failed. Please fix the errors above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[SUCCESS] All checks passed! You are good to commit or code." -ForegroundColor Green
exit 0
