@echo off
cls
echo ================================================
echo EMERGENCY FIX FOR SERVER ERROR
echo ================================================
echo.
echo This will:
echo 1. Delete the old database
echo 2. Create a fresh database
echo 3. Start the server
echo.
echo You will lose existing data!
echo.
pause

echo.
echo Deleting old database...
if exist "instance\girvi.db" (
    del "instance\girvi.db"
    echo ✓ Database deleted!
) else (
    echo ✓ No old database found
)

echo.
echo ================================================
echo Starting server with fresh database...
echo ================================================
echo.
echo Login with:
echo   Username: admin
echo   Password: admin123
echo.
echo Then complete shop profile before adding customers.
echo ================================================
echo.

python app.py
