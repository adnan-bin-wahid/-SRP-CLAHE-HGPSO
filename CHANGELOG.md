# Changelog

## v1.2
- Fixed Matplotlib 3.11+ report-generation compatibility: `Axes.boxplot()` now uses `tick_labels` with a backward-compatible fallback to `labels`.
- Added a regression test that generates report boxplots under the installed Matplotlib version.
- v1.1 Jinja2/LaTeX report fix retained.


## v1.1 — 2026-08-18
- Added the missing `Jinja2` runtime dependency required by pandas `DataFrame.to_latex()` on pandas 2.x.
- Added a dependency-free LaTeX-table fallback so report generation no longer fails solely because Jinja2 is absent or broken.
- Extended installation verification to check `jinja2` and `tabulate`.
- Verified the quick-check experiment through final report/package generation after the fix.

## 1.0.0 — 2026-08-17

- Full four-band SRP-CLAHE-HGPSO implementation.
- Feasibility-first spectral constraints.
- 256-proxy / 512-full benchmark adaptation.
- HE, CLAHE, AGCWD, PSO, GWO and parent-style HGPSO baselines.
- Validation-only configuration freeze.
- A1-A9 experimental/ablation support.
- Repeated-seed optimizer stability analysis.
- Paired synthetic clean-reference stress test.
- Friedman, Wilcoxon-Holm and rank-biserial statistics.
- Automatic publication-draft tables, figures, execution report and handoff ZIP.
- Resumable per-method caching.
