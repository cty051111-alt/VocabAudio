@echo off
setlocal
cd /d "%~dp0"
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"
"%PYEXE%" -m pip install -r requirements-dev.txt "pyinstaller>=6.11"
if errorlevel 1 goto fail
"%PYEXE%" -m pytest -q
if errorlevel 1 goto fail
"%PYEXE%" -m PyInstaller --noconfirm --clean --onefile --windowed --name VocabAudio --icon assets/VocabAudio.ico --add-data "assets/VocabAudio.ico;assets" --collect-all imageio_ffmpeg --collect-all pymupdf --hidden-import fitz app.py
if errorlevel 1 goto fail
"dist\VocabAudio.exe" --self-test
if errorlevel 1 goto fail
echo Build succeeded. Executable: dist\VocabAudio.exe
pause
exit /b 0
:fail
echo Build failed. Please copy the error text.
pause
exit /b 1
