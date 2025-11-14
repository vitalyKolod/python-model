@echo off
title Scenario Parser API - Setup

echo =========================================
echo Scenario Parser API - Setup Dependencies
echo =========================================
echo.

REM -----------------------------
REM 1. Проверка виртуального окружения
REM -----------------------------
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM -----------------------------
REM 2. Активируем виртуальное окружение
REM -----------------------------
call venv\Scripts\activate

REM -----------------------------
REM 3. Установка зависимостей
REM -----------------------------
echo Installing dependencies...
pip install --upgrade pip
pip install fastapi uvicorn python-docx spacy python-multipart tqdm

REM -----------------------------
REM 4. Проверка spaCy модели
REM -----------------------------
echo Checking spaCy model...
python - <<EOF
import spacy
try:
    spacy.load("ru_core_news_sm")
    print("spaCy model already installed.")
except:
    import os
    print("Downloading spaCy model...")
    os.system("python -m spacy download ru_core_news_sm")
EOF

echo.
echo Setup complete. You can now run run_api.bat to start the server.
pause
