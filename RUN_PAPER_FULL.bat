@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: RUN_PAPER_FULL.bat "E:\path\SRP_Sentinel2_Final_240"
  echo WARNING: paper_full uses the parent 30x100 optimizer and repeated-seed/ablation experiments.
  echo It can take many hours or days on a CPU. Runs are resumable.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
  echo Run RUN_FIRST_CHECK.bat once first.
  pause
  exit /b 1
)
python scripts\run_full_experiment.py --dataset "%~1" --output "results\paper_full" --preset paper_full
if errorlevel 1 goto :fail
echo SUCCESS. Send results\paper_full\PAPER_RESULTS_PACKAGE.zip to ChatGPT.
pause
exit /b 0
:fail
echo FAILED. The experiment is resumable; re-run the same BAT after fixing the error.
pause
exit /b 1
