@echo off
echo Parando Bet Tracker...
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im pythonw.exe /t >nul 2>&1
echo Bet Tracker parado!
pause