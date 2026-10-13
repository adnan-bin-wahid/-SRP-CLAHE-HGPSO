# Publishing Workflow After the Run

## Manuscript format and length

The current writing target is an IEEE-style two-column paper of at most
10 pages, including references, tables, and figures. Use the section budget
in [the writing plan](../paper/WRITING_PLAN.md) and the
[complete LaTeX draft](../paper/manuscript.tex). The selected venue's official
template and submission rules take precedence when preparing a submission.

The upload-ready archive is
`paper/SRP_CLAHE_HGPSO_IEEE_Overleaf.zip`; its entry point is `main.tex`.
See `paper/OVERLEAF_README.md` and the compiled package verification record.

## Evidence package

Archive:

- code ZIP / Git commit,
- dataset manifest,
- frozen config,
- environment manifest,
- per-image raw metrics,
- convergence data,
- statistical-test tables,
- generated figures.

## Manuscript sections to update from measured output

### Abstract

Only insert measured statements after the final run. Prefer effect/range language that is supported by the final table and statistics.

### Experimental Setup

Use `manifest/run_manifest.json` and `manifest/FROZEN_TEST_CONFIG.yaml` for hardware, software, image count, proxy budget, exact parameters and dataset adaptation.

### Results

Use:

- `TABLE_III_main_results.csv`
- `friedman_omnibus.csv`
- `wilcoxon_holm_pairwise.csv`
- `ablation_results.csv`
- `optimizer_stability.csv`
- `synthetic_paired_results.csv`

### Figures

Start with the generated plots, then re-render if the target journal requires specific dimensions/fonts.

### Baseline naming and attribution

Use method names in tables, legends, and panel headings: HE, CLAHE, AGCWD,
PSO, GWO, HGPSO, and Proposed SRP-HGPSO. The internal identifier
`Parent_HGPSO_Reproduction` remains in evidence files for traceability;
its publication label is `HGPSO`.

Cite each borrowed method and explain its implementation in the experimental
setup. State that HGPSO is an independent reproduction and document any
assumptions. Add the verified bibliographic reference to its table row or
caption when preparing the manuscript. Renaming a label does not remove the
need to acknowledge methodological dependence on earlier work.

Organize the results around visual enhancement, spectral preservation,
computational cost, component ablations, and robustness. Compare against the
full baseline set in the main table and trade-off plots. Discuss HGPSO as one
baseline, and identify the proposed method's contribution through its equations,
constraints, and ablation results.

### Discussion

Discuss quality-spectral-compute trade-offs. A method does not need to maximize every contrast metric if it gives substantially better spectral consistency and/or compute efficiency.

## Final checks before submission

Use `paper/RESEARCH_BRIEF.md` for the detailed section-by-section writing
specification, `paper/LITERATURE_NOTES.md` for source verification, and
`paper/evidence/README.md` for the retrospective evidence audit. The brief
qualifies the archived report's interpretations, including feasibility,
unequal budgets, statistical near ties, within-chip stability, and mixed
convergence histories. Use the audited main-test convergence asset when drafting.

- Replace all author placeholders.
- Verify all citations/DOIs.
- State Radiant Earth dataset DOI and license.
- Verify whether the target journal requires source-code/data availability statements.
- Ensure all test-set values are from the frozen run.
- Re-run a focused novelty search.
