# setup_venv.ps1
#
# Creates an isolated Python virtual environment for the
# Dutch monthly calendar generator (PDF version).
#
# Usage:
#   .\setup_venv.ps1
#
# After setup:
#   .\.venv\Scripts\python.exe .\calendar365.py 2026

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Dutch Calendar - Python setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Determine the directory containing this script.
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectDir

$VenvDir = Join-Path $ProjectDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# ------------------------------------------------------------
# Check for Python
# ------------------------------------------------------------

Write-Host "Checking for Python..." -ForegroundColor Yellow

$PythonCommand = Get-Command python -ErrorAction SilentlyContinue

if (-not $PythonCommand) {
    $PythonCommand = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $PythonCommand) {
    Write-Host ""
    Write-Host "ERROR: Python was not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Python 3 from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/windows/"
    Write-Host ""
    Write-Host "Make sure Python is added to PATH during installation."
    exit 1
}

$PythonExecutable = $PythonCommand.Source

Write-Host "Found Python: $PythonExecutable" -ForegroundColor Green

# ------------------------------------------------------------
# Display Python version
# ------------------------------------------------------------

& $PythonExecutable --version

# ------------------------------------------------------------
# Create virtual environment
# ------------------------------------------------------------

if (Test-Path $VenvDir) {
    Write-Host ""
    Write-Host "Virtual environment already exists:" -ForegroundColor Yellow
    Write-Host "  $VenvDir"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow

    & $PythonExecutable -m venv $VenvDir

    if (-not (Test-Path $VenvPython)) {
        Write-Host ""
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }

    Write-Host "Virtual environment created." -ForegroundColor Green
}

# ------------------------------------------------------------
# Upgrade pip inside the virtual environment
# ------------------------------------------------------------

Write-Host ""
Write-Host "Upgrading pip inside .venv..." -ForegroundColor Yellow

& $VenvPython -m pip install --upgrade pip

# ------------------------------------------------------------
# Install dependencies
# ------------------------------------------------------------

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

# CHANGED: Replaced odfpy with reportlab
& $VenvPython -m pip install reportlab

# ------------------------------------------------------------
# Verify installation
# ------------------------------------------------------------

Write-Host ""
Write-Host "Verifying reportlab installation..." -ForegroundColor Yellow

# CHANGED: Verify reportlab instead of odf
& $VenvPython -c "import reportlab; print('reportlab successfully installed.')"

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Virtual environment:" -ForegroundColor Cyan
Write-Host "  $VenvDir"

Write-Host ""
Write-Host "To generate a PDF calendar for 2026:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe .\calendar365.py 2026"

Write-Host ""
Write-Host "For example, for 2027:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe .\calendar365.py 2027"

Write-Host ""
Write-Host "The global Python installation was not modified." -ForegroundColor Green
Write-Host ""
