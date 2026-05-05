@echo off
fsutil dirty query %systemdrive% >nul || (powershell start-process "%~0" -verb runas && exit /b)

cd /d "%~dp0"

echo Starting Fishing Bot...
py -3.13 fishing_bot.py
pause
