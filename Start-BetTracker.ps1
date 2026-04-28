# Script para iniciar Bet Tracker em background
Write-Host "Iniciando Bet Tracker em background..." -ForegroundColor Green

# Obter o diretório do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Iniciar em background usando pythonw.exe (sem console)
$pythonw = Join-Path $scriptDir "venv\Scripts\pythonw.exe"
if (Test-Path $pythonw) {
    Start-Process $pythonw -ArgumentList "start_all.py" -WindowStyle Hidden
    Write-Host "Bet Tracker iniciado em background!" -ForegroundColor Green
    Write-Host "Dashboard: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Para parar, execute: .\Stop-BetTracker.ps1" -ForegroundColor Yellow
} else {
    Write-Host "Erro: pythonw.exe não encontrado no virtual environment" -ForegroundColor Red
}

Read-Host "Pressione Enter para continuar"