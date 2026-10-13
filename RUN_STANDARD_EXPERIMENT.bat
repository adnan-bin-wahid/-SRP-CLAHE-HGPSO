@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag your SRP_Sentinel2_Final_240 folder onto this BAT file
  echo OR run: RUN_STANDARD_EXPERIMENT.bat "E:\path\SRP_Sentinel2_Final_240"
  pause
  exit /b 1
)
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
if errorlevel 1 goto :fail
python scripts\validate_dataset.py --dataset "%~1"
if errorlevel 1 goto :fail
python scripts\run_full_experiment.py --dataset "%~1" --output "results\standard_run" --preset standard
if errorlevel 1 goto :fail
echo.
echo SUCCESS.
echo Open results\standard_run\report\EXECUTION_REPORT.html
echo Send results\standard_run\PAPER_RESULTS_PACKAGE.zip to ChatGPT.
pause
exit /b 0
:fail
echo FAILED. Re-running resumes cached results. Copy the error to ChatGPT.
pause
exit /b 1
