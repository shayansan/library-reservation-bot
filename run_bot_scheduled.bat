@echo off

cd /d "%~dp0"

if not exist "logs" mkdir "logs"

echo. >> "logs\scheduler.log"
echo ======================================== >> "logs\scheduler.log"
echo [%date% %time%] Starting scheduled bot >> "logs\scheduler.log"

"%~dp0.venv\Scripts\python.exe" "%~dp0main.py" >> "logs\scheduler.log" 2>&1

echo [%date% %time%] Scheduled bot finished >> "logs\scheduler.log"