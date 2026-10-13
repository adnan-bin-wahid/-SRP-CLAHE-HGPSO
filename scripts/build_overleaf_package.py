from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RUN = ROOT / "results/standard_run"
PACKAGE = PAPER / "overleaf"
PROPOSED = "SRP_CLAHE_HGPSO"
METHODS = ["Original", "HE", "CLAHE", "AGCWD", "CommonGain_CLAHE", "PSO_Transform",
           "GWO_Transform", "Parent_HGPSO_Reproduction", PROPOSED]
LABELS = {"Original": "Original", "HE": "HE", "CLAHE": "CLAHE", "AGCWD": "AGCWD",
          "CommonGain_CLAHE": "Common-gain CLAHE", "PSO_Transform": "PSO", "GWO_Transform": "GWO",
          "Parent_HGPSO_Reproduction": "HGPSO", PROPOSED: "SRP-CLAHE-HGPSO"}


def mean_sd(row, metric, scale=1.0, digits=3):
    return f"${row[metric + '_mean'] * scale:.{digits}f} \\pm {row[metric + '_std'] * scale:.{digits}f}$"


def main_table(summary):
    parts = [r"\begin{table*}[t]", r"\centering\footnotesize",
             r"\caption{Test-set results (200 chips): mean $\pm$ sample standard deviation. Spectral errors are relative to the input. Clipping counts band samples; times are measured method stages, not end-to-end processing. RGB-only adapters leave NIR unchanged; common-gain CLAHE and SRP apply gain to all four bands.}",
             r"\label{tab:main}", r"\textit{(a) Display descriptors and measured cost}\par\smallskip",
             r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}", r"\toprule",
             r"Method & Entropy (bits) & Local RMS contrast & Input SSIM & Time (s) \\", r"\midrule"]
    for method in METHODS:
        row = summary.loc[method]
        values = [mean_sd(row, m) for m in ("entropy", "local_rms_contrast", "ssim_to_input", "runtime_sec")]
        parts.append(LABELS[method] + " & " + " & ".join(values) + r" \\")
    parts += [r"\bottomrule\end{tabular*}", r"\medskip\textit{(b) Spectral consistency and clipping}\par\smallskip",
              r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}", r"\toprule",
              r"Method & NDVI MAE ($10^{-3}$) & NDWI MAE ($10^{-3}$) & SAM (degrees) & Clipping (\%) \\", r"\midrule"]
    for method in METHODS:
        row = summary.loc[method]
        values = [mean_sd(row, "ndvi_mae", 1000, 4), mean_sd(row, "ndwi_mae", 1000, 4),
                  mean_sd(row, "sam_mean_deg", digits=4), mean_sd(row, "clip_fraction", 100, 4)]
        parts.append(LABELS[method] + " & " + " & ".join(values) + r" \\")
    parts += [r"\bottomrule\end{tabular*}", r"\end{table*}"]
    return "\n".join(parts) + "\n"


def ablation_table():
    df = pd.read_csv(RUN / "tables/ablation_results.csv").set_index("ablation")
    selected = [("A3_no_constraints", "Without constraints"),
                ("A4_gain_sigma_0.0", r"Smoothing $\sigma=0$"),
                ("A4_gain_sigma_1.0", r"Smoothing $\sigma=1$"),
                ("A4_gain_sigma_2.0", r"Smoothing $\sigma=2$"),
                ("A5_gain_0.4_2.5", r"Gain $[0.4,2.5]$"),
                ("A5_gain_0.5_2.0", r"Gain $[0.5,2.0]$"),
                ("A5_gain_0.7_1.5", r"Gain $[0.7,1.5]$"),
                ("A6_proxy_128", r"Proxy $128\times128$"),
                ("A6_proxy_256", r"Proxy $256\times256$"),
                ("A6_proxy_512", r"Proxy $512\times512$")]
    parts = [r"\begin{table}[t]\centering\footnotesize",
             r"\caption{Selected sensitivity runs: means over eight chips. Different seed tags across variants confound setting and search randomness; these are descriptive comparisons.}",
             r"\label{tab:ablation}", r"\begin{tabular}{@{}lrrr@{}}\toprule",
             r"Setting & Contrast & NDVI MAE & Time (s) \\\midrule"]
    for key, label in selected:
        row = df.loc[key]
        value = f"{row.ndvi_mae_mean:.2e}"
        mantissa, exponent = value.split("e")
        parts.append(f"{label} & {row.local_rms_contrast_mean:.4f} & ${mantissa}\\times10^{{{int(exponent)}}}$ & {row.runtime_sec_mean:.3f}" + r" \\")
    parts += [r"\bottomrule\end{tabular}\end{table}"]
    return "\n".join(parts) + "\n"


