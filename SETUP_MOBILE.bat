@echo off
cls
echo ================================================================================
echo                    MOBILE APP CONNECTION SETUP
echo ================================================================================
echo.
echo STEP 1: Finding your computer's IP address...
echo.
ipconfig | findstr "IPv4" | findstr /V "127.0.0.1"
echo.
echo ================================================================================
echo.
echo STEP 2: Copy one of the IP addresses above (usually starts with 192.168)
echo         Example: 192.168.1.5
echo.
echo STEP 3: On your mobile app:
echo         - Open the app
echo         - Go to Server Settings (gear icon)
echo         - Enter: http://YOUR_IP:5000
echo           Example: http://192.168.1.5:5000
echo         - Tap "Test Connection"
echo         - Should say "Connected successfully!"
echo.
echo ================================================================================
echo.
echo STEP 4: Make sure both computer and phone are on SAME WiFi!
echo.
echo Your computer is connected to:
netsh wlan show interfaces | findstr "SSID"
echo.
echo Make sure your phone is connected to the SAME network!
echo.
echo ================================================================================
echo.
echo STEP 5: Allow firewall (if needed)
echo.
set /p firewall="Do you want to allow Flask through firewall? (Y/N): "
if /i "%firewall%"=="Y" (
    echo.
    echo Adding firewall rule...
    netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
    echo.
    echo ✓ Firewall rule added!
)
echo.
echo ================================================================================
echo.
echo STEP 6: Starting server...
echo ================================================================================
echo.
echo Server will start on: http://0.0.0.0:5000
echo.
echo On your phone, use: http://YOUR_IP:5000
echo.
echo ================================================================================
echo.
pause
echo.

cd /d "%~dp0"
python app.py
