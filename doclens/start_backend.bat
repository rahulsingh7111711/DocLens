@echo off
echo ============================================
echo   DocLens — Starting Backend (FastAPI)
echo ============================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Starting FastAPI server on http://localhost:8000
echo Press CTRL+C to stop.
echo.

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
