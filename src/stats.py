from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon


METRIC_DIRECTIONS = {
    "entropy": 1,
    "local_rms_contrast": 1,
    "edge_density": 1,
    "laplacian_variance": 1,
    "ssim_to_input": 1,  # fidelity/change metric, not restoration accuracy on unpaired real scenes
    "ndvi_mae": -1,
    "ndwi_mae": -1,
    "sam_mean_deg": -1,
    "sam_p95_deg": -1,
    "clip_fraction": -1,
    "runtime_sec": -1,
    "peak_rss_mb": -1,
    "psnr_to_clean_db": 1,
    "ssim_to_clean": 1,
}


def summarize_by_method(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    rows = []
    for method, g in df.groupby("method"):
        row: dict[str, Any] = {"method": method, "n": int(g["chip_id"].nunique())}
        for m in metrics:
            if m not in g.columns:
                continue
            x = pd.to_numeric(g[m], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
            if x.size == 0:
                continue
            row[f"{m}_mean"] = float(np.mean(x))
            row[f"{m}_std"] = float(np.std(x, ddof=1)) if x.size > 1 else 0.0
            row[f"{m}_median"] = float(np.median(x))
            row[f"{m}_q1"] = float(np.percentile(x, 25))
            row[f"{m}_q3"] = float(np.percentile(x, 75))
        rows.append(row)
    return pd.DataFrame(rows)


def holm_adjust(pvalues: list[float]) -> list[float]:
    n = len(pvalues)
    if n == 0:
        return []
    order = np.argsort(pvalues)
    adjusted = np.empty(n, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (n - rank) * float(pvalues[idx]))
        running = max(running, val)
        adjusted[idx] = running
    return adjusted.tolist()


def rank_biserial_paired(diff_oriented: np.ndarray) -> float:
    d = np.asarray(diff_oriented, dtype=float)
    d = d[np.isfinite(d) & (d != 0)]
    if d.size == 0:
        return 0.0
    absd = np.abs(d)
    # Average ranks for ties.
    order = np.argsort(absd)
    ranks = np.empty_like(absd, dtype=float)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and np.isclose(absd[order[j]], absd[order[i]]):
            j += 1
        avg = (i + 1 + j) / 2.0
        ranks[order[i:j]] = avg
        i = j
    wpos = float(np.sum(ranks[d > 0]))
    wneg = float(np.sum(ranks[d < 0]))
    denom = wpos + wneg
    return 0.0 if denom == 0 else (wpos - wneg) / denom


def paired_statistics(
    df: pd.DataFrame,
    metrics: list[str],
    proposed: str = "SRP_CLAHE_HGPSO",
    alpha: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    omnibus_rows = []
    pair_rows = []

    methods = sorted(df["method"].dropna().unique())
    for metric in metrics:
        if metric not in df.columns:
            continue
        pivot = df.pivot_table(index="chip_id", columns="method", values=metric, aggfunc="first")
        available = [m for m in methods if m in pivot.columns]
        complete = pivot[available].replace([np.inf, -np.inf], np.nan).dropna()
        if len(available) >= 3 and len(complete) >= 3:
            try:
                stat, p = friedmanchisquare(*[complete[m].to_numpy() for m in available])
            except Exception:
                stat, p = np.nan, np.nan
            omnibus_rows.append({
                "metric": metric,
                "n": len(complete),
                "methods": len(available),
                "friedman_stat": float(stat),
                "p_value": float(p),
                "significant": bool(np.isfinite(p) and p < alpha),
            })

        if proposed not in pivot.columns:
            continue
        provisional = []
        for baseline in available:
            if baseline == proposed:
                continue
            pair = pivot[[proposed, baseline]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(pair) < 3:
                continue
            direction = METRIC_DIRECTIONS.get(metric, 1)
            d_raw = pair[proposed].to_numpy() - pair[baseline].to_numpy()
            d_oriented = d_raw * direction  # positive means proposed is better
            try:
                if np.allclose(d_oriented, 0):
                    stat, p = 0.0, 1.0
                else:
                    stat, p = wilcoxon(d_oriented, zero_method="wilcox", alternative="two-sided", mode="auto")
            except Exception:
                stat, p = np.nan, np.nan
            provisional.append({
                "metric": metric,
                "proposed": proposed,
                "baseline": baseline,
                "n": len(pair),
                "wilcoxon_stat": float(stat),
                "p_value": float(p),
                "rank_biserial": float(rank_biserial_paired(d_oriented)),
                "median_oriented_difference": float(np.median(d_oriented)),
            })

        valid_ps = [r["p_value"] for r in provisional if np.isfinite(r["p_value"])]
        adjusted = holm_adjust(valid_ps)
        j = 0
        for r in provisional:
            if np.isfinite(r["p_value"]):
                r["p_holm"] = float(adjusted[j]); j += 1
                r["significant_holm"] = bool(r["p_holm"] < alpha)
            else:
                r["p_holm"] = np.nan
                r["significant_holm"] = False
            pair_rows.append(r)

    return pd.DataFrame(omnibus_rows), pd.DataFrame(pair_rows)
