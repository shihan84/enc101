@echo off
SETLOCAL

REM Define the path to the executable for version 2.0.1
SET "APP_PATH=.\IBE-100.exe"

ECHO ========================================================================
ECHO   ITAssist Broadcast Encoder - 100 (IBE-100) v2.0.1
ECHO ========================================================================
ECHO.

REM Check if the executable exists
IF NOT EXIST "%APP_PATH%" (
    ECHO [ERROR] IBE-100.exe not found at "%APP_PATH%".
    ECHO Please ensure the application is in the 'dist_final' directory.
    GOTO :EOF
)

ECHO [OK] Application executable found
ECHO.

REM Quick check for TSDuck
ECHO Checking system requirements...
tsp --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [WARNING] TSDuck not found in PATH!
    ECHO.
    ECHO If you get error code 1 when starting a stream, TSDuck may not be installed.
    ECHO.
    ECHO To fix:
    ECHO   1. Install TSDuck from: https://tsduck.io/download/
    ECHO   2. Add to PATH: set PATH=%%PATH%%;C:\Program Files\TSDuck\bin
    ECHO   3. Run diagnose_system.bat to check setup
    ECHO.
    ECHO Press any key to launch anyway, or Ctrl+C to cancel and install TSDuck...
    pause >nul
) ELSE (
    ECHO [OK] TSDuck found
    tsp --version
)

ECHO.
ECHO Launching ITAssist Broadcast Encoder - 100 (IBE-100) v2.0.2...
ECHO This version includes auto-update feature and enhanced diagnostics!
ECHO.
ECHO ========================================================================
ECHO.

REM Check for Python for serve_hls.py (optional)
IF EXIST "serve_hls.py" (
    ECHO [INFO] HLS/DASH test server script available
) ELSE (
    ECHO [INFO] HLS/DASH server will be managed from within the application
)

START "" "%APP_PATH%"

ENDLOCAL

