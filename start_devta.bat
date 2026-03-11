@echo off
title Devta AI
color 0D
echo.
echo   ====================================
echo     DEVTA AI - Starting up...
echo   ====================================
echo.

:: Change to script directory (so it works from any location)
cd /d "%~dp0"

:: Use venv python directly — no activation needed
set DEVTA_PYTHON=%~dp0venv\Scripts\python.exe

if not exist "%DEVTA_PYTHON%" (
    echo  ERROR: Virtual environment not found!
    echo  Please run setup.bat first.
    pause
    exit /b 1
)

echo  Launching Devta...
start "" "%DEVTA_PYTHON%" "%~dp0main.py"
