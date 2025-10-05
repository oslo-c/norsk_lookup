@echo off
echo Building DEBUG version (with console for troubleshooting)...
echo.

REM Build with console window so you can see errors
pyinstaller --onefile --name="NorwegianDictionary_DEBUG" ^
    --hidden-import=comtypes.gen ^
    --hidden-import=comtypes.gen.UIAutomationClient ^
    main.py

echo.
echo Debug version created at: dist\NorwegianDictionary_DEBUG.exe
echo Run this to see console output and error messages!
echo.
pause