@echo off
cls
echo ========================================
echo FIND YOUR IP ADDRESS FOR MOBILE PHONES
echo ========================================
echo.
echo Your Computer's IP Address:
echo.
ipconfig | findstr "IPv4"
echo.
echo ========================================
echo INSTRUCTIONS:
echo ========================================
echo.
echo 1. Look for the IP address above
echo    (example: 192.168.1.5)
echo.
echo 2. On your mobile phone, use this URL:
echo    http://YOUR_IP:5000
echo.
echo    Example: http://192.168.1.5:5000
echo.
echo 3. Make sure phone and computer are on
echo    the SAME WiFi network!
echo.
echo ========================================
echo.
pause
