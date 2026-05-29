@echo off
title PDF Smart Tool

echo ============================================
echo   PDF Smart Tool - Just Double Click
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b
)

echo Installing dependencies..
pip install -r "%~dp0requirements.txt" -q
if %errorlevel% equ 0 (
    echo [OK] Dependencies ready
) else (
    pip install -r "%~dp0requirements.txt"
)

echo Starting app..
python "%~dp0gui\app.py"
if %errorlevel% neq 0 (
    echo [ERROR] Launch failed
    pause
)

