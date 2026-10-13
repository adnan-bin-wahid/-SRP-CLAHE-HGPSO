# Manuscript Verification

Verified on October 13, 2026.

## Build and Layout

- The complete manuscript compiles to **9 pages**, including references,
  figures, and tables, using the standard two-column IEEEtran conference class.
- Local compilation used Tectonic 0.17.0 (XeTeX). A remote Overleaf build
  and a local pdfLaTeX build were not executed. The recommended Overleaf
  configuration is main.tex with pdfLaTeX.
- All four supplied author names and emails appear on the first page.
  Four side-by-side conference-style author blocks each display the institute,
  university, location, and individual email beneath the author's name.
  Their alignment, order, and nonoverlapping name/email bounds are checked.
- All 17 bibliography entries are cited; the build has no unresolved
  citations/references or horizontal overfull boxes.
- All fonts are embedded. No replacement glyphs or words outside page
  boundaries were found. Rendered pages were inspected for readability.
- Nonfatal warnings include underfull boxes, legacy algorithm-package
  comment encoding, and the portable compiler's Fontconfig configuration.
  These are not missing-font or unresolved-reference errors.

## Evidence and Tests

- Ten automated tests passed for the project and paper-evidence helpers.
- The completed standard-run evidence was used without rerunning enhancement
  experiments. Archived input hashes are checked during packaging.
- The manuscript reports clipping failures, unequal optimizer budgets,
  lower input SSIM, and negative synthetic restoration results. It does not
  claim universal superiority or guaranteed spectral feasibility.
- verification.json records the exact compiled PDF and main-source hashes.
  package_sha256.json inventories the packaged files.

## Reproduce Locally

From the project root, with the project's virtual environment active:

```text
python scripts/build_overleaf_package.py
paper\build-tools\tectonic\tectonic.exe --keep-logs --keep-intermediates --outdir paper/build paper/overleaf/main.tex
python scripts/verify_paper_package.py
python scripts/build_overleaf_package.py --package-only
```

The portable compiler is a local verification tool, not a required ZIP
dependency. Overleaf supplies IEEEtran and the standard LaTeX packages.
The ZIP includes the compiled PDF as a preview, not as a compilation input.

Authors must review the scientific claims and the selected venue's template,
page limit, and disclosure requirements before submission. IEEE style alone
does not establish compliance with a particular journal or conference.
