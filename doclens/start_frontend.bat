@echo off
echo ============================================
echo   DocLens — Starting Frontend (Streamlit)
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

echo Starting Streamlit on http://localhost:8501
echo Make sure the backend is also running!
echo Press CTRL+C to stop.
echo.

streamlit run frontend/app.py
pause
