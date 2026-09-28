@echo off
title LegalEase - FastAPI Backend
echo ===================================================
echo   Starting LegalEase FastAPI Backend Server
echo   Host: http://127.0.0.1:8000
echo   Docs: http://127.0.0.1:8000/docs
echo ===================================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
) else (
    echo [ERROR] Virtual environment not found. Please run setup first.
    pause
)
