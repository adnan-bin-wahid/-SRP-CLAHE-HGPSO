from __future__ import annotations

import json
import math
import os
import shutil
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import save_yaml
from .dataset import choose_representative_ids, validate_dataset
from .io import cube_to_rgb, find_dataset_splits, fit_display_model, load_manifest, load_scene, manifest_lookup
from .methods import MethodResult, run_method
from .metrics import paired_clean_metrics
from .reporting import build_execution_report, package_results, save_rgb
from .stats import paired_statistics, summarize_by_method
from .synthetic import degrade_scene
from .utils import environment_manifest, read_json, stable_seed, try_git_commit, write_json


def result_record(result: MethodResult, scene, proxy_size: int | None = None) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "chip_id": result.chip_id,
        "method": result.method,
        "split": scene.split,
        "location": scene.location,
        "datetime": scene.datetime,
        "cloud_fraction": scene.cloud_fraction,
        "valid_fraction": float(scene.valid_mask.mean()),
        "height": scene.height,
        "width": scene.width,
        "runtime_sec": result.runtime_sec,
        "peak_rss_mb": result.peak_rss_mb,
        "evaluations_proxy": result.evaluations_proxy,
        "evaluations_full": result.evaluations_full,
        "iterations_run": result.iterations_run,
        "stopped_early": result.stopped_early,
        "feasible": result.feasible,
        "violation": result.violation,
        "stable_visual_utility": result.stable_visual_utility,
        "notes": result.notes,
    }
    rec.update(result.metrics)
    for k, v in result.parameters.items():
        rec[f"param_{k}"] = v
    if proxy_size and result.evaluations_proxy:
        full_px = scene.height * scene.width
        proxy_px = min(proxy_size, scene.height, scene.width) ** 2
        rec["pixel_equivalent_evaluations"] = (
            result.evaluations_proxy * proxy_px / max(full_px, 1) + result.evaluations_full
        )
    else:
        rec["pixel_equivalent_evaluations"] = float(result.evaluations_full)
    return rec


def _result_json_payload(result: MethodResult, record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record": record,
        "parameters": result.parameters,
        "history": result.history or [],
    }


def _result_cache_path(output_root: Path, chip_id: str, method: str, namespace="main") -> Path:
    return output_root / "raw" / "method_results" / namespace / chip_id / f"{method}.json"


def _proxy_for_method(method: str, preset: dict[str, Any], custom: dict[str, Any] | None = None) -> int | None:
    custom = custom or {}
    if method in {"PSO_Transform", "GWO_Transform", "Parent_HGPSO_Reproduction"}:
        return int(custom.get("proxy_size", preset["baseline_proxy_size"]))
    if method.startswith("SRP_"):
        return int(custom.get("proxy_size", preset["proposed_proxy_size"]))
    return None


def run_cached(
    scene,
    cfg: dict[str, Any],
    method: str,
    preset: dict[str, Any],
    base_seed: int,
    output_root: Path,
    namespace: str,
    custom: dict[str, Any] | None = None,
    force: bool = False,
    save_image_path: Path | None = None,
) -> tuple[dict[str, Any], MethodResult | None]:
    cache = _result_cache_path(output_root, scene.chip_id, method, namespace)
    if cache.exists() and not force and save_image_path is None:
        payload = read_json(cache)
        return payload["record"], None

    result = run_method(scene, cfg, method, preset, base_seed, custom=custom)
    proxy = _proxy_for_method(method, preset, custom)
    record = result_record(result, scene, proxy)
    write_json(_result_json_payload(result, record), cache)

    if result.history:
        hdir = output_root / "raw" / "convergence" / namespace
        hdir.mkdir(parents=True, exist_ok=True)
        hdf = pd.DataFrame(result.history)
        hdf.insert(0, "method", method)
        hdf.insert(0, "chip_id", scene.chip_id)
        hdf.to_csv(hdir / f"{scene.chip_id}__{method}.csv", index=False)

    if save_image_path is not None and result.enhanced_rgb is not None:
        save_rgb(save_image_path, result.enhanced_rgb)

    return record, result


