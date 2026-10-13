# IEEE-Style Paper: Overleaf Package

## Upload and Build

Upload SRP_CLAHE_HGPSO_IEEE_Overleaf.zip as a new Overleaf project.
Select **main.tex** as the main document and **pdfLaTeX** as the compiler.
Overleaf runs the required BibTeX steps automatically. Recompile from scratch
if citations initially appear unresolved.

The package uses the standard IEEEtran conference class with two columns.
Four side-by-side author blocks each display the author's name, institute,
university, location, and individual email on the first page.
All figures, bibliography entries, and generated tables are local to the
package; no absolute paths or shell-escape features are required.
The supplied local PDF is 9 pages including references and floats, within
the requested 10-page cap. See VERIFICATION.md for the build checks and
compiler details; the remote Overleaf build has not been executed.

For a conventional local TeX Live/MiKTeX build:

~~~text
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
~~~

## Authors

The supplied author order is retained:

1. Sumaiya Farhana Islam, bsse1450@iit.du.ac.bd
2. Adnan Bin Wahid, bsse1442@iit.du.ac.bd
3. Redowan Billah Sami, bsse1409@iit.du.ac.bd
4. Md. Touhidur Rahman, bsse1432@iit.du.ac.bd

All authors: Institute of Information Technology, University of Dhaka,
Dhaka, Bangladesh. No corresponding-author designation, author contribution,
funding award, or ethical approval has been invented.

## Contents and Provenance

- main.tex: complete manuscript.
- references.bib: cited references, including the credited HGPSO source.
- figures/: original pipeline source, saved-output qualitative selection,
  main-test-only convergence, and arithmetic-mean trade-off plots.
- tables/: LaTeX tables generated from the audited saved results.
- evidence/: derived CSVs, audit metadata, and hash-checked archived input
  metrics/manifests for checking the numbers without the original machine.
- figure_provenance.json: deterministic saved-chip selection rule and IDs.
- package_sha256.json: packaged-file integrity inventory.

Main result data originate exclusively from the completed standard run.
No enhancement experiments were rerun to create the manuscript. The primary
comparison is with common-gain CLAHE; unequal budgets, 10 clipping failures,
lower input SSIM, and negative synthetic restoration findings are reported.
Tables show rounded summaries; evidence CSVs retain precision.

## Before Submission

This is a complete evidence-grounded draft, not a guarantee of acceptance.
Select the exact venue's official template and check its page/disclosure policy.
All authors must review the text, citations, author details, and claims.
Resolve bibliography verification flags described in the project's
LITERATURE_NOTES.md, especially final publisher/source metadata.
Confirm dataset attribution and a real public code/evidence archive if required.
No public repository release is falsely claimed in the manuscript.

Evidence manifests preserve the original run's local paths for provenance;
those paths are not used by LaTeX or needed to compile the paper.

Keep the raw experiment archive and study limitations intact. Changing a
fallback, optimizer, or budget requires new experiments rather than relabeling
the present results.
