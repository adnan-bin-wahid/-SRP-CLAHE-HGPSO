from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reporting import MAIN_METRICS, method_label
from src.stats import METRIC_DIRECTIONS, holm_adjust, summarize_by_method

PROPOSED = "SRP_CLAHE_HGPSO"


def paired_audit(df: pd.DataFrame, unit: str) -> pd.DataFrame:
    rows = []
    for metric in MAIN_METRICS:
        pivot = df.pivot(index=unit, columns="method", values=metric)
        metric_rows = []
        for baseline in sorted(set(pivot.columns) - {PROPOSED, "Original"}):
            pair = pivot[[PROPOSED, baseline]].replace([np.inf, -np.inf], np.nan).dropna()
            difference = (pair[PROPOSED] - pair[baseline]).to_numpy() * METRIC_DIRECTIONS[metric]
            nonzero = difference[difference != 0]
            if len(nonzero):
                result = wilcoxon(difference, zero_method="wilcox", alternative="two-sided", method="auto")
                ranks = rankdata(np.abs(nonzero), method="average")
                effect = float((ranks[nonzero > 0].sum() - ranks[nonzero < 0].sum()) / ranks.sum())
                statistic, pvalue = float(result.statistic), float(result.pvalue)
            else:
                statistic, pvalue, effect = 0.0, 1.0, 0.0
            metric_rows.append({
                "metric": metric, "baseline": baseline, "unit": unit,
                "n_pairs": len(pair), "n_nonzero": len(nonzero),
                "wilcoxon_stat": statistic, "p_value": pvalue,
                "rank_biserial_exact_ties": effect,
                "median_oriented_difference": float(np.median(difference)),
            })
        for row, adjusted in zip(metric_rows, holm_adjust([r["p_value"] for r in metric_rows])):
            row["p_holm"] = adjusted
            row["significant_holm"] = adjusted < 0.05
        rows.extend(metric_rows)
    return pd.DataFrame(rows)


