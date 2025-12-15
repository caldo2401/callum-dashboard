@echo off
setlocal

:: Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

set FLASK_APP=app.py
start "Callum Dashboard" /B python app.py

:: Give the server a moment to start
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000/
