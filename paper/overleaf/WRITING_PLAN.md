# IEEE Two-Column Paper Plan

The detailed section-by-section specification is in
[RESEARCH_BRIEF.md](RESEARCH_BRIEF.md), supported by
[LITERATURE_NOTES.md](LITERATURE_NOTES.md) and the reproducible
[derived evidence audit](evidence/README.md). These are preparation materials,
not a finished manuscript or new enhancement experiments.

## Agreed scope

- Maximum length: 10 pages in the compiled PDF, including references, figures,
  tables, and any appendix included in that PDF.
- Layout: two columns on each page, with a full-width title and selected
  full-width figures or tables where necessary.
- Initial layout: IEEEtran journal mode, pending selection of a target venue.
  Replace this with the venue's official template before submission.
- Evidence source: the completed `results/standard_run` experiment.
- Working target: 9.5 pages, leaving 0.5 page for layout adjustments.

Two-column layout means two text columns per page; it does not require
double-sided printing. The 10-page cap is this project's writing requirement,
not a universal IEEE page limit.

## Page budget

These allocations include the space occupied by equations, tables, figures,
captions, and headings within each section. They are approximate, not mandatory
page breaks.

| Content | Pages | Main purpose |
| --- | ---: | --- |
| Title, authors, abstract, index terms | 0.75 | Summarize the question, approach, and measured findings |
| I. Introduction | 1.00 | Motivation, research gap, objective, and supported contributions |
| II. Related Work | 0.75 | Position the method among enhancement and spectral-preservation approaches |
| III. Proposed Method | 2.00 | Equations, preservation argument, constraints, optimizer, and pseudocode |
| IV. Experimental Setup | 1.25 | Dataset, splits, preprocessing, baselines, budgets, metrics, and statistics |
| V. Results | 2.00 | Main comparisons, qualitative evidence, ablations, convergence, and stability |
| VI. Discussion and Limitations | 0.50 | Interpret trade-offs and identify practical limits |
| VII. Conclusion and availability statement | 0.25 | Answer the objective and provide access information |
| References and acknowledgments | 1.00 | Verified sources and any required acknowledgments |
| Working total | 9.50 | Reserve 0.50 page for final layout |

## Tables and figures

Target four tables and four figures initially; change the count if evidence or
readability requires it. These counts are editorial choices, not IEEE rules.

| Item | Planned content |
| --- | --- |
| Table I | Dataset, preprocessing, implementation, and optimizer settings |
| Table II | All-method test-set comparison: visual, spectral, and runtime metrics |
| Table III | Component ablations |
| Table IV | Selected corrected statistical comparisons and repeated-seed stability, using separate panels if needed |
| Fig. 1 | Proposed processing pipeline |
| Fig. 2 | Representative qualitative comparison with identical display bounds |
| Fig. 3 | Visual-spectral and quality-cost trade-offs as two panels |
| Fig. 4 | Optimizer convergence |

The existing qualitative grid contains many scenes. Select a compact subset
using a documented rule, and retain the complete grid as supplementary evidence.
Do not select scenes solely because they favor the proposed method.

Reformat the generated main table rather than shrinking its current wide layout
until the text becomes unreadable. Split visual and spectral metrics into panels
if necessary. Use `table*` and `figure*` for content spanning both columns.
Keep extra boxplots, full per-image metrics, complete statistical tables, and
detailed synthetic results in supplementary material when the venue permits it.
Summarize any synthetic experiment discussed in the main text accurately.

## Content requirements

- Explain inherited method components with citations. Use HGPSO as the display
  name and disclose its independent reproduction and implementation assumptions.
- Explain the shared gain applied to all four bands, including preservation
  assumptions and the effects of clipping and quantization.
- Document generation-normalized visual scores and the stable utility used for
  cross-generation optimizer bookkeeping.
- Report actual validation selection, frozen settings, test selection,
  evaluation budgets, hardware, and statistical procedures.
- Treat SSIM/PSNR to input as input fidelity measures. Restrict clean-reference
  restoration claims to the auxiliary paired synthetic experiment.
- Report non-significant findings along with significant findings. Do not
  claim superiority on every quality metric.
- Report 190/200 joint constraint compliance, including the ten clipping
  failures. The clipping measure counts valid band samples, not unique pixels.
- Make common-gain CLAHE the closest architectural control. Disclose unequal
  search budgets and method-stage timing boundaries in HGPSO cost comparisons.
- Use `evidence/convergence_main_test.pdf` for main-test convergence; the
  archived report generator can mix histories from other experiment namespaces.
- Treat ablations as small-subset descriptive evidence, quantify seed variation
  within chips, and report the negative synthetic clean-reference results.
- Explain that spectral-ratio preservation does not preserve absolute radiometry.
- Verify references, dataset license, author information, and availability links.

## Layout and length verification

Use the official class defaults for fonts, margins, and column spacing. Edit
repetition and move secondary evidence to permitted supplements to meet the
page cap. Do not force sections onto particular pages or compress spacing.

`manuscript.tex` now contains the complete evidence-grounded draft with the
four supplied authors. The upload-ready entry point is `overleaf/main.tex`.
It requires a LaTeX distribution with IEEEtran. From this directory, a typical
build command is `latexmk -pdf manuscript.tex`. Once the full text and references
are present, inspect the compiled PDF for page count, column overflow, readable
labels, float placement, and complete citations. Revise until it is at most
10 pages. The package verification record reports the actual compiled count;
the page budget alone is not a layout guarantee.

Official guidance:

- Templates: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/
- Article structure: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/

