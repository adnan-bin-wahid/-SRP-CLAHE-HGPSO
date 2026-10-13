from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import load_config
from src.experiment import run_full_experiment


def main():
    ap = argparse.ArgumentParser(description="Run the complete SRP-CLAHE-HGPSO paper experiment.")
    ap.add_argument("--dataset", required=True, help="Path to SRP_Sentinel2_Final_240 folder.")
    ap.add_argument("--output", default="results/paper_run")
    ap.add_argument("--config", default=str(ROOT / "configs" / "paper.yaml"))
    ap.add_argument("--preset", choices=["quick","standard","paper_practical","paper_full"], default="standard")
    ap.add_argument("--force", action="store_true", help="Recompute cached main results.")
    ap.add_argument("--skip-calibration", action="store_true")
    ap.add_argument("--skip-ablations", action="store_true")
    ap.add_argument("--skip-stability", action="store_true")
    ap.add_argument("--skip-synthetic", action="store_true")
    ap.add_argument("--max-test-images", type=int, default=None, help="Debug-only cap; omit for final paper.")
    args = ap.parse_args()

    cfg = load_config(args.config)
    run_full_experiment(
        dataset_root=args.dataset,
        output_root=args.output,
        cfg=cfg,
        preset_name=args.preset,
        force=args.force,
        skip_calibration=args.skip_calibration,
        skip_ablations=args.skip_ablations,
        skip_stability=args.skip_stability,
        skip_synthetic=args.skip_synthetic,
        max_test_images=args.max_test_images,
    )


if __name__ == "__main__":
    main()
