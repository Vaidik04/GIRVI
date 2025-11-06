@echo off
title Girvi Backend Server
color 0A

echo.
echo ================================================
echo          GIRVI BACKEND SERVER
echo ================================================
echo.

cd /d "%~dp0"

REM Test dependencies first
python test_server.py
if errorlevel 1 (
    echo.
    echo [ERROR] Dependencies check failed!
    echo Installing required packages...
    pip install -r requirements.txt
    echo.
)

echo.
echo ================================================
echo Starting server...
echo ================================================
echo.
echo Server URLs:
echo   - Android Emulator: http://10.0.2.2:5000
echo   - iOS Simulator:    http://localhost:5000
echo   - Real Device:      http://YOUR_IP_ADDRESS:5000
echo.
echo Press Ctrl+C to stop
echo ================================================
echo.

python app.py
