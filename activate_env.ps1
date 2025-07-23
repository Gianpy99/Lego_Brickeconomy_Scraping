# PowerShell script to activate Python 3.13 virtual environment

Write-Host "🚀 Activating Python 3.13 Virtual Environment..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv_py313\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: py -3.13 -m venv venv_py313" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& .\venv_py313\Scripts\Activate.ps1

Write-Host "✅ Python 3.13 environment activated!" -ForegroundColor Green
Write-Host "📦 Python version:" -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "📝 Available commands:" -ForegroundColor Yellow
Write-Host "  python demo.py           - Interactive demonstration" -ForegroundColor White
Write-Host "  python main.py --help    - Command-line help" -ForegroundColor White
Write-Host "  python test_imports.py   - Test all modules" -ForegroundColor White
Write-Host "  python setup.py          - Setup and install dependencies" -ForegroundColor White
Write-Host ""
