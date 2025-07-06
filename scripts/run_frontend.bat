@echo off
echo Starting RUHANI frontend development server...
cd ..
npm run dev

if %ERRORLEVEL% NEQ 0 (
    echo Frontend server stopped with error code %ERRORLEVEL%
    echo Please check the logs for more information.
    pause
)