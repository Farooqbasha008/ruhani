@echo off
echo Running database setup tests...
cd ..
python -m app.db.test_db_setup

if %ERRORLEVEL% EQU 0 (
    echo Database setup tests completed successfully!
) else (
    echo Database setup tests failed with error code %ERRORLEVEL%
    echo Please check your .env file and ensure all required settings are provided.
)

pause