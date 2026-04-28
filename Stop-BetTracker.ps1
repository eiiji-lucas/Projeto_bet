# Script para parar Bet Tracker
Write-Host "Parando Bet Tracker..." -ForegroundColor Yellow

# Parar todos os processos Python
Get-Process python, pythonw -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "Bet Tracker parado!" -ForegroundColor Green

Read-Host "Pressione Enter para continuar"