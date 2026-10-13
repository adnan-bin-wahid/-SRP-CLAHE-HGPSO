@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo SRP-CLAHE-HGPSO v1.1 dependency repair

echo ============================================================

if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Run RUN_FIRST_CHECK.bat instead.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install "Jinja2>=3.1,<4"
if errorlevel 1 goto :fail
python scripts\verify_install.py
if errorlevel 1 goto :fail
python scripts\run_quick_check.py
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo REPAIR + QUICK CHECK PASSED

echo ============================================================
pause
exit /b 0

:fail
echo.
echo Repair/check failed. Copy the error and send it to ChatGPT.
pause
exit /b 1
