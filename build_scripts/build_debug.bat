@echo off
REM Navigate to project root
cd /d "%~dp0.."

echo Generating comtypes cache first...
python build_scripts\generate_comtypes.py
echo.

echo Building DEBUG version (with console for troubleshooting)...
echo.

REM Change to src directory and build from there
cd src
pyinstaller --onefile --name="NorwegianDictionary_DEBUG" ^
    --hidden-import=comtypes.gen ^
    --hidden-import=comtypes.gen.UIAutomationClient ^
    --collect-data comtypes ^
    --distpath=..\dist ^
    --workpath=..\build ^
    --specpath=.. ^
    main.py
cd ..

echo.
echo Debug version created at: dist\NorwegianDictionary_DEBUG.exe
echo Run this to see console output and error messages!
echo.
pause