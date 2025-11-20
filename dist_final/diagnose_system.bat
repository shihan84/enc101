@echo off
REM System Diagnostic Tool for IBE-100 v2.0.1
REM Helps diagnose error code 1 issues

SETLOCAL
echo.
echo ========================================================================
echo   IBE-100 v2.0.1 System Diagnostic Tool
echo   ITAssist Broadcast Encoder - 100
echo ========================================================================
echo.

REM Check if executable exists
echo [1] Checking IBE-100 executable...
IF EXIST "IBE-100.exe" (
    echo    IBE-100.exe: Found
    for %%F in (IBE-100.exe) do echo    Size: %%~zF bytes
) ELSE (
    echo    IBE-100.exe: NOT FOUND
    echo    Please ensure you're in the correct directory
)
echo.

REM Check if TSDuck is available
echo [2] Checking TSDuck...
tsp --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo    TSDuck is installed
    tsp --version
) ELSE (
    echo    TSDuck NOT found in PATH
    echo.
    echo    This is the most common cause of error code 1!
    echo.
    echo    Common solutions:
    echo    1. Install TSDuck from: https://tsduck.io/download/
    echo    2. Add TSDuck to PATH:
    echo       set PATH=%%PATH%%;C:\Program Files\TSDuck\bin
    echo    3. Or run this from TSDuck bin folder
    echo    4. For permanent fix: Add to Environment Variables
)
echo.

REM Test TSDuck plugins
echo [3] Checking TSDuck plugins...
tsp --help | findstr /i "spliceinject hls srt" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo    Required plugins are available
) ELSE (
    echo    WARNING: Some plugins may be missing
    echo    Run: tsp --list-plugins
)
echo.

REM Check if scte35_final folder exists
echo [4] Checking SCTE-35 configuration...
IF EXIST "scte35_final\" (
    echo    scte35_final folder exists
    dir /b "scte35_final\*.xml" >nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        echo    Marker files found
        for /f %%i in ('dir /b "scte35_final\*.xml" ^| find /c /v ""') do echo    Found %%i XML marker files
    ) ELSE (
        echo    No marker files yet (will be created on first use)
    )
) ELSE (
    echo    scte35_final folder not found (will be created automatically)
)
echo.

REM Check network connectivity
echo [5] Checking network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo    Internet connectivity: OK
) ELSE (
    echo    Internet connectivity: FAILED
)
echo.

REM Check for optional HLS/DASH server
echo [6] Checking web server components...
IF EXIST "serve_hls.py" (
    echo    serve_hls.py: Found
) ELSE (
    echo    serve_hls.py: Not found (server managed from GUI)
)
IF EXIST "test_player.html" (
    echo    test_player.html: Found
) ELSE (
    echo    test_player.html: Not found
)
echo.

REM Final summary
echo ========================================================================
echo   Diagnostic Summary
echo ========================================================================
echo.
echo If you see error code 1, the most common causes are:
echo.
echo [1] TSDuck not installed or not in PATH
echo     Solution: Install TSDuck and add to PATH
echo.
echo [2] Input source not accessible
echo     Solution: Check input URL is correct and accessible
echo.
echo [3] SRT server rejecting connection
echo     Solution: Verify SRT server is running and accepts connections
echo.
echo [4] Missing permissions
echo     Solution: Run as administrator or fix permissions
echo.
echo [5] Firewall blocking connections
echo     Solution: Allow IBE-100 and TSDuck through firewall
echo.
echo For detailed diagnosis, run:
echo   python diagnose_error.py
echo.
echo Or check the IBE-100 console output for specific error messages
echo.
echo ========================================================================
echo.
echo v2.0.1 Features:
echo   - Integrated HLS/DASH output
echo   - Real-time monitoring dashboard
echo   - Enhanced SCTE-35 support
echo   - Web server for testing
echo   - System metrics display
echo.
pause

ENDLOCAL

