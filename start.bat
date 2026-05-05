@echo off
setlocal enabledelayedexpansion

fsutil dirty query %systemdrive% >nul || (powershell start-process "%~0" -verb runas && exit /b)

cd /d "%~dp0"

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m ensurepip
    python -m pip install --upgrade pip
)

python -c "import pkg_resources; ps = [l.split('=')[0].split('>')[0].strip() for l in open('req.txt') if l.strip() and not l.startswith('#')]; pkg_resources.require(ps)" >nul 2>&1

if %errorlevel% neq 0 (
    python -m pip install -r req.txt
    if %errorlevel% neq 0 (
        echo [ERROR]
        pause
        exit /b
    )
)

py fishing_bot.py
pause
