@echo off
echo Iniciando Bet Tracker em background...
cd /d "%~dp0"
start /B pythonw start_all.py
echo Bet Tracker iniciado em background!
echo Para parar, execute: stop_bet_tracker.bat
pause