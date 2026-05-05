@echo off
chcp 65001 > nul
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

python -m pip install --upgrade pip
pip install -r req.txt
python fishing_bot.py[cite: 1, 3]
pause
