@echo off
echo ========================================
echo Starting Girvi Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo Installing/updating dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Warning: Failed to install some dependencies
)
echo.

echo Starting Flask server on http://0.0.0.0:5000
echo.
echo Server will be accessible at:
echo - Android Emulator: http://10.0.2.2:5000
echo - iOS Simulator: http://localhost:5000  
echo - Real Device: http://YOUR_IP:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause
