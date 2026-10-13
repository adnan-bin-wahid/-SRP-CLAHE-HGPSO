from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
dataset=ROOT/"data"/"demo_dataset"
if not dataset.exists():
    subprocess.run([sys.executable,str(ROOT/"scripts"/"make_demo_dataset.py"),"--output",str(dataset)],check=True)
out=ROOT/"results"/"quick_check"
cmd=[sys.executable,str(ROOT/"scripts"/"run_full_experiment.py"),"--dataset",str(dataset),"--output",str(out),"--preset","quick","--max-test-images","3","--skip-ablations","--skip-stability","--skip-synthetic"]
print("Running:"," ".join(cmd))
subprocess.run(cmd,check=True)
print("QUICK CHECK PASSED")
