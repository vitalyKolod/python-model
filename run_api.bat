@echo off
title Scenario Parser API - Run Server

echo =========================================
echo Scenario Parser API - Server Launcher
echo =========================================
echo.

REM 1. Проверяем, есть ли venv
if not exist venv (
    echo Virtual environment not found! Please run setup.bat first.
    pause
    exit /b
)

REM 2. Активируем виртуальное окружение
call venv\Scripts\activate

REM 3. Запуск uvicorn
echo Starting Scenario Parser API server...
echo Open http://127.0.0.1:8000/docs in your browser
echo.

REM Запуск сервера в новом окне, чтобы оно оставалось открытым
start cmd /k "python api.py"

echo.
echo Server launched in a new window.
echo Press any key to close this launcher window.
pause >nul
