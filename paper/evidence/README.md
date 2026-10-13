# Derived Evidence Audit

These files are derived from the completed `results/standard_run` archive. They do not replace its raw experiment records. This is a retrospective evidence check and sensitivity analysis, not a new enhancement experiment or a preregistered statistical protocol.

## Reproduce

Run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\analyze_paper_evidence.py
```

Alternatively use an environment with the project's installed dependencies. The script uses Matplotlib's noninteractive Agg backend. Output defaults to `paper/evidence`; an output directory inside the archived run is rejected. Files in this derived directory are overwritten on rerun.

## Inventory

| File | Meaning |
| --- | --- |
| `evidence_audit.json` | Source SHA256 hashes, sample counts, completeness checks, feasibility, ratio-of-means comparisons, statistical differences, convergence coverage |
| `main_summary_verified.csv` | Recomputed means/SDs/medians, checked against the archived summary |
| `pairwise_chip_audited.csv` | Paired Wilcoxon tests and direction-oriented rank-biserial effects using exact-equality ties; seven comparisons corrected separately for each metric |
| `statistical_implementation_audit.csv` | Comparison with archived p-values and effects; near-tie ranking changes no significance decisions |
| `dataset_group_inventory.csv` | Split/location/acquisition-time groups and validity summaries |
| `group_mean_metrics.csv` | Equal-weight group-level inputs after within-group averaging |
| `pairwise_group_sensitivity.csv` | Exploratory paired comparisons of the 50 test metadata-group means |
| `infeasible_test_chips.csv` | Ten proposed test outputs exceeding the clipped-band-sample constraint |
| `cost_summary.csv` | Runtime, proxy/full evaluation, iteration, and pixel-equivalent workload summaries |
| `main_methods_on_ablation_subset.csv` | Main-run summaries restricted to the same eight ablation chips; not newly rerun seed-matched controls |
| `stability_within_chip.csv` | Per-method/per-chip variation across three seeds, separating within-chip from between-scene variation |
| `synthetic_summary_verified.csv` | Reference-based PSNR/SSIM summaries for the 12-chip synthetic experiment |
| `convergence_main_test.png`, `.pdf` | Main-test-only median best stable-utility curves, with early-stopped values carried forward to each method's observed horizon |

Some CSVs have multilevel headers from grouped aggregation. Read `cost_summary.csv` and `stability_within_chip.csv` with `header=[0,1]` when appropriate rather than treating the second header row as an observation.

## Interpretation Rules

- Raw method IDs retain `Parent_HGPSO_Reproduction` for traceability. Display it as `HGPSO` with one clear attribution/independent-reproduction statement in the paper.
- The primary unit is the chip, with 200 complete pairs. Metadata grouping is a sensitivity analysis, not verification of geographic independence.
- Positive oriented effect favors the proposed method, including for lower-is-better metrics. Non-significance does not prove equivalence.
- The clipping statistic counts valid **band samples**, not unique clipped pixels. Joint feasibility is 190/200.
- Runtime is the measured method stage, excluding loading/context preparation and including candidate metrics. Budgets differ across optimizers.
- The convergence audit uses only `raw/convergence/main`. The archived report generator collects histories recursively and can mix other experiment namespaces. Use these audited assets in the manuscript.
- Carry-forward represents an unchanged best score after stopping. Proposed and baseline horizons differ, and generations are not equal cost.
- Source hashes are verified unchanged at the end of the audit. Hash coverage is the input files named in the JSON, not a claim that every repository file or generated plot is cryptographically inventoried.

The writing interpretation is in [RESEARCH_BRIEF.md](../RESEARCH_BRIEF.md).
