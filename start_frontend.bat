@echo off
title LegalEase - Streamlit Frontend
echo ===================================================
echo   Starting LegalEase Streamlit Frontend Application
echo   URL: http://localhost:8501
echo ===================================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
) else (
    echo [ERROR] Virtual environment not found. Please run setup first.
    pause
)