def science(value):
    if value >= 0.001:
        return f"${value:.4f}$"
    mantissa, exponent = f"{value:.2e}".split("e")
    return f"${mantissa}\\times10^{{{int(exponent)}}}$"


def statistics_table():
    df = pd.read_csv(PAPER / "evidence/pairwise_chip_audited.csv").set_index(["baseline", "metric"])
    selected = [("CommonGain_CLAHE", "local_rms_contrast", "CG", "Contrast"),
                ("CommonGain_CLAHE", "ssim_to_input", "CG", "Input SSIM"),
                ("CommonGain_CLAHE", "ndvi_mae", "CG", "NDVI MAE"),
                ("CommonGain_CLAHE", "ndwi_mae", "CG", "NDWI MAE"),
                ("CommonGain_CLAHE", "sam_mean_deg", "CG", "SAM"),
                ("CommonGain_CLAHE", "runtime_sec", "CG", "Time"),
                ("Parent_HGPSO_Reproduction", "local_rms_contrast", "HG", "Contrast"),
                ("Parent_HGPSO_Reproduction", "ndvi_mae", "HG", "NDVI MAE"),
                ("Parent_HGPSO_Reproduction", "ndwi_mae", "HG", "NDWI MAE"),
                ("Parent_HGPSO_Reproduction", "sam_mean_deg", "HG", "SAM"),
                ("Parent_HGPSO_Reproduction", "runtime_sec", "HG", "Time")]
    parts = [r"\begin{table}[t]\centering\footnotesize",
             r"\caption{Selected proposed-versus-control tests on 200 chips. CG: common-gain CLAHE; HG: HGPSO. Holm correction covers seven controls separately per metric. Positive oriented rank-biserial effect $r$ favors SRP.}",
             r"\label{tab:stats}\begin{tabular}{@{}llrr@{}}\toprule",
             r"Control & Metric & Adjusted $p$ & $r$ \\\midrule"]
    for baseline, metric, label, metric_label in selected:
        row = df.loc[(baseline, metric)]
        parts.append(f"{label} & {metric_label} & {science(row.p_holm)} & ${row.rank_biserial_exact_ties:+.3f}$" + r" \\")
    parts += [r"\bottomrule\end{tabular}\end{table}"]
    return "\n".join(parts) + "\n"


def synthetic_table():
    df = pd.read_csv(PAPER / "evidence/synthetic_summary_verified.csv").set_index("method")
    parts = [r"\begin{table}[t]\centering\footnotesize",
             r"\caption{Auxiliary synthetic results (12 chips): clean-reference scores, mean $\pm$ SD. Original denotes the degraded input with no enhancement.}",
             r"\label{tab:synthetic}\begin{tabular}{@{}lrr@{}}\toprule",
             r"Method & PSNR (dB) & SSIM \\\midrule"]
    for method in ("Original", "CLAHE", "Parent_HGPSO_Reproduction", PROPOSED):
        row = df.loc[method]
        label = "SRP (proposed)" if method == PROPOSED else LABELS[method]
        parts.append(label + " & " + mean_sd(row, "psnr_to_clean_db") + " & " + mean_sd(row, "ssim_to_clean") + r" \\")
    parts += [r"\bottomrule\end{tabular}\end{table}"]
    return "\n".join(parts) + "\n"


