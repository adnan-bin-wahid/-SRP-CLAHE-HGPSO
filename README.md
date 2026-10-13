# SRP-CLAHE-HGPSO

Paper experiment suite and evidence-grounded IEEE-style manuscript.

## Completed Paper

- [Nine-page manuscript PDF](paper/manuscript.pdf)
- [Overleaf upload ZIP](paper/SRP_CLAHE_HGPSO_IEEE_Overleaf.zip)
- [LaTeX manuscript](paper/manuscript.tex)
- [Build verification](paper/VERIFICATION.md)
- [Completed standard-run results](results/standard_run/)

Upload the ZIP as a new Overleaf project, select `main.tex`, and use
`pdfLaTeX`. The repository contains code, tests, saved experiment outputs,
paper evidence, figures, tables, and bibliography. Local environments,
temporary build files, and the downloaded compiler are excluded. The full
Sentinel-2 source dataset is not bundled; see the dataset instructions below.

Repository: https://github.com/adnan-bin-wahid/-SRP-CLAHE-HGPSO

> **Version 1.1 (2026-08-18):** fixes the pandas/Jinja2 LaTeX-report dependency found during a Windows quick-check. The numerical experiment was already completing; the failure occurred only during final report generation. v1.2 adds Jinja2 and a fallback LaTeX writer.


Complete CPU-only experimental codebase for the manuscript:

**Spectral-Ratio-Preserving Satellite Image Enhancement Using CLAHE and Budget-Aware Hybrid Grey Wolf–Particle Swarm Optimization**

This repository is designed to take the automatically created `SRP_Sentinel2_Final_240` dataset folder and produce the **raw measurements, tables, statistical tests, ablations, figures, environment manifest, and a compact results package** needed to finish the empirical paper.

## Research-integrity boundary

This software does **not** fabricate results. Every table and plot in `results/` is generated from measured execution. The parent HGPSO code is an independent reproduction because the source study does not publish every implementation detail required for exact source-level reproduction. The code records those assumptions instead of presenting them as author-supplied implementation details.

The real Sentinel-2 experiment has no pristine clean target. Therefore `SSIM_to_input`, `PSNR_to_input`, and `MSE_to_input` are explicitly treated as **fidelity/change measures**, not restoration-accuracy measures. A separate optional synthetic paired stress test provides a known clean reference for legitimate clean-target PSNR/SSIM.

---

## 1. Expected dataset

Use the ZIP created by the companion dataset builder and extract it. The root must look like:

```text
SRP_Sentinel2_Final_240/
├── dataset_manifest.csv
├── validation/
│   ├── <chip_id>/
│   │   ├── B02.tif
│   │   ├── B03.tif
│   │   ├── B04.tif
│   │   ├── B08.tif
│   │   └── cloud_mask.tif
│   └── ...
└── test/
    ├── <chip_id>/
    │   ├── B02.tif
    │   ├── B03.tif
    │   ├── B04.tif
    │   ├── B08.tif
    │   └── cloud_mask.tif
    └── ...
```

The Radiant Earth challenge chips are 512×512, 10 m, co-registered Sentinel-2 L2A B02/B03/B04/B08 data. This project uses the supplied expert cloud mask instead of the SCL layer originally proposed in the draft. That dataset adaptation is automatically recorded in the run report.

---

## 2. First: verify the codebase

On Windows, double-click:

```text
RUN_FIRST_CHECK.bat
```

This creates `.venv`, installs dependencies, creates a tiny synthetic multispectral dataset, and runs a small end-to-end experiment.

Expected final message:

```text
QUICK CHECK PASSED
```

Open:

```text
results\quick_check\report\EXECUTION_REPORT.html
```

Do this **before** starting the real 240-image experiment.

---

## 3. Validate your real dataset

PowerShell / Command Prompt:

```powershell
.\.venv\Scripts\activate
python scripts\validate_dataset.py --dataset "E:\path\SRP_Sentinel2_Final_240"
```

Expected:

```text
Dataset validation PASSED
```

The validator checks band existence, shape alignment, CRS/transform consistency, cloud mask shape, usable clear-pixel fraction, split structure, and available manifest metadata.

---

