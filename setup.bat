@echo off
title Devta AI - Setup
color 0D
echo.
echo  ██████╗ ███████╗██╗   ██╗████████╗ █████╗ 
echo  ██╔══██╗██╔════╝██║   ██║╚══██╔══╝██╔══██╗
echo  ██║  ██║█████╗  ██║   ██║   ██║   ███████║
echo  ██║  ██║██╔══╝  ╚██╗ ██╔╝   ██║   ██╔══██║
echo  ██████╔╝███████╗ ╚████╔╝    ██║   ██║  ██║
echo  ╚═════╝ ╚══════╝  ╚═══╝     ╚═╝   ╚═╝  ╚═╝
echo.
echo  Setting up Devta AI Assistant...
echo  ================================================
echo.

REM ── Check Python ──────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% found.

REM ── Create virtual environment ────────────────────
echo.
echo [1/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM ── Activate venv ────────────────────────────────
call venv\Scripts\activate.bat

REM ── Upgrade pip ───────────────────────────────────
echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM ── Install dependencies ──────────────────────────
echo.
echo [3/5] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may have failed. Trying individual installs...
    pip install google-generativeai --quiet
    pip install SpeechRecognition --quiet
    pip install pyttsx3 --quiet
    pip install pyaudio --quiet
    pip install vosk --quiet
    pip install plyer --quiet
    pip install pyautogui --quiet
    pip install psutil --quiet
    pip install pygetwindow --quiet
    pip install python-dotenv --quiet
    pip install keyboard --quiet
    pip install Pillow --quiet
    pip install pystray --quiet
    pip install pyperclip --quiet
    pip install colorama --quiet
)
echo [OK] Dependencies installed.

REM ── Create .env file ─────────────────────────────
echo.
echo [4/5] Setting up configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo.
    echo ================================================
    echo  ACTION REQUIRED: Enter your Gemini API Key
    echo ================================================
    echo  Get your FREE key at: https://aistudio.google.com/
    echo  (Takes 30 seconds, no credit card needed)
    echo.
    set /p APIKEY="Paste your Gemini API key here and press Enter: "
    echo GEMINI_API_KEY=%APIKEY%> .env
    echo [OK] API key saved to .env
) else (
    echo [OK] .env already exists. Skipping.
)

REM ── Test the setup ────────────────────────────────
echo.
echo [5/5] Testing setup...
python -c "import google.generativeai; import pyttsx3; import speech_recognition; print('[OK] Core packages OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] Some packages could not be verified, but proceeding anyway.
) else (
    echo [OK] All core packages verified.
)

echo.
echo ================================================
echo  Devta AI Setup Complete!
echo ================================================
echo.
echo  To start Devta, run:   start_devta.bat
echo  Or directly:           python main.py
echo.
echo  Wake words:   "Hello Devta" / "Bhai Devta"
echo  Stop phrase:  "Devta stop"
echo.

REM ── Create start shortcut ─────────────────────────
echo @echo off > start_devta.bat
echo title Devta AI >> start_devta.bat
echo call venv\Scripts\activate.bat >> start_devta.bat
echo python main.py >> start_devta.bat
echo pause >> start_devta.bat

echo [OK] Created start_devta.bat shortcut.
echo.
pause
