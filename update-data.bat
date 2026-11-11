@echo off
rem Load the newest SeminoleCounty.zip (from this folder or your Downloads) into the HomeOwners website.
rem You can also drag a zip file onto this file.
cd /d "%~dp0"
python update_data.py %*
echo.
pause
