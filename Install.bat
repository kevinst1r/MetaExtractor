@echo off

:: Check for Python installation and install if not present
python -V >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iwr -Uri 'https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe' -OutFile 'python_installer.exe'; Start-Process -FilePath 'python_installer.exe' -Args '/quiet InstallAllUsers=1 PrependPath=1' -Wait; Remove-Item -Path 'python_installer.exe'}"
    echo Python installed.
) ELSE (
    echo Python is already installed.
)

REM Install required Python packages using python -m pip
echo Installing required Python packages...
python -m pip install PyQt5 Pillow

if %errorlevel% neq 0 (
    echo Failed to install required packages. Please check your Python installation.
    exit /b
)

echo Script finished. You can now run Meta Extractor!
pause
