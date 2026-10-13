from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config import load_config
from src.dataset import validate_dataset

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--config", default=str(ROOT / "configs" / "paper.yaml"))
args = ap.parse_args()
cfg = load_config(args.config)
df, warnings = validate_dataset(args.dataset, cfg)
print(df.groupby(["split","status"]).size() if not df.empty else "No scenes found")
print(f"Total scenes: {len(df)}")
for w in warnings:
    print("WARNING:", w)
if (df["status"] == "ERROR").any():
    print(df[df["status"] == "ERROR"][["chip_id","split","error"]].to_string(index=False))
    raise SystemExit(2)
print("Dataset validation PASSED")
