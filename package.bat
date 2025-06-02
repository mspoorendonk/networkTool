@echo off
REM =====================================================================================
REM  package.bat - Build, package, and optionally install Inno Setup for NetworkTool
REM
REM  This script automates the following steps:
REM   1. Checks if Inno Setup (ISCC.exe) is installed; if not, downloads and installs it.
REM   2. Cleans previous build, dist, and Output folders.
REM   3. Runs PyInstaller to create a Windows executable from your Python project.
REM   4. Runs Inno Setup to create a Windows installer from the executable.
REM   5. Copies the final installer to a configurable output folder (see OUTPUT_FOLDER).
REM
REM  Configuration:
REM   - Adjust INNO_URL if a different Inno Setup version is needed.
REM   - Set OUTPUT_FOLDER to your desired destination for the installer.
REM   - Make sure 'networktool.spec' and 'inno setup script.iss' are present in the project root.
REM
REM  Usage:
REM   - Run this script from your project root (not from dist/ or src/).
REM   - Requires PowerShell for downloading Inno Setup if not present.
REM   - Requires PyInstaller and Inno Setup (will auto-install Inno Setup if missing).
REM =====================================================================================
setlocal

REM === Configuration ===
set "INNO_URL=https://jrsoftware.org/download.php/is.exe"
set "INNO_INSTALLER=%TEMP%\inno_setup_installer.exe"
set "INNO_DEFAULT_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "OUTPUT_FOLDER=G:\My Drive\Project\networkTool\Output"

REM === Check if ISCC.exe is in PATH or default location ===
where ISCC.exe >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Inno Setup is already installed and in PATH.
    set "ISCC=ISCC.exe"
    goto :run_build
)

if exist "%INNO_DEFAULT_PATH%" (
    echo Inno Setup is already installed at "%INNO_DEFAULT_PATH%".
    set "ISCC=%INNO_DEFAULT_PATH%"
    goto :run_build
)

REM === Download and install Inno Setup ===
echo Inno Setup not found. Downloading installer...
powershell -Command "Invoke-WebRequest -Uri '%INNO_URL%' -OutFile '%INNO_INSTALLER%'"
if not exist "%INNO_INSTALLER%" (
    echo Failed to download Inno Setup installer!
    exit /b 1
)
echo Installing Inno Setup silently...
"%INNO_INSTALLER%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
if not exist "%INNO_DEFAULT_PATH%" (
    echo Inno Setup installation failed!
    exit /b 1
)
echo Inno Setup installed successfully.
set "ISCC=%INNO_DEFAULT_PATH%"

:run_build
REM === Build with PyInstaller, then package with Inno Setup, then copy output ===
rem I manually delete the folders as they were giving me errors
rmdir /s /q "build"
rmdir /s /q "dist"
rmdir /s /q "Output"
echo "====================================== creating executable =============================================="
"pyinstaller.exe" --noconfirm "networktool.spec" || exit /b 1
echo "====================================== creating installer =============================================="
"%ISCC%" "inno setup script.iss" || exit /b 1
echo "======================================= copying to output folder =============================================="
if exist "%OUTPUT_FOLDER%" (
    copy /Y "Output\Networktool setup.exe" "%OUTPUT_FOLDER%"
) else (
    echo Destination folder "%OUTPUT_FOLDER%" does not exist. Please create it or update the path in package.bat.
)
echo "============================================= done =============================================="
echo Packaging complete.
endlocal
