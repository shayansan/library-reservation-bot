@echo off

cd /d "%~dp0"

echo ========================================
echo Library Reservation Bot v2
echo ========================================
echo.

"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"

echo.
echo Bot finished.
pause