def _select_validation_config(
    dataset_root: Path,
    cfg: dict[str, Any],
    preset: dict[str, Any],
    validation_ids: list[str],
    lookup: dict[str, dict[str, Any]],
    output_root: Path,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Sequential one-factor validation selection using a deliberately small budget.

    This avoids spending the full paper budget on dozens of validation variants.
    The selected configuration is frozen before test-set evaluation.
    """
    frozen = deepcopy(cfg)
    records = []
    # Small fixed calibration search budget, independent of paper test budget.
    cal_pop = min(8, preset["proposed_population"])
    cal_gen = min(12, preset["proposed_generations"])

    axes = [
        ("local_window", [7, 15, 31]),
        ("gain_sigma", [0.0, 1.0, 2.0]),
        ("gain_max", [1.5, 2.0, 2.5]),
    ]

    for axis, values in axes:
        variant_scores = []
        for val in values:
            per = []
            for chip in validation_ids:
                scene = load_scene(
                    dataset_root / "validation" / chip,
                    "validation",
                    reflectance_scale=frozen["project"]["reflectance_scale"],
                    cloud_mask_name=frozen["input"]["cloud_mask_name"],
                    cloud_values=frozen["input"]["cloud_values"],
                    min_valid_fraction=frozen["input"]["min_valid_fraction"],
                    manifest_row=lookup.get(chip),
                )
                prep_override = {}
                if axis == "local_window": prep_override["local_window"] = int(val)
                if axis == "gain_sigma": prep_override["gain_sigma"] = float(val)
                if axis == "gain_max": prep_override["gain_max"] = float(val)
                custom = {
                    "population": cal_pop,
                    "generations": cal_gen,
                    "elite_count": min(3, preset["proposed_elites"]),
                    "proxy_size": min(256, scene.height, scene.width),
                    "preprocessing": prep_override,
                    "seed_tag": f"validation_{axis}_{val}",
                }
                rec, _ = run_cached(
                    scene, frozen, "SRP_CLAHE_HGPSO", preset,
                    frozen["project"]["base_seed"], output_root,
                    namespace=f"validation_{axis}_{str(val).replace('.','p')}",
                    custom=custom,
                )
                per.append(rec)
                records.append({"axis": axis, "value": val, **rec})
            pdf = pd.DataFrame(per)
            feasible_rate = float(pd.to_numeric(pdf["feasible"], errors="coerce").fillna(False).mean())
            utility = float(pd.to_numeric(pdf["stable_visual_utility"], errors="coerce").median())
            violation = float(pd.to_numeric(pdf["violation"], errors="coerce").fillna(0).median())
            runtime = float(pd.to_numeric(pdf["runtime_sec"], errors="coerce").median())
            variant_scores.append((val, feasible_rate, utility, violation, runtime))

        # Prefer feasibility, then visual utility, then lower violation/runtime.
        best_val = max(variant_scores, key=lambda x: (x[1], x[2], -x[3], -x[4]))[0]
        if axis == "local_window": frozen["preprocessing"]["local_window"] = int(best_val)
        elif axis == "gain_sigma": frozen["preprocessing"]["gain_sigma"] = float(best_val)
        elif axis == "gain_max": frozen["preprocessing"]["gain_max"] = float(best_val)

    return frozen, pd.DataFrame(records)


def _load_scene_for_id(dataset_root: Path, split: str, chip: str, cfg: dict[str, Any], lookup):
    return load_scene(
        dataset_root / split / chip,
        split,
        reflectance_scale=cfg["project"]["reflectance_scale"],
        cloud_mask_name=cfg["input"]["cloud_mask_name"],
        cloud_values=cfg["input"]["cloud_values"],
        min_valid_fraction=cfg["input"]["min_valid_fraction"],
        manifest_row=lookup.get(chip),
    )


def run_main_benchmark(
    dataset_root: Path,
    cfg: dict[str, Any],
    preset: dict[str, Any],
    test_ids: list[str],
    lookup,
    output_root: Path,
    qualitative_ids: list[str],
    force: bool = False,
) -> pd.DataFrame:
    rows = []
    methods = cfg["methods"]["main"]
    qroot = output_root / "artifacts" / "qualitative"
    for i, chip in enumerate(test_ids, 1):
        scene = _load_scene_for_id(dataset_root, "test", chip, cfg, lookup)
        print(f"[MAIN {i}/{len(test_ids)}] {chip}", flush=True)
        for method in methods:
            img_path = qroot / chip / f"{method}.png" if chip in qualitative_ids else None
            rec, _ = run_cached(
                scene, cfg, method, preset, cfg["project"]["base_seed"],
                output_root, namespace="main", force=force, save_image_path=img_path,
            )
            rows.append(rec)
    df = pd.DataFrame(rows)
    raw_dir = output_root / "raw"; raw_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_dir / "per_image_metrics.csv", index=False)
    return df


def run_ablations(
    dataset_root: Path,
    cfg: dict[str, Any],
    preset: dict[str, Any],
    ids: list[str],
    lookup,
    output_root: Path,
) -> pd.DataFrame:
    rows = []
    base_seed = cfg["project"]["base_seed"]

    # Component ablations A1/A2 are represented by main-method results on these same scenes.
    for chip in ids:
        scene = _load_scene_for_id(dataset_root, "test", chip, cfg, lookup)

        variants = []
        variants.append(("A3_no_constraints", "SRP_no_constraints", {}))
        for v in cfg["ablation"]["gain_sigma"]:
            variants.append((f"A4_gain_sigma_{v}", "SRP_CLAHE_HGPSO", {"preprocessing": {"gain_sigma": float(v)}, "seed_tag": f"A4_{v}"}))
        for lo, hi in cfg["ablation"]["gain_bounds"]:
            variants.append((f"A5_gain_{lo}_{hi}", "SRP_CLAHE_HGPSO", {"preprocessing": {"gain_min": float(lo), "gain_max": float(hi)}, "seed_tag": f"A5_{lo}_{hi}"}))
        for v in cfg["ablation"]["proxy_size"]:
            if v <= max(scene.height, scene.width):
                variants.append((f"A6_proxy_{v}", "SRP_CLAHE_HGPSO", {"proxy_size": int(v), "seed_tag": f"A6_{v}"}))
        for pop, gen in cfg["ablation"]["search_budget"]:
            variants.append((f"A7_budget_{pop}x{gen}", "SRP_CLAHE_HGPSO", {"population": int(pop), "generations": int(gen), "seed_tag": f"A7_{pop}_{gen}"}))

        # A8 fixed a,b,c from validation best-parameter medians if available.
        fixed_path = output_root / "manifest" / "reduced_search_fixed_abc.json"
        if fixed_path.exists():
            fixed = read_json(fixed_path)
        else:
            fixed = {"a": 0.8, "b": 0.3, "c": 0.5}
        variants.append(("A8_reduced_kp", "SRP_reduced_kp", {"fixed_abc": fixed, "seed_tag": "A8_reduced"}))

        names = ["entropy", "contrast", "edge", "sharpness", "ssim"]
        for label, vals in cfg["ablation"]["objective_weights"].items():
            weights = {k: float(v) for k, v in zip(names, vals)}
            variants.append((f"A9_weights_{label}", "SRP_CLAHE_HGPSO", {"weights": weights, "seed_tag": f"A9_{label}"}))

        for label, method, custom in variants:
            rec, _ = run_cached(
                scene, cfg, method, preset, base_seed, output_root,
                namespace=f"ablation/{label}", custom=custom,
            )
            rows.append({"ablation": label, **rec})

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # Aggregate for paper-ready ablation table.
    metrics = ["stable_visual_utility","entropy","local_rms_contrast","ndvi_mae","ndwi_mae","sam_mean_deg","clip_fraction","runtime_sec","pixel_equivalent_evaluations"]
    agg = []
    for label, g in df.groupby("ablation"):
        row = {"ablation": label, "n": int(g["chip_id"].nunique())}
        for m in metrics:
            if m in g:
                x = pd.to_numeric(g[m], errors="coerce").dropna()
                if len(x):
                    row[f"{m}_median"] = float(x.median())
                    row[f"{m}_mean"] = float(x.mean())
        if "feasible" in g:
            f = pd.to_numeric(g["feasible"], errors="coerce").dropna()
            row["feasible_rate"] = float(f.mean()) if len(f) else np.nan
        agg.append(row)
    out = pd.DataFrame(agg)
    df.to_csv(output_root / "raw" / "ablation_per_image.csv", index=False)
    return out


def run_stability(
    dataset_root: Path,
    cfg: dict[str, Any],
    preset: dict[str, Any],
    ids: list[str],
    seeds: int,
    lookup,
    output_root: Path,
) -> pd.DataFrame:
    rows = []
    for chip in ids:
        scene = _load_scene_for_id(dataset_root, "test", chip, cfg, lookup)
        for method in ["Parent_HGPSO_Reproduction", "SRP_CLAHE_HGPSO"]:
            for s in range(seeds):
                custom = {"seed_tag": f"stability_seed_{s}"}
                rec, _ = run_cached(
                    scene, cfg, method, preset, cfg["project"]["base_seed"],
                    output_root, namespace=f"stability/seed_{s}", custom=custom,
                )
                rows.append({"replicate": s, **rec})
    raw = pd.DataFrame(rows)
    raw.to_csv(output_root / "raw" / "stability_per_run.csv", index=False)
    if raw.empty:
        return raw
    agg = []
    for method, g in raw.groupby("method"):
        row = {"method": method, "images": int(g["chip_id"].nunique()), "seeds": int(g["replicate"].nunique())}
        for m in ["stable_visual_utility","ndvi_mae","ndwi_mae","sam_mean_deg","runtime_sec"]:
            if m in g:
                x = pd.to_numeric(g[m], errors="coerce").dropna()
                row[f"{m}_mean"] = float(x.mean()) if len(x) else np.nan
                row[f"{m}_std"] = float(x.std(ddof=1)) if len(x)>1 else 0.0
                row[f"{m}_cv"] = float(x.std(ddof=1) / max(abs(x.mean()),1e-12)) if len(x)>1 else 0.0
        agg.append(row)
    return pd.DataFrame(agg)


def run_synthetic_track(
    dataset_root: Path,
    cfg: dict[str, Any],
    preset: dict[str, Any],
    ids: list[str],
    lookup,
    output_root: Path,
) -> pd.DataFrame:
    rows = []
    methods = ["Original", "CLAHE", "Parent_HGPSO_Reproduction", "SRP_CLAHE_HGPSO"]
    for chip in ids:
        clean = _load_scene_for_id(dataset_root, "test", chip, cfg, lookup)
        degraded = degrade_scene(clean, stable_seed(cfg["project"]["base_seed"], chip, "synthetic"), mode="mixed")
        clean_model = fit_display_model(clean, tuple(cfg["preprocessing"]["display_percentiles"]))
        clean_rgb = cube_to_rgb(clean.cube, clean_model)
        for method in methods:
            rec, result = run_cached(
                degraded, cfg, method, preset, cfg["project"]["base_seed"],
                output_root, namespace="synthetic_mixed",
                custom={"seed_tag": "synthetic_mixed"},
                force=False,
            )
            # If loaded from cache, rerun only to recover enhanced cube for paired metrics.
            if result is None or result.enhanced_cube is None:
                result = run_method(degraded, cfg, method, preset, cfg["project"]["base_seed"], custom={"seed_tag": "synthetic_mixed"})
            enhanced_rgb_clean_scale = cube_to_rgb(result.enhanced_cube, clean_model)
            paired = paired_clean_metrics(clean_rgb, enhanced_rgb_clean_scale, clean.valid_mask)
            rows.append({"source_chip_id": chip, "method": method, **paired, "runtime_sec": result.runtime_sec})
    raw = pd.DataFrame(rows)
    raw.to_csv(output_root / "raw" / "synthetic_paired_per_image.csv", index=False)
    metrics = ["psnr_to_clean_db","ssim_to_clean","runtime_sec"]
    return summarize_by_method(raw.rename(columns={"source_chip_id":"chip_id"}), metrics)


def collect_history(output_root: Path) -> pd.DataFrame:
    files = list((output_root / "raw" / "convergence").rglob("*.csv")) if (output_root / "raw" / "convergence").exists() else []
    dfs = []
    for p in files:
        try:
            dfs.append(pd.read_csv(p))
        except Exception:
            pass
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def derive_reduced_params(validation_df: pd.DataFrame, output_root: Path) -> dict[str, float]:
    sub = validation_df.copy()
    vals = {}
    for p in ("a","b","c"):
        col = f"param_{p}"
        x = pd.to_numeric(sub.get(col, pd.Series(dtype=float)), errors="coerce").dropna()
        vals[p] = float(x.median()) if len(x) else {"a":0.8,"b":0.3,"c":0.5}[p]
    write_json(vals, output_root / "manifest" / "reduced_search_fixed_abc.json")
    return vals


def run_full_experiment(
    dataset_root: str | Path,
    output_root: str | Path,
    cfg: dict[str, Any],
    preset_name: str,
    force: bool = False,
    skip_calibration: bool = False,
    skip_ablations: bool = False,
    skip_stability: bool = False,
    skip_synthetic: bool = False,
    max_test_images: int | None = None,
) -> dict[str, Any]:
    dataset_root = Path(dataset_root).resolve()
    output_root = Path(output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    for d in ["raw","tables","figures","report","manifest","artifacts"]:
        (output_root / d).mkdir(parents=True, exist_ok=True)

    preset = cfg["presets"][preset_name]
    print("[0] Validating dataset...", flush=True)
    validation_df, warnings = validate_dataset(dataset_root, cfg)
    validation_df.to_csv(output_root / "manifest" / "dataset_validation.csv", index=False)
    if (validation_df["status"] == "ERROR").any():
        bad = validation_df[validation_df["status"] == "ERROR"]
        raise RuntimeError(f"Dataset validation failed for {len(bad)} scenes. See manifest/dataset_validation.csv")

    manifest = load_manifest(dataset_root)
    lookup = manifest_lookup(manifest)
    split_dirs = find_dataset_splits(dataset_root)
    validation_ids_all = [p.name for p in split_dirs.get("validation", [])]
    test_ids_all = [p.name for p in split_dirs.get("test", [])]
    if max_test_images is not None:
        test_ids_all = test_ids_all[:max_test_images]

    env = environment_manifest()
    run_info = {
        "project": cfg["project"]["name"],
        "preset": preset_name,
        "started_unix": time.time(),
        "dataset_root": str(dataset_root),
        "validation_images_available": len(validation_ids_all),
        "test_images_used": len(test_ids_all),
        "environment": env,
        "git_commit": try_git_commit(Path(__file__).resolve().parents[1]),
        "dataset_adaptation": "Radiant Earth Sentinel-2 L2A 512x512 B02/B03/B04/B08 chips with expert cloud_mask.tif; cloud mask is used instead of SCL.",
    }
    write_json(run_info, output_root / "manifest" / "run_manifest.json")
    save_yaml(cfg, output_root / "manifest" / "starting_config.yaml")

    # Validation/calibration set is deterministic and separated from test.
    nval = min(preset["validation_scenes"], len(validation_ids_all))
    val_ids = choose_representative_ids(validation_df, "validation", nval, cfg["project"]["base_seed"])
    frozen_cfg = deepcopy(cfg)
    calibration_df = pd.DataFrame()
    if not skip_calibration and val_ids:
        print("[1] Validation-only configuration selection...", flush=True)
        frozen_cfg, calibration_df = _select_validation_config(dataset_root, cfg, preset, val_ids, lookup, output_root)
        calibration_df.to_csv(output_root / "tables" / "validation_selection_per_run.csv", index=False)
    save_yaml(frozen_cfg, output_root / "manifest" / "FROZEN_TEST_CONFIG.yaml")

    # Run final proposed on validation IDs once to derive reduced-search a,b,c medians.
    val_param_rows = []
    for chip in val_ids:
        scene = _load_scene_for_id(dataset_root, "validation", chip, frozen_cfg, lookup)
        rec, _ = run_cached(scene, frozen_cfg, "SRP_CLAHE_HGPSO", preset, frozen_cfg["project"]["base_seed"], output_root, namespace="validation_final")
        val_param_rows.append(rec)
    derive_reduced_params(pd.DataFrame(val_param_rows), output_root)

    # Qualitative IDs from the test set.
    qn = min(frozen_cfg["project"].get("qualitative_scene_count",8), len(test_ids_all))
    qdf = validation_df[(validation_df["split"]=="test") & (validation_df["chip_id"].isin(test_ids_all))]
    qualitative_ids = choose_representative_ids(qdf, "test", qn, frozen_cfg["project"]["base_seed"])
    write_json({"qualitative_chip_ids": qualitative_ids}, output_root / "manifest" / "qualitative_selection.json")

    print("[2] Main frozen test-set benchmark...", flush=True)
    main_df = run_main_benchmark(dataset_root, frozen_cfg, preset, test_ids_all, lookup, output_root, qualitative_ids, force=force)

    # Automatic sanity checks based on analytical invariance expectation.
    prop = main_df[main_df["method"] == "SRP_CLAHE_HGPSO"]
    if not prop.empty:
        feasible_rate = pd.to_numeric(prop["feasible"], errors="coerce").fillna(False).mean()
        if feasible_rate < 0.90:
            warnings.append(f"Proposed full-resolution feasibility rate is only {feasible_rate:.1%}; inspect constraints/gain clipping before writing claims.")
        low_clip = prop[pd.to_numeric(prop["clip_fraction"], errors="coerce") < 1e-6]
        if len(low_clip) and pd.to_numeric(low_clip["ndvi_mae"], errors="coerce").median() > 1e-5:
            warnings.append("Unexpected NDVI error despite near-zero clipping; verify identical gain application/numerical pipeline.")

    # Statistical analysis on complete same-data pairs.
    stats_metrics = frozen_cfg["reporting"]["primary_metrics"]
    inferential_df = main_df[main_df["method"] != "Original"].copy()
    omnibus_df, pairwise_df = paired_statistics(inferential_df, stats_metrics, alpha=frozen_cfg["reporting"]["alpha"])

    print("[3] Ablation study...", flush=True)
    ablation_out = pd.DataFrame()
    if not skip_ablations:
        aid = choose_representative_ids(qdf, "test", min(preset["ablation_scenes"], len(test_ids_all)), frozen_cfg["project"]["base_seed"]+1)
        ablation_out = run_ablations(dataset_root, frozen_cfg, preset, aid, lookup, output_root)

    print("[4] Repeated-seed optimizer stability...", flush=True)
    stability_out = pd.DataFrame()
    if not skip_stability:
        sid = choose_representative_ids(qdf, "test", min(preset["stability_scenes"], len(test_ids_all)), frozen_cfg["project"]["base_seed"]+2)
        stability_out = run_stability(dataset_root, frozen_cfg, preset, sid, preset["stability_seeds"], lookup, output_root)

    print("[5] Paired synthetic clean-reference stress test...", flush=True)
    synthetic_out = pd.DataFrame()
    if not skip_synthetic:
        syid = choose_representative_ids(qdf, "test", min(preset["synthetic_scenes"], len(test_ids_all)), frozen_cfg["project"]["base_seed"]+3)
        synthetic_out = run_synthetic_track(dataset_root, frozen_cfg, preset, syid, lookup, output_root)

    history_df = collect_history(output_root)

    # Create qualitative grid after cached images have been emitted.
    from .reporting import make_qualitative_grid
    qmethods = ["Original","CLAHE","Parent_HGPSO_Reproduction","CommonGain_CLAHE","SRP_CLAHE_HGPSO"]
    make_qualitative_grid(output_root / "artifacts" / "qualitative", qualitative_ids, qmethods, output_root / "figures" / "qualitative_comparison_grid.jpg")

    run_info["finished_unix"] = time.time()
    run_info["frozen_config"] = frozen_cfg["preprocessing"]
    run_info["warnings"] = warnings
    write_json(run_info, output_root / "manifest" / "run_manifest.json")

    build_execution_report(
        output_root, run_info, main_df, omnibus_df, pairwise_df,
        ablation_out, stability_out, synthetic_out, history_df, warnings,
    )

    payload = {
        "run_manifest": run_info,
        "warnings": warnings,
        "main_summary": summarize_by_method(main_df, frozen_cfg["reporting"]["primary_metrics"]).to_dict(orient="records"),
        "friedman": omnibus_df.to_dict(orient="records"),
        "wilcoxon_holm": pairwise_df.to_dict(orient="records"),
        "ablation_summary": ablation_out.to_dict(orient="records"),
        "stability_summary": stability_out.to_dict(orient="records"),
        "synthetic_summary": synthetic_out.to_dict(orient="records"),
        "files_to_send_chatgpt": [
            "report/EXECUTION_REPORT.md",
            "tables/TABLE_III_main_results.csv",
            "tables/wilcoxon_holm_pairwise.csv",
            "tables/ablation_results.csv",
            "tables/optimizer_stability.csv",
            "tables/synthetic_paired_results.csv",
            "manifest/run_manifest.json",
            "manifest/FROZEN_TEST_CONFIG.yaml",
            "raw/per_image_metrics.csv",
        ],
    }
    write_json(payload, output_root / "PAPER_RESULTS_PAYLOAD.json")

    if frozen_cfg["reporting"].get("package_results_zip", True):
        package_results(output_root, output_root / "PAPER_RESULTS_PACKAGE.zip")

    print("\nEXPERIMENT COMPLETE", flush=True)
    print(f"Report: {output_root / 'report' / 'EXECUTION_REPORT.html'}", flush=True)
    print(f"Payload: {output_root / 'PAPER_RESULTS_PAYLOAD.json'}", flush=True)
    print(f"Send-back ZIP: {output_root / 'PAPER_RESULTS_PACKAGE.zip'}", flush=True)
    return payload
