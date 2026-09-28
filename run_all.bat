@echo off
title LegalEase Launcher
echo =======================================================
echo   Launching LegalEase Complete System
echo   1. Backend API (FastAPI) at http://127.0.0.1:8000
echo   2. Frontend UI (Streamlit) at http://localhost:8501
echo =======================================================

cd /d "%~dp0"

echo Starting FastAPI backend in a new window...
start "LegalEase Backend (Port 8000)" cmd /k "start_backend.bat"

timeout /t 3 /nobreak >nul

echo Starting Streamlit frontend in a new window...
start "LegalEase Frontend (Port 8501)" cmd /k "start_frontend.bat"

timeout /t 2 /nobreak >nul

echo Opening LegalEase Web App in your default browser...
start http://localhost:8501

echo.
echo Both servers initiated and browser opened!
echo You can minimize this window.
pause >nul
