@echo off
echo ========================================
echo Girvi Management System - Fresh Start
echo ========================================
echo.

REM Check if database exists
if exist "instance\girvi.db" (
    echo Found existing database...
    echo.
    set /p backup="Create backup before deleting? (Y/N): "
    
    if /i "%backup%"=="Y" (
        echo Creating backup...
        copy "instance\girvi.db" "instance\girvi_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db" > nul
        echo Backup created successfully!
        echo.
    )
    
    echo Deleting old database...
    del "instance\girvi.db"
    echo Old database deleted!
    echo.
) else (
    echo No existing database found.
    echo.
)

echo ========================================
echo Starting application...
echo ========================================
echo.
echo The application will create a new database automatically.
echo.
echo Login with:
echo   Username: admin
echo   Password: admin123
echo.
echo ========================================
echo.

python app.py

pause
