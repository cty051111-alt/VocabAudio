@echo off
setlocal
cd /d "%~dp0"
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if exist "%PYEXE%" goto run
where py >nul 2>nul
if not errorlevel 1 goto via_py
where python >nul 2>nul
if not errorlevel 1 goto via_python
echo Python was not found. Please install Python 3.13.
pause
exit /b 1
:via_py
py -3.13 app.py
if errorlevel 1 pause
exit /b %errorlevel%
:via_python
python app.py
if errorlevel 1 pause
exit /b %errorlevel%
:run
"%PYEXE%" app.py
if errorlevel 1 pause
exit /b %errorlevel%
