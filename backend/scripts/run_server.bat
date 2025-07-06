@echo off
echo Starting RUHANI backend server...
cd ..
python run.py

if %ERRORLEVEL% NEQ 0 (
    echo Server stopped with error code %ERRORLEVEL%
    echo Please check the logs for more information.
    pause
)