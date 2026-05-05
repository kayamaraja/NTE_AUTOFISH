@echo off
setlocal enabledelayedexpansion

fsutil dirty query %systemdrive% >nul 2>&1 || (
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

py -m pip install -r req.txt

echo Starting Fishing Bot...
py fishing_bot.py

pause
