@echo off
echo ====================================
echo   Building Norwegian Dictionary
echo   Installer Package
echo ====================================
echo.

REM Navigate to project root
cd /d "%~dp0.."

REM Step 0: Generate comtypes cache
echo [0/4] Generating comtypes type libraries...
python build_scripts\generate_comtypes.py
echo.

REM Step 1: Install PyInstaller if needed
echo [1/4] Installing PyInstaller...
pip install pyinstaller
echo.

REM Step 2: Build the executable with hidden imports and comtypes data
echo [2/4] Building executable...
cd src
pyinstaller --noconsole --onefile --name="NorwegianDictionary" ^
    --hidden-import=comtypes.gen ^
    --hidden-import=comtypes.gen.UIAutomationClient ^
    --collect-data comtypes ^
    --distpath=..\dist ^
    --workpath=..\build ^
    --specpath=.. ^
    main.py
cd ..
echo.

REM Step 3: Check if Inno Setup is installed
echo [3/4] Checking for Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist "%INNO_PATH%" (
    echo Found Inno Setup!
    echo Building installer...
    "%INNO_PATH%" installer\installer_script.iss
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
    echo 2. Open installer\installer_script.iss
    echo 3. Click Build -^> Compile
    echo.
)

pause