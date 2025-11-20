@echo off
SETLOCAL EnableDelayedExpansion

echo.
echo ========================================================================
echo   IBE-100 v2.0.1 Pre-Deployment Prerequisite Check
echo   ITAssist Broadcast Encoder - 100
echo ========================================================================
echo.

SET ERROR_COUNT=0
SET WARNING_COUNT=0

REM ========================================================================
REM [1] Check TSDuck Installation
REM ========================================================================
echo [1] Checking TSDuck installation...
tsp --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] TSDuck not found!
    echo.
    echo Solution:
    echo   1. Download TSDuck from: https://tsduck.io/download/tsduck/
    echo   2. Install to default location: C:\Program Files\TSDuck
    echo   3. Add to PATH: set PATH=%%PATH%%;C:\Program Files\TSDuck\bin
    echo.
    SET /A ERROR_COUNT+=1
) ELSE (
    echo [OK] TSDuck installed
    tsp --version
)
echo.

REM ========================================================================
REM [2] Check TSDuck in PATH
REM ========================================================================
echo [2] Checking TSDuck in system PATH...
where tsp >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] TSDuck not in system PATH
    echo.
    echo Solution:
    echo   Add C:\Program Files\TSDuck\bin to Environment Variables PATH
    echo.
    SET /A ERROR_COUNT+=1
) ELSE (
    echo [OK] TSDuck found in PATH
    where tsp
)
echo.

REM ========================================================================
REM [3] Check Required Plugins
REM ========================================================================
echo [3] Checking required TSDuck plugins...
tsp --list-plugins > temp_plugins.txt 2>&1
FINDSTR /I "hls" temp_plugins.txt >nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] hls plugin not found
    SET /A WARNING_COUNT+=1
) ELSE (
    echo [OK] hls plugin available
)

FINDSTR /I "srt" temp_plugins.txt >nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] srt plugin not found
    SET /A WARNING_COUNT+=1
) ELSE (
    echo [OK] srt plugin available
)

FINDSTR /I "spliceinject" temp_plugins.txt >nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] spliceinject plugin not found
    SET /A WARNING_COUNT+=1
) ELSE (
    echo [OK] spliceinject plugin available
)

DEL temp_plugins.txt >nul 2>&1
echo.

REM ========================================================================
REM [4] Check Network Connectivity
REM ========================================================================
echo [4] Checking network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo [OK] Internet connectivity OK
) ELSE (
    echo [WARNING] Network connectivity issues detected
    echo   - Check internet connection
    echo   - Check firewall settings
    SET /A WARNING_COUNT+=1
)
echo.

REM ========================================================================
REM [5] Check Application Files
REM ========================================================================
echo [5] Checking IBE-100 application files...
IF EXIST "IBE-100.exe" (
    echo [OK] IBE-100.exe found
    FOR %%F IN (IBE-100.exe) DO ECHO    Size: %%~zF bytes
) ELSE (
    echo [ERROR] IBE-100.exe not found in current directory
    SET /A ERROR_COUNT+=1
)
echo.

IF EXIST "launch_ibe100_v2.0.1.bat" (
    echo [OK] launch_ibe100_v2.0.1.bat found
) ELSE (
    echo [WARNING] launch_ibe100_v2.0.1.bat not found
    SET /A WARNING_COUNT+=1
)

IF EXIST "diagnose_system.bat" (
    echo [OK] diagnose_system.bat found
) ELSE (
    echo [WARNING] diagnose_system.bat not found
    SET /A WARNING_COUNT+=1
)
echo.

REM ========================================================================
REM [6] Check File Permissions
REM ========================================================================
echo [6] Checking file permissions...
ECHO test > permission_test.tmp 2>&1
IF EXIST "permission_test.tmp" (
    ECHO [OK] Write permissions OK
    DEL permission_test.tmp >nul 2>&1
) ELSE (
    ECHO [ERROR] Cannot write to current directory
    ECHO   - Run as administrator
    ECHO   - Check folder permissions
    SET /A ERROR_COUNT+=1
)
echo.

REM ========================================================================
REM [7] Check System Resources
REM ========================================================================
echo [7] Checking system resources...
ECHO    (Checking available resources...)
FOR /F "tokens=2 delims==" %%I IN ('wmic OS get TotalVisibleMemorySize /VALUE') DO SET TOTAL_MEM=%%I
FOR /F "tokens=2 delims==" %%I IN ('wmic OS get FreePhysicalMemory /VALUE') DO SET FREE_MEM=%%I

IF DEFINED TOTAL_MEM IF DEFINED FREE_MEM (
    SET /A TOTAL_GB=!TOTAL_MEM! / 1048576
    SET /A FREE_GB=!FREE_MEM! / 1048576
    
    IF !TOTAL_GB! GEQ 4 (
        ECHO    Total Memory: !TOTAL_GB! GB
        ECHO    Free Memory: !FREE_GB! GB
        ECHO [OK] System meets minimum requirements
    ) ELSE (
        ECHO    Total Memory: !TOTAL_GB! GB
        ECHO [WARNING] Low system memory (4GB+ recommended)
        SET /A WARNING_COUNT+=1
    )
) ELSE (
    ECHO [INFO] Could not determine memory (may require wmic)
)
echo.

REM ========================================================================
REM [8] Check Firewall/Antivirus (Info Only)
REM ========================================================================
echo [8] Firewall and antivirus information...
ECHO    Please ensure:
ECHO    - Windows Defender allows TSDuck
ECHO    - Firewall allows network connections
ECHO    - Antivirus not blocking IBE-100.exe
echo.

REM ========================================================================
REM SUMMARY
REM ========================================================================
echo ========================================================================
echo   Prerequisite Check Summary
echo ========================================================================
echo.
ECHO Errors found: %ERROR_COUNT%
ECHO Warnings found: %WARNING_COUNT%
echo.

IF %ERROR_COUNT% GTR 0 (
    ECHO ========================================================================
    ECHO   [FAILED] Critical errors detected!
    ECHO ========================================================================
    ECHO.
    ECHO Please fix the errors above before deploying IBE-100.
    ECHO.
    ECHO Most common issues:
    ECHO   1. TSDuck not installed → Install from https://tsduck.io/download/
    ECHO   2. TSDuck not in PATH → Add C:\Program Files\TSDuck\bin to PATH
    ECHO   3. Missing files → Ensure all files are in deployment folder
    ECHO.
    ECHO See PRE_REQUISITE_CHECKLIST.md for detailed instructions.
    ECHO.
    ENDLOCAL
    EXIT /B 1
)

IF %WARNING_COUNT% GTR 0 (
    ECHO ========================================================================
    ECHO   [WARNING] Some issues detected
    ECHO ========================================================================
    ECHO.
    ECHO System is ready for deployment, but review warnings above.
    ECHO.
    ECHO IBE-100 should work, but some features may be limited.
    ECHO.
    ECHO Next steps:
    ECHO   1. Review warnings above
    ECHO   2. Run diagnose_system.bat for detailed diagnostics
    ECHO   3. Launch IBE-100: launch_ibe100_v2.0.1.bat
    ECHO.
) ELSE (
    ECHO ========================================================================
    ECHO   [PASSED] All prerequisites met!
    ECHO ========================================================================
    ECHO.
    ECHO System is ready for IBE-100 v2.0.1 deployment.
    ECHO.
    ECHO Next steps:
    ECHO   1. Launch IBE-100: launch_ibe100_v2.0.1.bat
    ECHO   2. Configure stream settings
    ECHO   3. Start processing
    ECHO.
)

ENDLOCAL

pause