## 4. Recommended experiment order

### A. Standard end-to-end run first

Use this to make sure the complete workflow works on the real data before committing to the long paper run:

```text
RUN_STANDARD_EXPERIMENT.bat "E:\path\SRP_Sentinel2_Final_240"
```

or:

```powershell
python scripts\run_full_experiment.py `
  --dataset "E:\path\SRP_Sentinel2_Final_240" `
  --output "results\standard_run" `
  --preset standard
```

### B. Practical final-paper run

```text
RUN_PAPER_PRACTICAL.bat "E:\path\SRP_Sentinel2_Final_240"
```

This uses the manuscript's proposed 16×50 SRP budget, a 256×256 proxy for the 512×512 dataset chips, 10 full-resolution elite checks, and a moderate repeated-seed/ablation protocol.

### C. Strict parent-budget paper run

```text
RUN_PAPER_FULL.bat "E:\path\SRP_Sentinel2_Final_240"
```

`paper_full` uses the parent-style 30×100 budget for PSO/GWO/parent HGPSO, plus 25-image × 10-seed stability analysis. **This can take many hours or days on a CPU.** The run is resumable.

---

## 5. Why the proposed proxy is 256×256 here

The manuscript draft discussed a 512×512 proxy for 1024×1024 images. The selected Radiant Earth benchmark chips are already 512×512. To preserve the same half-linear / quarter-pixel proxy principle, this suite uses:

```text
512×512 full chip → 256×256 optimization proxy → full-resolution elite verification
```

The 128/256/512 proxy ablation is generated automatically. This adaptation must be described in the final experimental section.

---

## 6. Methods automatically compared

Same-image test-set benchmark:

```text
Original
HE
CLAHE
AGCWD
CommonGain_CLAHE
PSO_Transform
GWO_Transform
Parent_HGPSO_Reproduction
SRP_CLAHE_HGPSO
```

Interpretation:

- HE / CLAHE / AGCWD: RGB-visible enhancement; NIR is unchanged.
- Parent/PSO/GWO: visual-channel transform applied to visible bands; NIR remains unchanged.
- CommonGain_CLAHE: isolates the four-band common-gain projection without HGPSO.
- SRP-CLAHE-HGPSO: full proposed shared-gain, feasibility-first method.

---

## 7. Metrics automatically generated

### Visual/information

- entropy
- local RMS contrast
- Canny edge density
- Laplacian variance
- mean brightness

### Input-fidelity/change

- SSIM to input
- MSE to input
- PSNR to input

These are **not called restoration accuracy** on real unpaired data.

### Spectral consistency

- NDVI MAE / RMSE / correlation
- NDVI sign-flip fraction
- NDWI MAE / RMSE / correlation
- NDWI sign-flip fraction
- mean / median / 95th-percentile SAM
- clipped-valid-pixel fraction

### Efficiency

- wall-clock runtime per image
- sampled process peak RSS memory
- proxy evaluations
- full-resolution elite evaluations
- iteration count
- early-stop status
- pixel-equivalent evaluation workload

---

## 8. Automatic validation-only configuration freeze

Before touching the frozen test set, the runner uses a small representative subset of `validation/` to evaluate:

```text
local window: 7, 15, 31
gain sigma:   0, 1, 2
gain max:     1.5, 2.0, 2.5
```

The selection uses a small fixed calibration search budget and then writes:

```text
manifest/FROZEN_TEST_CONFIG.yaml
```

No test-set parameter is fed back into the configuration.

The median validation best `a,b,c` values are also stored for the reduced-dimensional `k,p` ablation.

---

## 9. Automatic ablations

The suite implements the manuscript's planned components as far as the chosen 512×512 benchmark permits:

- A1 RGB-only parent reconstruction vs shared four-band gain — already represented in the main benchmark.
- A2 common gain without optimizer vs proposed — already represented in the main benchmark.
- A3 no spectral feasibility constraints.
- A4 gain smoothing σ = 0, 0.5, 1, 2.
- A5 gain-bound sensitivity.
- A6 proxy resolution 128, 256, 512.
- A7 search budget 8×20, 12×30, 16×50, 30×100.
- A8 five-parameter vs reduced `k,p` search with validation-frozen `a,b,c`.
- A9 objective-weight perturbations.

Ablations are run on a deterministic representative test subset and are kept separate from validation selection.

---

## 10. Statistical analysis

For each primary metric the software creates:

1. Friedman omnibus test across methods.
2. Paired Wilcoxon signed-rank test: proposed vs each baseline.
3. Holm correction for multiple pairwise tests.
4. Paired rank-biserial effect size.
5. Mean ± standard deviation and median/IQR summaries.

The held-out image/chip is the paired statistical unit. Random optimizer seeds are analyzed separately so repeated seeds are not treated as independent dataset samples.

---

## 11. Optimizer stability experiment

The stability stage runs independent seeds on a fixed representative subset and reports dispersion/CV for the parent reproduction and the proposed method.

The strict `paper_full` preset uses:

```text
25 images × 10 seeds × 2 methods
```

The practical preset is smaller.

---

## 12. Paired synthetic stress test

A controlled `mixed` degradation is generated from a subset of clean benchmark chips. Because the undegraded chip is retained as a target, this auxiliary experiment can legitimately report:

```text
PSNR_to_clean
SSIM_to_clean
```

It is explicitly labeled a **synthetic computational stress test**, not a complete physical atmosphere/sensor model.

---

## 13. Final output

A complete run creates:

```text
results/paper_full/
├── PAPER_RESULTS_PAYLOAD.json
├── PAPER_RESULTS_PACKAGE.zip       <-- send this back to ChatGPT
├── manifest/
│   ├── run_manifest.json
│   ├── starting_config.yaml
│   ├── FROZEN_TEST_CONFIG.yaml
│   ├── dataset_validation.csv
│   └── reduced_search_fixed_abc.json
├── raw/
│   ├── per_image_metrics.csv
│   ├── ablation_per_image.csv
│   ├── stability_per_run.csv
│   ├── synthetic_paired_per_image.csv
│   ├── convergence/
│   └── method_results/
├── tables/
│   ├── TABLE_III_main_results.csv
│   ├── TABLE_III_main_results.tex
│   ├── friedman_omnibus.csv
│   ├── wilcoxon_holm_pairwise.csv
│   ├── ablation_results.csv
│   ├── optimizer_stability.csv
│   └── synthetic_paired_results.csv
├── figures/
│   ├── qualitative_comparison_grid.jpg
│   ├── visual_spectral_tradeoff.png
│   ├── quality_cost_tradeoff.png
│   ├── convergence_median.png
│   └── boxplot_*.png
└── report/
    ├── EXECUTION_REPORT.html
    ├── EXECUTION_REPORT.md
    └── hypothesis_diagnostics.json
