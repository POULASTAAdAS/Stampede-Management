# Stampede Management - Virtual Environment Activation Script
# This script sets the execution policy for the current session and activates the venv

Write-Host "Setting execution policy for current session..." -ForegroundColor Cyan
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

Write-Host "`nVirtual environment activated successfully!" -ForegroundColor Green
Write-Host "Python version: " -NoNewline
python --version
Write-Host "Location: " -NoNewline
Get-Command python | Select-Object -ExpandProperty Source

Write-Host "`nYou can now run the application with: python main.py" -ForegroundColor Yellow
