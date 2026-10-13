@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: RUN_PAPER_PRACTICAL.bat "E:\path\SRP_Sentinel2_Final_240"
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
  echo Run RUN_FIRST_CHECK.bat once first, or create .venv and install requirements.
  pause
  exit /b 1
)
python scripts\run_full_experiment.py --dataset "%~1" --output "results\paper_practical" --preset paper_practical
if errorlevel 1 goto :fail
echo SUCCESS. Send results\paper_practical\PAPER_RESULTS_PACKAGE.zip to ChatGPT.
pause
exit /b 0
:fail
echo FAILED. Run the same command again to resume cached work.
pause
exit /b 1