```

### What to send back after the experiment

The easiest file is:

```text
PAPER_RESULTS_PACKAGE.zip
```

If upload size is an issue, send:

```text
PAPER_RESULTS_PAYLOAD.json
report/EXECUTION_REPORT.md
tables/TABLE_III_main_results.csv
tables/wilcoxon_holm_pairwise.csv
```

With those measured outputs, the empirical Results, Discussion, Abstract, Conclusion, and final tables can be written without inventing values.

---

## 14. Resume behavior

Every image/method result is cached under:

```text
raw/method_results/
```

If the PC is stopped, power fails, or an experiment throws an error, run the same command again. Completed method results are reused. Use `--force` only when you intentionally changed implementation/configuration and need to invalidate cached main results.

---

## 15. Important limitations to preserve in the paper

- Shared gain preserves normalized ratios and spectral direction before clipping, but not absolute radiometry.
- Nonzero spectral error can arise from clipping and numerical precision.
- The parent HGPSO is an independent reproduction, not the authors' source code.
- The Radiant Earth benchmark uses an expert cloud mask rather than Sentinel-2 SCL in this project-specific subset.
- The chosen four-band dataset cannot establish preservation of every possible multispectral feature.
- A final novelty/literature search is still required immediately before submission.

See `docs/` before manuscript submission.


## v1.2 compatibility note
This release is tested with the newer Matplotlib boxplot API (`tick_labels`) and keeps a fallback for older Matplotlib releases.
