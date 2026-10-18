@echo off
setlocal
cd /d "%~dp0"
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if exist "%PYEXE%" goto run
where py >nul 2>nul
if not errorlevel 1 goto via_py
where python >nul 2>nul
if not errorlevel 1 goto via_python
echo Python 3 not found.
pause
exit /b 1
:via_py
py -3.13 -m pip install -r requirements.txt
pause
exit /b
:via_python
python -m pip install -r requirements.txt
pause
exit /b
:run
"%PYEXE%" -m pip install -r requirements.txt
"%PYEXE%" -c "import pymupdf; print('PDF module OK')"
pause
