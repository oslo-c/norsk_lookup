@echo off
echo ====================================
echo   Building Norwegian Dictionary
echo   Installer Package
echo ====================================
echo.

REM Step 1: Install PyInstaller if needed
echo [1/3] Installing PyInstaller...
pip install pyinstaller
echo.

REM Step 2: Build the executable with hidden imports
echo [2/3] Building executable...
pyinstaller --noconsole --onefile --name="NorwegianDictionary" ^
    --hidden-import=comtypes.gen ^
    --hidden-import=comtypes.gen.UIAutomationClient ^
    main.py
echo.

REM Step 3: Check if Inno Setup is installed
echo [3/3] Checking for Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist "%INNO_PATH%" (
    echo Found Inno Setup!
    echo Building installer...
    "%INNO_PATH%" installer_script.iss
    echo.
    echo ====================================
    echo   BUILD COMPLETE!
    echo ====================================
    echo.
    echo Your installer is located at:
    echo   Output\NorwegianDictionary_Setup.exe
    echo.
    echo Give this installer to your classmates!
    echo.
) else (
    echo.
    echo ====================================
    echo   INNO SETUP NOT FOUND
    echo ====================================
    echo.
    echo The executable was built successfully, but the installer was not created.
    echo.
    echo To create the installer:
    echo 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Install it (use default location)
    echo 3. Run this script again
    echo.
    echo OR manually compile the installer:
    echo 1. Open Inno Setup Compiler
    echo 2. Open installer_script.iss
    echo 3. Click Build -^> Compile
    echo.
)

pause