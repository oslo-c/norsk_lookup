@echo off
REM Navigate to project root
cd /d "%~dp0.."

echo [Step 1/3] Cleaning old builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q *.spec
if exist "src\*.spec" del /q src\*.spec
echo.

echo [Step 2/3] Pre-generating comtypes cache...
python build_scripts\generate_comtypes.py
echo.

echo [Step 3/3] Building DEBUG executable...
cd src
pyinstaller --onefile ^
    --name="NorwegianDictionary_DEBUG" ^
    --hidden-import=comtypes ^
    --hidden-import=comtypes.client ^
    --hidden-import=comtypes.client._code_cache ^
    --hidden-import=comtypes.client._generate ^
    --hidden-import=comtypes.stream ^
    --hidden-import=comtypes.server ^
    --hidden-import=comtypes.persist ^
    --hidden-import=comtypes.typeinfo ^
    --copy-metadata comtypes ^
    --collect-submodules comtypes ^
    --distpath=..\dist ^
    --workpath=..\build ^
    --specpath=.. ^
    main.py
cd ..

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo Debug executable: dist\NorwegianDictionary_DEBUG.exe
echo.
echo Run it and watch the console for debug messages!
echo.
pause