def figures(summary):
    output = PAPER / "figures"
    output.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8, "pdf.fonttype": 42})
    histories = pd.concat([pd.read_csv(path) for path in sorted((RUN / "raw/convergence/main").glob("*.csv"))])
    fig, ax = plt.subplots(figsize=(3.45, 2.30))
    for method in ("PSO_Transform", "GWO_Transform", "Parent_HGPSO_Reproduction", PROPOSED):
        group = histories[histories.method == method]
        pivot = group.pivot(index="generation", columns="chip_id", values="best_stable_utility").sort_index().ffill()
        assert pivot.shape[1] == 200 and not pivot.isna().any().any()
        label = "SRP (proposed)" if method == PROPOSED else LABELS[method]
        ax.plot(pivot.index, pivot.median(axis=1), label=label, linewidth=1.5)
    ax.set(xlabel="Generation", ylabel="Median best stable utility")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right")
    fig.tight_layout(pad=0.5)
    fig.savefig(output / "convergence.pdf")
    fig.savefig(output / "convergence.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.7))
    plotted = METHODS[1:]
    colors = ["#707070", "#3682b0", "#b35b34", "#167948", "#7c5192", "#ca9c1d", "#b54260", "#171717"]
    for index, (method, color) in enumerate(zip(plotted, colors), start=1):
        row = summary.loc[method]
        axes[0].scatter(row.sam_mean_deg_mean, row.local_rms_contrast_mean, color=color, s=36, marker="o")
        axes[1].scatter(row.runtime_sec_mean, row.local_rms_contrast_mean, color=color, s=36, marker="o")
        offsets = {5: (6, -12), 6: (6, 11), 7: (20, 1)}
        for panel, x in enumerate((row.sam_mean_deg_mean, row.runtime_sec_mean)):
            offset = offsets.get(index, (4, 4))
            if panel == 1:
                offset = {2: (-10, 10), 4: (8, -8), 5: (6, -8), 6: (4, 12), 7: (10, -5), 8: (-12, 10)}.get(index, offset)
            axes[panel].annotate(str(index), (x, row.local_rms_contrast_mean), xytext=offset,
                                 textcoords="offset points", fontsize=8,
                                 arrowprops={"arrowstyle": "-", "lw": 0.4, "color": color})
    axes[0].set(xlabel="Mean SAM (degrees, log scale)", ylabel="Mean local RMS contrast")
    axes[0].set_xscale("log")
    axes[1].set(xlabel="Mean method-stage time (s, log scale)")
    axes[1].set_xscale("log")
    axes[0].set_title("(a) Spectral-shape trade-off", fontsize=9)
    axes[1].set_title("(b) Measured cost trade-off", fontsize=9)
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.margins(x=0.18, y=0.16)
    fig.tight_layout(pad=0.6)
    fig.savefig(output / "tradeoffs.pdf")
    fig.savefig(output / "tradeoffs.png", dpi=200)
    plt.close(fig)

    available = sorted(path.name for path in (RUN / "artifacts/qualitative").iterdir() if path.is_dir())
    raw = pd.read_csv(RUN / "raw/per_image_metrics.csv")
    original = raw[(raw.method == "Original") & raw.chip_id.isin(available)].set_index("chip_id")
    low = original.sort_values(["local_rms_contrast", "chip_id"]).index[0]
    middle = original.sort_values(["local_rms_contrast", "chip_id"]).index[len(original) // 2]
    proposed = raw[(raw.method == PROPOSED) & raw.chip_id.isin(available)].set_index("chip_id")
    difficult = proposed.sort_values(["clip_fraction", "chip_id"], ascending=[False, True]).index[0]
    chips = list(dict.fromkeys([low, middle, difficult]))
    for chip in original.index:
        if len(chips) < 3 and chip not in chips:
            chips.append(chip)
    methods = ["Original", "CLAHE", "Parent_HGPSO_Reproduction", "CommonGain_CLAHE", PROPOSED]
    fig, axes = plt.subplots(3, 5, figsize=(7.1, 4.6))
    for r, chip in enumerate(chips):
        for c, method in enumerate(methods):
            axes[r, c].imshow(plt.imread(RUN / "artifacts/qualitative" / chip / f"{method}.png"))
            axes[r, c].set_xticks([])
            axes[r, c].set_yticks([])
            for spine in axes[r, c].spines.values():
                spine.set_visible(False)
            if r == 0:
                axes[r, c].set_title({"CommonGain_CLAHE": "Common-gain\nCLAHE", PROPOSED: "SRP\n(proposed)"}.get(method, LABELS[method]), fontsize=8)
            if c == 0:
                axes[r, c].set_ylabel(chip, fontsize=8)
    fig.subplots_adjust(left=0.035, right=0.999, bottom=0.005, top=0.9, hspace=0.06, wspace=0.03)
    fig.savefig(output / "qualitative.jpg", dpi=300)
    plt.close(fig)
    info = {"qualitative_available_chips": available, "qualitative_selected": chips,
            "selection_rule": "Among eight saved chips: lowest original contrast, upper-median original contrast, and greatest proposed clipping; ties resolved by chip ID.",
            "tradeoff_key": {str(index): LABELS[method] for index, method in enumerate(plotted, 1)}}
    (PAPER / "figure_provenance.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate manuscript assets and package an Overleaf upload.")
    parser.add_argument("--package-only", action="store_true", help="Package already rendered assets without changing them.")
    args = parser.parse_args()
    if not args.package_only:
        summary = pd.read_csv(PAPER / "evidence/main_summary_verified.csv").set_index("method")
        tables = PAPER / "tables"
        tables.mkdir(exist_ok=True)
        for name, content in {"main_results.tex": main_table(summary), "ablations.tex": ablation_table(),
                              "statistics.tex": statistics_table(), "synthetic.tex": synthetic_table()}.items():
            (tables / name).write_text(content, encoding="ascii")
        figures(summary)
    PACKAGE.mkdir(exist_ok=True)
    for source, target in [(PAPER / "manuscript.tex", PACKAGE / "main.tex"),
                           (PAPER / "manuscript.tex", PACKAGE / "manuscript.tex"),
                           (PAPER / "references.bib", PACKAGE / "references.bib"),
                           (PAPER / "OVERLEAF_README.md", PACKAGE / "README.md"),
                           (PAPER / "figure_provenance.json", PACKAGE / "figure_provenance.json")]:
        shutil.copy2(source, target)
    for name in ("RESEARCH_BRIEF.md", "LITERATURE_NOTES.md", "WRITING_PLAN.md"):
        shutil.copy2(PAPER / name, PACKAGE / name)
    for folder in ("figures", "tables"):
        destination = PACKAGE / folder
        destination.mkdir(exist_ok=True)
        for path in (PAPER / folder).iterdir():
            if path.suffix in {".pdf", ".jpg", ".tex"}:
                shutil.copy2(path, destination / path.name)
    evidence = PACKAGE / "evidence"
    evidence.mkdir(exist_ok=True)
    for path in (PAPER / "evidence").iterdir():
        if path.suffix in {".csv", ".pdf", ".png"}:
            shutil.copy2(path, evidence / path.name)
    for name in ("evidence_audit.json", "README.md"):
        shutil.copy2(PAPER / "evidence" / name, evidence / name)
    archive_inputs = evidence / "archived_run"
    archive_inputs.mkdir(exist_ok=True)
    source_inputs = json.loads((PAPER / "evidence/evidence_audit.json").read_text(encoding="utf-8"))["source_hashes_sha256"]
    for name, expected_hash in source_inputs.items():
        source = RUN / name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash, name
        target = archive_inputs / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for name in ("manuscript.pdf", "VERIFICATION.md", "verification.json"):
        if (PAPER / name).exists():
            shutil.copy2(PAPER / name, PACKAGE / name)
    tex = (PACKAGE / "main.tex").read_text(encoding="ascii")
    bib = (PACKAGE / "references.bib").read_text(encoding="ascii")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,]+)", bib))
    citations = {key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", tex) for key in group.split(",")}
    assert citations <= keys, citations - keys
    for target in re.findall(r"\\input\{([^}]+)\}", tex):
        assert (PACKAGE / (target if target.endswith(".tex") else target + ".tex")).exists(), target
    hashes = {str(path.relative_to(PACKAGE)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(PACKAGE.rglob("*")) if path.is_file() and path.name != "package_sha256.json" and path.suffix not in {".log", ".aux", ".out", ".bbl", ".blg"}}
    (PACKAGE / "package_sha256.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="ascii")
    archive = PAPER / "SRP_CLAHE_HGPSO_IEEE_Overleaf.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file() and path.suffix not in {".log", ".aux", ".out", ".bbl", ".blg"}:
                bundle.write(path, str(path.relative_to(PACKAGE)))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    print(f"Overleaf ZIP: {archive}")
    print(f"Citations: {len(citations)}; figure selection: {(PAPER / 'figure_provenance.json').read_text()}")


if __name__ == "__main__":
    main()
