@echo off
echo ============================================
echo   DocLens — First-Time Setup
echo ============================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/4] Installing dependencies (this may take 3-5 minutes)...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [4/4] Setting up .env file...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file. Please open it and add your GROQ_API_KEY.
) else (
    echo .env already exists, skipping.
)

echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo NEXT STEPS:
echo  1. Open .env and add your GROQ_API_KEY
echo     Get a free key at: https://console.groq.com
echo.
echo  2. Double-click start_backend.bat   (Terminal 1)
echo  3. Double-click start_frontend.bat  (Terminal 2)
echo  4. Open http://localhost:8501 in your browser
echo.
pause
