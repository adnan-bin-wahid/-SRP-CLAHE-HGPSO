from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .io import find_dataset_splits, load_manifest, manifest_lookup, load_scene


def validate_dataset(dataset_root: str | Path, cfg: dict[str, Any]) -> tuple[pd.DataFrame, list[str]]:
    root = Path(dataset_root)
    splits = find_dataset_splits(root)
    manifest = load_manifest(root)
    lookup = manifest_lookup(manifest)
    rows = []
    warnings = []

    for split, dirs in splits.items():
        for d in dirs:
            row = lookup.get(d.name, {})
            try:
                scene = load_scene(
                    d,
                    split,
                    reflectance_scale=cfg["project"]["reflectance_scale"],
                    cloud_mask_name=cfg["input"]["cloud_mask_name"],
                    cloud_values=cfg["input"]["cloud_values"],
                    min_valid_fraction=cfg["input"]["min_valid_fraction"],
                    manifest_row=row,
                )
                rows.append({
                    "chip_id": scene.chip_id,
                    "split": split,
                    "height": scene.height,
                    "width": scene.width,
                    "valid_fraction": float(scene.valid_mask.mean()),
                    "cloud_fraction": scene.cloud_fraction,
                    "scale_used": scene.scale_used,
                    "location": scene.location,
                    "datetime": scene.datetime,
                    "status": "OK",
                    "error": "",
                })
            except Exception as e:
                rows.append({
                    "chip_id": d.name,
                    "split": split,
                    "status": "ERROR",
                    "error": str(e),
                })

    df = pd.DataFrame(rows)
    if not df.empty:
        ok = df[df["status"] == "OK"]
        if "validation" not in set(ok["split"]) or "test" not in set(ok["split"]):
            warnings.append("Both validation and test splits are required for the full paper protocol.")
        if not manifest.empty and "location" in manifest.columns and "split" in manifest.columns:
            vloc = set(manifest.loc[manifest["split"] == "validation", "location"].astype(str))
            tloc = set(manifest.loc[manifest["split"] == "test", "location"].astype(str))
            overlap = sorted(vloc & tloc)
            if overlap:
                warnings.append(f"Validation/test location overlap detected: {overlap[:10]}")
        shapes = ok[["height", "width"]].drop_duplicates() if {"height","width"}.issubset(ok.columns) else pd.DataFrame()
        if len(shapes) > 1:
            warnings.append("Multiple raster shapes detected; proxy workload comparisons must use actual pixel counts.")
    return df, warnings


def choose_representative_ids(df: pd.DataFrame, split: str, n: int, seed: int = 0) -> list[str]:
    sub = df[(df["status"] == "OK") & (df["split"] == split)].copy()
    if len(sub) <= n:
        return sub["chip_id"].astype(str).tolist()
    # Deterministic spread by valid/cloud fractions if available; otherwise evenly spaced.
    if "cloud_fraction" in sub.columns:
        sub["cloud_fraction"] = pd.to_numeric(sub["cloud_fraction"], errors="coerce").fillna(0)
        sub["valid_fraction"] = pd.to_numeric(sub["valid_fraction"], errors="coerce").fillna(1)
        sub = sub.sort_values(["cloud_fraction", "valid_fraction", "chip_id"])
    idx = np.linspace(0, len(sub) - 1, n).round().astype(int)
    return sub.iloc[idx]["chip_id"].astype(str).tolist()
