@echo off
cd /d "%~dp0"  ; Ensure we are in the correct directory
start /min cmd /c "python main.py"
