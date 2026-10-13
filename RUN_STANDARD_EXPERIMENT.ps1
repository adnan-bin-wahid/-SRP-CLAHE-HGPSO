param([Parameter(Mandatory=$true)][string]$Dataset)
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv\Scripts\python.exe")) { py -3.11 -m venv .venv }
Set-ExecutionPolicy -Scope Process Bypass -Force
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\validate_dataset.py --dataset $Dataset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts\run_full_experiment.py --dataset $Dataset --output "results\standard_run" --preset standard
exit $LASTEXITCODE
