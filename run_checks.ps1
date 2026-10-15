Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Running UV-Powered Project Validation" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "[1/4] Formatting code..." -ForegroundColor Yellow
uv run ruff format .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Formatting failed!" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[2/4] Linting code..." -ForegroundColor Yellow
uv run ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Linting failed!" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[3/4] Checking static types..." -ForegroundColor Yellow
uv run mypy .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Type checking failed!" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[4/4] Executing test suite..." -ForegroundColor Yellow
uv run pytest
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Tests failed!" -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "=========================================" -ForegroundColor Green
Write-Host " ✨ All checks passed instantly via uv! ✨" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
