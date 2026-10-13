@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo SRP-CLAHE-HGPSO FIRST CHECK
echo ============================================================
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3.11 -m venv .venv 2>nul
    if errorlevel 1 py -m venv .venv
  ) else (
    python -m venv .venv
  )
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\verify_install.py
if errorlevel 1 goto :fail
python scripts\run_quick_check.py
if errorlevel 1 goto :fail
echo.
echo SUCCESS. Open results\quick_check\report\EXECUTION_REPORT.html
pause
exit /b 0
:fail
echo FAILED. Copy the error and send it to ChatGPT.
pause
exit /b 1
