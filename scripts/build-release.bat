@echo off
setlocal
set VERSION=%1
if "%VERSION%"=="" set VERSION=1.0.0

echo =========================================
echo Building PLAIN v%VERSION% for Windows
echo =========================================

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0
:: Navigate to project root (parent of scripts directory)
cd /d "%SCRIPT_DIR%\.."

:: 1. Build Interpreter
echo.
echo Building Interpreter...
echo   - plain.exe...
go build -ldflags="-s -w" -o plain.exe cmd/plain/main.go
if %errorlevel% neq 0 (
    echo Error: Failed to build interpreter.
    exit /b %errorlevel%
)
echo   + Interpreter built successfully.

:: 2. Build IDE
echo.
echo Building IDE...

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PyInstaller not found. Please run: pip install pyinstaller
    exit /b 1
)

echo   - Running PyInstaller...
python -m PyInstaller plain_ide.spec --noconfirm --clean
if %errorlevel% neq 0 (
    echo Error: PyInstaller failed.
    exit /b %errorlevel%
)
echo   + IDE built successfully.

:: 3. Package Release
echo.
echo Packaging Release...

set RELEASE_DIR=releases
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

set PLATFORM=windows-amd64
set PACKAGE_NAME=plain-v%VERSION%-%PLATFORM%
set PACKAGE_PATH=%RELEASE_DIR%\%PACKAGE_NAME%

if exist "%PACKAGE_PATH%" rmdir /s /q "%PACKAGE_PATH%"
mkdir "%PACKAGE_PATH%"

:: Copy build output
xcopy /E /I /Q "dist\plain-ide" "%PACKAGE_PATH%"

:: Copy Interpreter to root
echo   - Copying interpreter...
copy plain.exe "%PACKAGE_PATH%\" >nul
if %errorlevel% neq 0 (
    echo Error: Failed to copy plain.exe
    exit /b %errorlevel%
)

:: Copy Documentation
copy README.md "%PACKAGE_PATH%\" >nul
if exist LICENSE copy LICENSE "%PACKAGE_PATH%\" >nul
if exist INSTALLATION.md copy INSTALLATION.md "%PACKAGE_PATH%\" >nul

:: Copy Documentation Folder
if exist docs (
    mkdir "%PACKAGE_PATH%\docs"
    xcopy /E /I /Q "docs" "%PACKAGE_PATH%\docs"
)

:: Copy Examples
if exist examples (
    mkdir "%PACKAGE_PATH%\examples"
    echo   - Copying examples...
    for /r examples %%f in (*.plain) do copy "%%f" "%PACKAGE_PATH%\examples\" >nul
)

:: Create Zip
echo.
echo Creating Archive...
cd "%RELEASE_DIR%"
if exist "%PACKAGE_NAME%.zip" del "%PACKAGE_NAME%.zip"

:: Use PowerShell to zip
powershell -command "Compress-Archive -Path '%PACKAGE_NAME%' -DestinationPath '%PACKAGE_NAME%.zip'"

if exist "%PACKAGE_NAME%.zip" (
    echo   + Archive created: releases\%PACKAGE_NAME%.zip
) else (
    echo   ! Warning: Failed to create zip archive.
)

cd ..

echo.
echo =========================================
echo Build Complete!
echo =========================================
endlocal
