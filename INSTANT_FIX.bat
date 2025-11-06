@echo off
echo =====================================
echo FIXING SERVER ERROR NOW...
echo =====================================
echo.

REM Stop any running Python processes
taskkill /F /IM python.exe 2>nul

echo Deleting old database...
if exist "instance\girvi.db" (
    del "instance\girvi.db"
    echo Database deleted!
) else (
    echo No old database found.
)

echo.
echo Creating instance folder...
if not exist "instance" mkdir instance

echo.
echo =====================================
echo STARTING SERVER...
echo =====================================
echo.
echo Login: admin / admin123
echo Then complete shop profile
echo =====================================
echo.

python app.py

pause
