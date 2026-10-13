from __future__ import annotations

import html
import json
import math
import shutil
import zipfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from .stats import summarize_by_method
from .utils import write_json


MAIN_METRICS = [
    "entropy", "local_rms_contrast", "ssim_to_input", "ndvi_mae",
    "ndwi_mae", "sam_mean_deg", "clip_fraction", "runtime_sec",
]

METHOD_LABELS = {
    "Original": "Original",
    "HE": "HE",
    "CLAHE": "CLAHE",
    "AGCWD": "AGCWD",
    "CommonGain_CLAHE": "Common gain + CLAHE",
    "PSO_Transform": "PSO",
    "GWO_Transform": "GWO",
    "Parent_HGPSO_Reproduction": "HGPSO",
    "SRP_CLAHE_HGPSO": "Proposed SRP-HGPSO",
    "SRP_no_constraints": "SRP no constraints",
    "SRP_reduced_kp": "SRP reduced k,p",
}


def method_label(m: str) -> str:
    return METHOD_LABELS.get(m, m)


def save_rgb(path: str | Path, rgb: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(path)


def plot_metric_boxplots(df: pd.DataFrame, metrics: list[str], out_dir: str | Path) -> list[str]:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    methods = [m for m in df["method"].dropna().unique() if m != "Original"]
    for metric in metrics:
        if metric not in df.columns:
            continue
        arrays, labels = [], []
        for m in methods:
            x = pd.to_numeric(df.loc[df["method"] == m, metric], errors="coerce")
            x = x.replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
            if x.size:
                arrays.append(x); labels.append(method_label(m))
        if len(arrays) < 2:
            continue
        fig, ax = plt.subplots(figsize=(max(8, 1.2*len(arrays)), 5.5))
        # Matplotlib renamed the boxplot label argument from ``labels`` to
        # ``tick_labels``. Matplotlib 3.11 removed the old alias. Use the new
        # API first, with a fallback so the suite still works on 3.8-3.10.
        try:
            ax.boxplot(arrays, tick_labels=labels, showfliers=False)
        except TypeError:
            ax.boxplot(arrays, labels=labels, showfliers=False)
        ax.set_ylabel(metric)
        ax.set_title(f"Per-image distribution: {metric}")
        ax.tick_params(axis="x", rotation=35)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        p = out_dir / f"boxplot_{metric}.png"
        fig.savefig(p, dpi=180)
        plt.close(fig)
        paths.append(str(p))
    return paths


def plot_runtime_quality(df: pd.DataFrame, out_dir: str | Path) -> str | None:
    if not {"runtime_sec", "local_rms_contrast", "method"}.issubset(df.columns):
        return None
    g = df.groupby("method")[["runtime_sec", "local_rms_contrast"]].median(numeric_only=True).dropna()
    if g.empty:
        return None
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for method, row in g.iterrows():
        ax.scatter(row["runtime_sec"], row["local_rms_contrast"], s=55)
        ax.annotate(method_label(method), (row["runtime_sec"], row["local_rms_contrast"]), xytext=(5,4), textcoords="offset points", fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("Median runtime per image (s, log scale)")
    ax.set_ylabel("Median local RMS contrast")
    ax.set_title("Quality-cost trade-off")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out = Path(out_dir) / "quality_cost_tradeoff.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return str(out)


def plot_spectral_tradeoff(df: pd.DataFrame, out_dir: str | Path) -> str | None:
    req = {"ndvi_mae", "sam_mean_deg", "local_rms_contrast", "method"}
    if not req.issubset(df.columns):
        return None
    g = df.groupby("method")[["ndvi_mae", "sam_mean_deg", "local_rms_contrast"]].median(numeric_only=True).dropna()
    if g.empty:
        return None
    fig, ax = plt.subplots(figsize=(7.5,5.5))
    for method, row in g.iterrows():
        x = max(row["ndvi_mae"], 1e-12)
        y = row["local_rms_contrast"]
        size = 30 + 50 * min(row["sam_mean_deg"], 5)
        ax.scatter(x, y, s=size)
        ax.annotate(method_label(method), (x,y), xytext=(5,4), textcoords="offset points", fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("Median NDVI MAE (log scale; lower is better)")
    ax.set_ylabel("Median local RMS contrast (higher is better)")
    ax.set_title("Visual enhancement vs spectral-ratio error")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out = Path(out_dir) / "visual_spectral_tradeoff.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return str(out)


def plot_convergence(history_df: pd.DataFrame, out_dir: str | Path) -> str | None:
    if history_df.empty or "generation" not in history_df.columns:
        return None
    methods = [m for m in history_df["method"].unique() if m in {"PSO_Transform","GWO_Transform","Parent_HGPSO_Reproduction","SRP_CLAHE_HGPSO"}]
    if not methods:
        return None
    fig, ax = plt.subplots(figsize=(8,5.5))
    for method in methods:
        sub = history_df[history_df["method"] == method]
        piv = sub.pivot_table(index="generation", columns="chip_id", values="best_stable_utility", aggfunc="first")
        med = piv.median(axis=1, skipna=True)
        ax.plot(med.index, med.values, label=method_label(method))
    ax.set_xlabel("Generation")
    ax.set_ylabel("Median best stable visual utility")
    ax.set_title("Optimizer convergence on evaluated scenes")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out = Path(out_dir) / "convergence_median.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return str(out)


def make_qualitative_grid(root: str | Path, chip_ids: list[str], methods: list[str], out: str | Path) -> str | None:
    root, out = Path(root), Path(out)
    if not chip_ids or not methods:
        return None
    thumb = 220
    label_h = 34
    canvas = Image.new("RGB", (thumb * len(methods), (thumb + label_h) * len(chip_ids)), "white")
    draw = ImageDraw.Draw(canvas)
    for r, chip in enumerate(chip_ids):
        for c, method in enumerate(methods):
            p = root / chip / f"{method}.png"
            if not p.exists():
                continue
            im = Image.open(p).convert("RGB")
            im.thumbnail((thumb, thumb))
            x = c * thumb + (thumb - im.width)//2
            y0 = r * (thumb + label_h)
            canvas.paste(im, (x, y0 + label_h))
            label = method_label(method) if r == 0 else chip
            if r == 0:
                draw.text((c*thumb+5, y0+5), method_label(method), fill="black")
            if c == 0:
                draw.text((5, y0+label_h+5), chip, fill="white")
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)
    return str(out)


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df.empty:
        return "_No data available._"
    x = df if max_rows is None else df.head(max_rows)
    try:
        return x.to_markdown(index=False)
    except Exception:
        return "```\n" + x.to_string(index=False) + "\n```"


def _latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def _latex_table_fallback(df: pd.DataFrame, caption: str, label: str) -> str:
    """Dependency-free LaTeX fallback used if pandas Styler/Jinja2 is unavailable."""
    cols = list(df.columns)
    align = "l" + "r" * max(0, len(cols) - 1)
    lines = [
        r"\begin{table}[!t]",
        r"\centering",
        f"\\caption{{{_latex_escape(caption)}}}",
        f"\\label{{{_latex_escape(label)}}}",
        f"\\begin{{tabular}}{{{align}}}",
        r"\hline",
        " & ".join(_latex_escape(c) for c in cols) + r" \\ ",
        r"\hline",
    ]
    for _, row in df.iterrows():
        vals = []
        for value in row.tolist():
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(f"{float(value):.6g}")
            else:
                vals.append(_latex_escape(value))
        lines.append(" & ".join(vals) + r" \\ ")
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def write_latex_table(df: pd.DataFrame, path: str | Path, caption: str, label: str) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        path.write_text("% No data available\n", encoding="utf-8")
        return
    try:
        txt = df.to_latex(
            index=False,
            escape=True,
            float_format=lambda x: f"{x:.6g}",
            caption=caption,
            label=label,
        )
    except (ImportError, ModuleNotFoundError):
        # Pandas 2.x routes DataFrame.to_latex through Styler, which needs Jinja2.
        # The project now declares Jinja2 explicitly, but keep this fallback so
        # report generation cannot fail solely because that optional dependency
        # is absent or broken in a user environment.
        txt = _latex_table_fallback(df, caption, label)
    path.write_text(txt, encoding="utf-8")


def _format_main_table(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    rows = []
    for _, r in summary.iterrows():
        row = {"Method": method_label(str(r["method"])), "n": int(r.get("n",0))}
        for m in MAIN_METRICS:
            mean, std = r.get(f"{m}_mean"), r.get(f"{m}_std")
            if pd.notna(mean):
                if m in {"ndvi_mae","ndwi_mae","clip_fraction"}:
                    row[m] = f"{mean:.3e} ± {std:.2e}"
                elif m == "sam_mean_deg":
                    row[m] = f"{mean:.4f} ± {std:.4f}"
                else:
                    row[m] = f"{mean:.4f} ± {std:.4f}"
        rows.append(row)
    return pd.DataFrame(rows)


def build_execution_report(
    output_root: str | Path,
    run_info: dict[str, Any],
    main_df: pd.DataFrame,
    omnibus_df: pd.DataFrame,
    pairwise_df: pd.DataFrame,
    ablation_df: pd.DataFrame,
    stability_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    history_df: pd.DataFrame,
    warnings: list[str],
) -> dict[str, str]:
    output_root = Path(output_root)
    report_dir = output_root / "report"
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize_by_method(main_df, MAIN_METRICS)
    summary.to_csv(tables_dir / "main_results_summary.csv", index=False)
    main_table = _format_main_table(summary)
    main_table.to_csv(tables_dir / "TABLE_III_main_results.csv", index=False)
    write_latex_table(
        main_table, tables_dir / "TABLE_III_main_results.tex",
        "Test-set comparison (mean and standard deviation). HGPSO is an independent reproduction; implementation assumptions should be described in the experimental setup.",
        "tab:main_results",
    )

    if not omnibus_df.empty:
        omnibus_df.to_csv(tables_dir / "friedman_omnibus.csv", index=False)
    if not pairwise_df.empty:
        pairwise_df.to_csv(tables_dir / "wilcoxon_holm_pairwise.csv", index=False)
    if not ablation_df.empty:
        ablation_df.to_csv(tables_dir / "ablation_results.csv", index=False)
    if not stability_df.empty:
        stability_df.to_csv(tables_dir / "optimizer_stability.csv", index=False)
    if not synthetic_df.empty:
        synthetic_df.to_csv(tables_dir / "synthetic_paired_results.csv", index=False)

    pairwise_display = pairwise_df.replace({"proposed": METHOD_LABELS, "baseline": METHOD_LABELS})
    stability_display = stability_df.replace({"method": METHOD_LABELS})
    synthetic_display = synthetic_df.replace({"method": METHOD_LABELS})

    plot_metric_boxplots(main_df, ["entropy","local_rms_contrast","ndvi_mae","ndwi_mae","sam_mean_deg","runtime_sec"], figures_dir)
    plot_runtime_quality(main_df, figures_dir)
    plot_spectral_tradeoff(main_df, figures_dir)
    plot_convergence(history_df, figures_dir)

    # Hypothesis diagnostics are calculations, not publication claims by themselves.
    diagnostics: dict[str, Any] = {}
    pivot = main_df.pivot_table(index="chip_id", columns="method", values=["ndvi_mae","ndwi_mae","sam_mean_deg","runtime_sec","local_rms_contrast"], aggfunc="first")
    try:
        if "SRP_CLAHE_HGPSO" in pivot["ndvi_mae"] and "Parent_HGPSO_Reproduction" in pivot["ndvi_mae"]:
            p = pivot["ndvi_mae"][["SRP_CLAHE_HGPSO","Parent_HGPSO_Reproduction"]].dropna()
            ratio = np.median(p["Parent_HGPSO_Reproduction"] / np.maximum(p["SRP_CLAHE_HGPSO"], 1e-12))
            diagnostics["H1_ndvi_median_error_reduction_factor_vs_parent"] = float(ratio)
    except Exception:
        pass
    try:
        if "SRP_CLAHE_HGPSO" in pivot["runtime_sec"] and "Parent_HGPSO_Reproduction" in pivot["runtime_sec"]:
            p = pivot["runtime_sec"][["SRP_CLAHE_HGPSO","Parent_HGPSO_Reproduction"]].dropna()
            diagnostics["H2_parent_to_proposed_median_runtime_ratio"] = float(np.median(p["Parent_HGPSO_Reproduction"] / np.maximum(p["SRP_CLAHE_HGPSO"], 1e-9)))
    except Exception:
        pass
    write_json(diagnostics, report_dir / "hypothesis_diagnostics.json")

    warning_text = "\n".join(f"- {w}" for w in warnings) if warnings else "- No automatic protocol warning was triggered."
    md = f"""# SRP-CLAHE-HGPSO Execution Report

## Research-integrity status

This report contains **measured outputs from this run only**. It does not convert design targets into results. HGPSO is an independently implemented baseline with assumptions documented in `docs/METHOD_MAPPING.md`; cite the source method and describe these assumptions in the manuscript's experimental setup. PSNR/SSIM against a real degraded input are treated as fidelity/change measures, not restoration accuracy; restoration claims are reserved for the optional paired synthetic track.

## Run manifest

```json
{json.dumps(run_info, indent=2)}
```

## Automatic protocol warnings

{warning_text}

## Main same-data results

{dataframe_to_markdown(main_table)}

The columns `ssim_to_input` and any input-referenced PSNR/MSE quantify similarity/change relative to the real input. They are **not** clean-reference restoration metrics.

## Friedman omnibus tests

{dataframe_to_markdown(omnibus_df)}

## Proposed-vs-baseline Wilcoxon tests with Holm correction

{dataframe_to_markdown(pairwise_display)}

Effect-size orientation is normalized so positive rank-biserial values favor the proposed method according to the metric direction.

## Ablation results

{dataframe_to_markdown(ablation_df, 100)}

## Optimizer stability

{dataframe_to_markdown(stability_display, 100)}

## Paired synthetic stress-test results

{dataframe_to_markdown(synthetic_display, 100)}

The synthetic track is a controlled stress test with a known clean target; it is not presented as a complete physical atmospheric/sensor simulator.

## Hypothesis diagnostics

```json
{json.dumps(diagnostics, indent=2)}
```

## Files to use when writing the paper

- `tables/TABLE_III_main_results.csv` — primary same-data results table.
- `tables/friedman_omnibus.csv` — omnibus nonparametric tests.
- `tables/wilcoxon_holm_pairwise.csv` — corrected paired tests and rank-biserial effect sizes.
- `tables/ablation_results.csv` — parameter/component ablations.
- `tables/optimizer_stability.csv` — repeated-seed analysis.
- `tables/synthetic_paired_results.csv` — clean-reference auxiliary stress test.
- `figures/` — publication-draft plots generated from measured data.
- `raw/per_image_metrics.csv` — full per-image evidence; keep this archived.
- `manifest/run_manifest.json` — hardware/software/configuration audit.
- `PAPER_RESULTS_PAYLOAD.json` — compact machine-readable handoff for paper writing.

## Interpretation guardrails

1. A visually higher contrast result is not automatically better if spectral error or clipping increases substantially.
2. Exact normalized-ratio and spectral-angle invariance is analytical only before clipping/quantization and for valid denominators.
3. Shared gain preserves spectral direction/ratios but **not absolute radiometry**.
4. The Radiant Earth challenge chips are Sentinel-2 L2A four-band 512×512 products. Their expert cloud mask is used here instead of the SCL layer in the original draft; this dataset adaptation must be stated explicitly.
5. Do not copy cross-paper PSNR/SSIM numbers into the same-data comparison table.
6. Statistical significance should be reported together with effect size and the actual per-image distribution.
"""
    md_path = report_dir / "EXECUTION_REPORT.md"
    md_path.write_text(md, encoding="utf-8")

    # Simple self-contained HTML for convenient inspection.
    html_body = "<html><head><meta charset='utf-8'><style>body{font-family:Arial,sans-serif;max-width:1200px;margin:40px auto;line-height:1.45}table{border-collapse:collapse;font-size:12px}th,td{border:1px solid #ccc;padding:5px}code,pre{background:#f5f5f5;padding:4px;overflow:auto}</style></head><body>"
    html_body += "<h1>SRP-CLAHE-HGPSO Execution Report</h1>"
    html_body += "<p><b>Measured run output only.</b> Read EXECUTION_REPORT.md for interpretation guardrails.</p>"
    html_body += "<h2>Main results</h2>" + main_table.to_html(index=False, escape=True)
    html_body += "<h2>Friedman tests</h2>" + omnibus_df.to_html(index=False, escape=True) if not omnibus_df.empty else "<h2>Friedman tests</h2><p>No data.</p>"
    html_body += "<h2>Wilcoxon + Holm</h2>" + pairwise_display.to_html(index=False, escape=True) if not pairwise_display.empty else "<h2>Wilcoxon + Holm</h2><p>No data.</p>"
    html_body += "<h2>Warnings</h2><pre>" + html.escape(warning_text) + "</pre>"
    for img in sorted(figures_dir.glob("*.png")):
        html_body += f"<h3>{html.escape(img.stem)}</h3><img src='../figures/{img.name}' style='max-width:100%'>"
    html_body += "</body></html>"
    html_path = report_dir / "EXECUTION_REPORT.html"
    html_path.write_text(html_body, encoding="utf-8")

    return {"markdown": str(md_path), "html": str(html_path)}


def package_results(output_root: str | Path, zip_path: str | Path) -> str:
    output_root, zip_path = Path(output_root), Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.unlink(missing_ok=True)
    include_dirs = ["report", "tables", "figures", "manifest", "raw"]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for d in include_dirs:
            p = output_root / d
            if not p.exists():
                continue
            for f in p.rglob("*"):
                if f.is_file():
                    # Skip potentially huge enhanced rasters from raw packaging.
                    if f.suffix.lower() in {".tif", ".tiff", ".npz"}:
                        continue
                    z.write(f, f.relative_to(output_root))
        payload = output_root / "PAPER_RESULTS_PAYLOAD.json"
        if payload.exists():
            z.write(payload, payload.relative_to(output_root))
    return str(zip_path)
