@echo off
title Push LegalEase to GitHub
cd /d "%~dp0"
echo ========================================================
echo   Pushing commits to GitHub:
echo   https://github.com/ananthika-commits/LegalEase_Eugin.git
echo ========================================================
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Successfully pushed to GitHub!
) else (
    echo [FAILED] Git push encountered an error or needs authentication.
)
echo.
pause
