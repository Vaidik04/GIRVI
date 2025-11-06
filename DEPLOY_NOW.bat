@echo off
title Deploy to Heroku
color 0E

echo ================================================
echo      DEPLOY GIRVI BACKEND TO HEROKU
echo ================================================
echo.

cd /d "%~dp0"

echo Checking prerequisites...
echo.

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo Install from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo [OK] Git installed

REM Check Heroku CLI
heroku --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Heroku CLI not found!
    echo Install from: https://devcenter.heroku.com/articles/heroku-cli
    echo.
    pause
    exit /b 1
)
echo [OK] Heroku CLI installed
echo.

echo ================================================
echo Step 1: Login to Heroku
echo ================================================
echo Browser will open. Login with your Heroku account.
echo.
pause

heroku login
if errorlevel 1 (
    echo [ERROR] Login failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Step 2: Initialize Git Repository
echo ================================================
echo.

if not exist ".git" (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - Girvi backend"
) else (
    echo Git repository already exists.
    echo Committing current changes...
    git add .
    git commit -m "Deploy to Heroku" 2>nul
)

echo.
echo ================================================
echo Step 3: Create Heroku App
echo ================================================
echo.
echo Enter a unique app name (lowercase, no spaces)
echo Or press Enter for auto-generated name
echo.
set /p appname="App name: "

if "%appname%"=="" (
    heroku create
) else (
    heroku create %appname%
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create app!
    echo Try a different name or let Heroku generate one.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Step 4: Deploy to Heroku
echo ================================================
echo This may take 2-3 minutes...
echo.

git push heroku main
if errorlevel 1 (
    echo Trying with master branch...
    git push heroku master
)

if errorlevel 1 (
    echo.
    echo [ERROR] Deployment failed!
    echo Check logs: heroku logs --tail
    pause
    exit /b 1
)

echo.
echo ================================================
echo Step 5: Initialize Database
echo ================================================
echo.

heroku run python -c "from app import app, init_db; init_db()"

echo.
echo ================================================
echo [SUCCESS] Deployment Complete!
echo ================================================
echo.
echo Your app is now live!
echo.

REM Get app URL
for /f "tokens=*" %%i in ('heroku info -s ^| findstr web_url') do set APPURL=%%i
set APPURL=%APPURL:web_url=%

echo App URL: %APPURL%
echo Health Check: %APPURL%/api/mobile/health
echo.
echo ================================================
echo NEXT STEPS:
echo ================================================
echo.
echo 1. Test your API:
echo    Open: %APPURL%/api/mobile/health
echo.
echo 2. Update mobile app with URL:
echo    Edit: GirviMobile\lib\main.dart
echo    Change defaultValue to: '%APPURL%'
echo.
echo 3. View logs:
echo    heroku logs --tail
echo.
echo 4. Open app in browser:
echo    heroku open
echo.
pause