def main_convergence(root: Path, destination: Path, test_ids: set[str]) -> dict:
    files = sorted((root / "raw/convergence/main").glob("*.csv"))
    history = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    assert set(history.chip_id) == test_ids
    assert not history.duplicated(["method", "chip_id", "generation"]).any()
    counts = {}
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for method, group in history.groupby("method"):
        pivot = group.pivot(index="generation", columns="chip_id", values="best_stable_utility").sort_index()
        assert set(pivot.columns) == test_ids
        # Carry an early-stopped chip's last score to its method's observed horizon.
        pivot = pivot.reindex(range(1, int(pivot.index.max()) + 1)).ffill()
        assert not pivot.isna().any().any()
        ax.plot(pivot.index, pivot.median(axis=1), label=method_label(method))
        counts[method] = {"chips": len(pivot.columns), "observed_horizon": int(pivot.index.max())}
    ax.set_xlabel("Generation")
    ax.set_ylabel("Median best stable visual utility")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    for extension in ("png", "pdf"):
        fig.savefig(destination / f"convergence_main_test.{extension}", dpi=300)
    plt.close(fig)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit saved paper evidence without rerunning enhancement.")
    parser.add_argument("--run", type=Path, default=ROOT / "results/standard_run")
    parser.add_argument("--output", type=Path, default=ROOT / "paper/evidence")
    args = parser.parse_args()
    root, output = args.run.resolve(), args.output.resolve()
    if root == output or root in output.parents:
        raise ValueError("Derived evidence must be outside the archived experiment directory.")
    output.mkdir(parents=True, exist_ok=True)
    paths = [root / "raw" / name for name in (
        "per_image_metrics.csv", "ablation_per_image.csv", "stability_per_run.csv", "synthetic_paired_per_image.csv",
    )]
    paths += [root / "manifest/run_manifest.json", root / "manifest/FROZEN_TEST_CONFIG.yaml",
              root / "manifest/dataset_validation.csv", root / "tables/main_results_summary.csv",
              root / "tables/wilcoxon_holm_pairwise.csv", root / "tables/validation_selection_per_run.csv"]
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    main_df = pd.read_csv(root / "raw/per_image_metrics.csv")
    assert not main_df.duplicated(["chip_id", "method"]).any()
    assert main_df.groupby("method").chip_id.nunique().nunique() == 1
    assert main_df[MAIN_METRICS].notna().all().all()
    manifest = json.loads((root / "manifest/run_manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("finished_unix") is not None
    assert main_df.chip_id.nunique() == manifest["test_images_used"]

    summary = summarize_by_method(main_df, MAIN_METRICS)
    existing_summary = pd.read_csv(root / "tables/main_results_summary.csv").set_index("method")
    checked_summary = summary.set_index("method").loc[existing_summary.index]
    numeric_columns = existing_summary.select_dtypes(include="number").columns
    assert np.allclose(existing_summary[numeric_columns], checked_summary[numeric_columns], equal_nan=True)
    summary.to_csv(output / "main_summary_verified.csv", index=False)

    pairwise = paired_audit(main_df, "chip_id")
    pairwise.to_csv(output / "pairwise_chip_audited.csv", index=False)
    existing_pairs = pd.read_csv(root / "tables/wilcoxon_holm_pairwise.csv")
    comparison = pairwise.merge(existing_pairs, on=["metric", "baseline"], suffixes=("_audit", "_archived"))
    comparison["effect_difference"] = comparison.rank_biserial_exact_ties - comparison.rank_biserial
    comparison["adjusted_p_difference"] = comparison.p_holm_audit - comparison.p_holm_archived
    comparison.to_csv(output / "statistical_implementation_audit.csv", index=False)

    metadata = pd.read_csv(root / "manifest/dataset_validation.csv")
    assert metadata[["location", "datetime"]].notna().all().all()
    metadata["group_id"] = metadata.location + "|" + metadata.datetime
    per_chip = main_df[["chip_id", "location", "datetime"]].drop_duplicates()
    assert len(per_chip) == main_df.chip_id.nunique()
    main_df["group_id"] = main_df.location + "|" + main_df.datetime
    grouped = main_df.groupby(["group_id", "method"], as_index=False)[MAIN_METRICS].mean()
    grouped.to_csv(output / "group_mean_metrics.csv", index=False)
    paired_audit(grouped, "group_id").to_csv(output / "pairwise_group_sensitivity.csv", index=False)
    metadata.groupby(["split", "location", "datetime"], as_index=False).agg(
        chips=("chip_id", "count"), valid_fraction_mean=("valid_fraction", "mean"),
    ).to_csv(output / "dataset_group_inventory.csv", index=False)

    proposed = main_df[main_df.method == PROPOSED].copy()
    thresholds = {"ndvi_mae": 0.005, "ndwi_mae": 0.005, "sam_mean_deg": 0.5, "clip_fraction": 0.005}
    violations = pd.DataFrame({metric: proposed[metric] > threshold for metric, threshold in thresholds.items()})
    feasible = ~violations.any(axis=1)
    recorded_feasible = proposed.feasible.astype(str).str.lower().eq("true")
    assert np.array_equal(feasible.to_numpy(), recorded_feasible.to_numpy())
    proposed.loc[~feasible, ["chip_id", "location", "datetime", *thresholds, "violation"]].to_csv(
        output / "infeasible_test_chips.csv", index=False,
    )
    cost_columns = ["runtime_sec", "evaluations_proxy", "evaluations_full", "iterations_run", "pixel_equivalent_evaluations"]
    main_df.groupby("method")[cost_columns].agg(["mean", "median", "min", "max"]).to_csv(output / "cost_summary.csv")

    ablation = pd.read_csv(root / "raw/ablation_per_image.csv")
    ablation_ids = set(ablation.chip_id)
    summarize_by_method(main_df[main_df.chip_id.isin(ablation_ids)], MAIN_METRICS).to_csv(
        output / "main_methods_on_ablation_subset.csv", index=False,
    )
    stability = pd.read_csv(root / "raw/stability_per_run.csv")
    within = stability.groupby(["method", "chip_id"])[
        ["stable_visual_utility", "ndvi_mae", "ndwi_mae", "sam_mean_deg", "runtime_sec"]
    ].agg(["mean", "std", "min", "max"])
    within.to_csv(output / "stability_within_chip.csv")
    synthetic = pd.read_csv(root / "raw/synthetic_paired_per_image.csv")
    synth_columns = ["psnr_to_clean_db", "ssim_to_clean", "runtime_sec"]
    summarize_by_method(synthetic.rename(columns={"source_chip_id": "chip_id"}), synth_columns).to_csv(
        output / "synthetic_summary_verified.csv", index=False,
    )

    indexed = summary.set_index("method")
    comparisons = {}
    for baseline in ("Original", "CLAHE", "CommonGain_CLAHE", "Parent_HGPSO_Reproduction"):
        comparisons[baseline] = {
            "contrast_change_pct_ratio_of_means": float(100 * (indexed.loc[PROPOSED, "local_rms_contrast_mean"] / indexed.loc[baseline, "local_rms_contrast_mean"] - 1)),
            "runtime_change_pct_ratio_of_means": float(100 * (indexed.loc[PROPOSED, "runtime_sec_mean"] / indexed.loc[baseline, "runtime_sec_mean"] - 1)),
        }
    calibration = pd.read_csv(root / "tables/validation_selection_per_run.csv")
    val_groups = set(metadata.loc[metadata.split == "validation", "group_id"])
    test_groups = set(metadata.loc[metadata.split == "test", "group_id"])
    calibration_ids = set(calibration.chip_id)
    audit = {
        "source_run": str(root), "source_hashes_sha256": hashes,
        "main_rows": len(main_df), "test_chips": main_df.chip_id.nunique(),
        "methods": sorted(main_df.method.unique()), "calibration_chips_used": len(calibration_ids),
        "calibration_evaluations": len(calibration), "validation_chips_available": int((metadata.split == "validation").sum()),
        "ablation_chips": len(ablation_ids), "ablation_variants": ablation.ablation.nunique(),
        "stability_chips": stability.chip_id.nunique(), "stability_seeds": stability.replicate.nunique(),
        "synthetic_chips": synthetic.source_chip_id.nunique(),
        "test_location_date_groups": len(test_groups), "validation_location_date_groups": len(val_groups),
        "location_date_split_overlap": sorted(val_groups & test_groups),
        "location_split_overlap": sorted(set(metadata.loc[metadata.split == "validation", "location"]) & set(metadata.loc[metadata.split == "test", "location"])),
        "feasible_test_chips": int(feasible.sum()), "infeasible_test_chips": int((~feasible).sum()),
        "threshold_exceedances": {k: int(violations[k].sum()) for k in thresholds},
        "max_effect_size_change_exact_ties": float(comparison.effect_difference.abs().max()),
        "max_adjusted_p_change": float(comparison.adjusted_p_difference.abs().max()),
        "holm_decision_changes": int((comparison.significant_holm_audit != comparison.significant_holm_archived).sum()),
        "ratio_of_means_comparisons": comparisons,
        "main_convergence": main_convergence(root, output, set(main_df.chip_id)),
        "notes": [
            "Group-level tests are post hoc sensitivity analyses using location and acquisition time as a proxy for source scene.",
            "Audited ranks use SciPy exact-equality ties; archived effects use numpy.isclose tie grouping.",
            "Runtime measurements exclude scene loading and preprocessing context preparation; they include candidate metric evaluation.",
            "Clip fraction counts clipped band samples over four times the number of valid pixels, not unique pixels.",
            "No enhancement experiment or input evidence file is modified by this audit.",
        ],
    }
    assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == value for name, value in hashes.items())
    (output / "evidence_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in (
        "main_rows", "test_chips", "calibration_chips_used", "feasible_test_chips", "infeasible_test_chips",
        "test_location_date_groups", "max_effect_size_change_exact_ties", "max_adjusted_p_change", "holm_decision_changes",
    )}, indent=2))
    print(f"Derived evidence: {output}")


if __name__ == "__main__":
    main()
