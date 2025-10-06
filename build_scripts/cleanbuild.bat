@echo off
echo ====================================
echo   Cleaning Build Files
echo ====================================
echo.

echo Removing build artifacts...

if exist "build" (
    echo Deleting build folder...
    rmdir /s /q "build"
)

if exist "dist" (
    echo Deleting dist folder...
    rmdir /s /q "dist"
)

if exist "Output" (
    echo Deleting Output folder...
    rmdir /s /q "Output"
)

if exist "*.spec" (
    echo Deleting spec files...
    del /q "*.spec"
)

echo.
echo ====================================
echo   Clean Complete!
echo ====================================
echo.
echo All build files have been removed.
echo You can now rebuild with build_installer.bat
echo.
pause