# Research and Evidence Brief for the IEEE Paper

Prepared: 13 October 2026. This is research preparation and a writing specification, **not the full manuscript**. The intended manuscript is at most 10 compiled pages in two columns, including references, tables, and figures.

## 1. Recommendation

The completed experiments support a paper about **spectral-ratio-preserving visual enhancement and its contrast-cost trade-off**, not universal image-quality superiority, guaranteed constraint satisfaction, or restoration of clean imagery.

Suggested working title:

**Spectral-Ratio-Preserving CLAHE-HGPSO Enhancement of Four-Band Sentinel-2 Images**

Use SRP-CLAHE-HGPSO as the method name. Avoid claiming a new hybrid optimizer: the hybrid-search foundation is inherited. The original paper is Rentapalli and Khairuzzaman, *Enhancement of Satellite Images Using Contrast-Limited Adaptive Histogram Equalization With Hybrid Grey Wolf and Particle Swarm Optimization*, DOI [10.1109/ACCESS.2026.3651193](https://doi.org/10.1109/ACCESS.2026.3651193). Its author manuscript was inspected and its publisher-deposited Crossref metadata subsequently verified. See [literature notes](LITERATURE_NOTES.md#l01-hgpso-source).

Main research question: Can a shared-gain, constraint-aware adaptation improve display contrast while retaining RGB-NIR spectral ratios at a modest image-specific search budget?

Supporting questions:

1. What does optimization add beyond non-optimized common-gain CLAHE?
2. How do spectral distortion and measured method-stage cost compare with independently reproduced RGB-only enhancement baselines?
3. How often do the constraints hold at full resolution, and what trade-offs appear in auxiliary experiments?

These questions organize a retrospective analysis of completed experiments. Do not present them as preregistered hypotheses.

### Supported contributions

- A reproducibly specified four-band enhancement implementation using one positive gain per pixel, with an explicit preservation argument and clipping qualifications.
- An image-specific feasibility-ranked search over an inherited five-parameter transform, proxy evaluation, and full-resolution elite checking.
- An empirical comparison on 200 test chips, with common-gain CLAHE as the closest architectural control, paired comparisons, constraint failures, and exploratory cost/parameter analyses.

The combination is a **candidate contribution**, not a verified first-in-literature result. A targeted literature search does not establish exhaustive novelty. Common-channel scaling already has prior art; cite it explicitly [L06].

## 2. Evidence Boundary

Use only `results/standard_run` for primary experimental claims. Its finished manifest, frozen configuration, raw data, and summary tables agree. The `paper_practical` run is incomplete and must not supply claimed main settings or results. Configured `paper_full` settings are not completed evidence.

| Evidence | Actual extent | Source |
| --- | --- | --- |
| Main comparison | 200 chips x 9 methods = 1,800 rows | `raw/per_image_metrics.csv` |
| Available validation subset | 40 chips | `manifest/dataset_validation.csv` |
| Hyperparameter calibration actually used | 6 validation chips, 54 candidate-chip runs | `tables/validation_selection_per_run.csv` |
| Ablations | 20 variants x 8 test chips = 160 rows | `raw/ablation_per_image.csv` |
| Repeated seeds | 8 chips x 3 seeds x 2 methods = 48 rows | `raw/stability_per_run.csv` |
| Synthetic paired experiment | 12 chips x 4 methods = 48 rows | `raw/synthetic_paired_per_image.csv` |
| Post hoc sensitivity analysis | 50 test location/acquisition-time groups | `paper/evidence/pairwise_group_sensitivity.csv` |

Paths in the source column are relative to `results/standard_run` unless stated otherwise. [Evidence audit](evidence/README.md) explains derived files and the rerun command. The audit verifies source hashes before and after execution; it does not rerun enhancement or overwrite the archived evidence.

### Claim Ledger

| Proposed claim | Decision and exact qualification |
| --- | --- |
| Mean local RMS contrast is 33.38% above common-gain CLAHE | Supported as a ratio of test-set means; chip-level Holm-adjusted p = 1.108e-30 |
| Spectral preservation is significantly better than common-gain CLAHE | Not supported by the primary chip-level tests for NDVI, NDWI, or SAM |
| Spectral errors are much lower than the RGB-only HGPSO reproduction | Supported for this implementation and comparison; architecture differs because NIR is unchanged in the RGB-only adapter |
| Contrast is superior to HGPSO | Not established: mean is 2.89% higher, but adjusted p = 1 and the paired median difference is slightly negative |
| Runtime is 28.19% lower than HGPSO | Supported for the measured method-stage timings, under unequal search budgets; not a matched-budget algorithmic speedup |
| All outputs obey the constraints | False: 190/200 satisfy all four; 10 exceed the clipping threshold |
| The method preserves absolute reflectance | False: multiplying by a gain changes radiometry even without changing ratios |
| Shared gain always preserves indices exactly | Only in the ideal unclipped, positive-gain case without denominator regularization or numerical error |
| More entropy proves better enhancement | False: entropy is a display-domain descriptor, not recovered physical information or perceptual validation |
| The method restores degraded images | Not supported: the auxiliary clean-reference scores worsen relative to no enhancement |
| The optimizer is universally more stable | Not supported by three-seed within-chip utility variation |
| The study proves a novel first-ever spectral-preserving hybrid | Not established by the search or experiments |

## 3. Ten-Page Structure: What to Write Where

Use the [page budget](WRITING_PLAN.md): 9.5 planned pages plus 0.5 page reserve. These are space allocations, not forced page breaks. A final page count requires a complete compiled manuscript.

### Front Matter: approximately 0.75 page

**Title and authors:** Use the working title or a closely scoped revision. Add real author names, affiliations, corresponding author, and any genuine funding statement only after confirmation.

**Abstract:** Target approximately 180-220 words, subject to the selected venue's limits. Write it last. Include, in order:

1. The conflict between visual enhancement and multispectral-ratio consistency.
2. The four-band shared-gain adaptation, constraint-aware image-specific search, and proxy/full-resolution evaluation.
3. The 200-chip experiment and closest control, common-gain CLAHE.
4. Contrast improvement of 33.38% over that control, small average NDVI/NDWI/SAM errors, and 95% full-resolution feasibility.
5. The cost qualification: lower timed stage cost than the larger-budget HGPSO reproduction but substantially slower than common-gain CLAHE.

Do not put unsupported "state-of-the-art," "all constraints guaranteed," or restoration claims in the abstract. Avoid citations and undefined abbreviations there. Suggested index terms: multispectral image enhancement; Sentinel-2; contrast-limited adaptive histogram equalization; spectral-ratio preservation; constrained optimization.

### I. Introduction: approximately 1 page

Write four compact paragraphs followed by the contribution list:

- **P1, practical problem:** Display enhancement can change bands used for normalized-difference indices. Separate visual interpretability from the quantitative integrity of the original product. Cite dataset context and the index/SAM foundations [L07-L10]. Do not claim downstream classification gains without an experiment.
- **P2, existing approaches:** Introduce histogram/gamma enhancement and image-specific optimization [L02-L05, L01]. Mention that visible-only changes can disturb ratios involving unchanged NIR.
- **P3, gap and control:** State the practical question of increasing contrast without unnecessary spectral distortion and cost. Introduce non-optimized common-gain CLAHE as the control that separates the shared-gain architecture from search. Acknowledge shared-scaling prior art [L06].
- **P4, scope:** State four bands, cloud-free valid pixels, image-specific optimization without model training, 200 test chips, and the limited claim scope. Recent learned enhancement [L13-L14] is related work, not an experimentally beaten baseline.
- **Contributions:** Use the three qualified contributions above. Finish with a one-sentence organization statement only if needed.

Do not repeatedly describe the work as extending a "parent paper." Cite the source naturally as earlier work, explain inherited components once in Method, and use `HGPSO` in tables.

### II. Related Work: approximately 0.75 page

Use three short thematic subsections or paragraphs, not one paragraph per source:

- **Contrast enhancement and search:** AHE/CLAHE, adaptive gamma correction, PSO/GWO, and the source HGPSO method [L01-L05]. Explain which elements are reused rather than comparing published numbers from incompatible datasets.
- **Spectral and color consistency:** Established common-channel scaling and gamut/clipping issues [L06, L15]. Connect this to the four-band application and explain that spectral shape and absolute radiometry are different properties.
- **Learned remote-sensing enhancement and evaluation:** Briefly position recent low-light/multispectral networks [L13-L14]. Explain that supervised restoration needs appropriate paired data and that this study instead evaluates input-relative ratios and display descriptors. Cite SSIM's reference-based interpretation [L11].

End with the narrowly stated contribution gap. Do not claim all existing methods ignore spectral preservation, or that learned methods require more cost than this implementation without measurements.

### III. Proposed Method: approximately 2 pages

Use four subsections plus compact pseudocode. The code-grounded equations and settings are specified in Section 4 below.

- **A. Input and display model:** Define the RGB-NIR cube, valid mask, reflectance scaling, original-fitted display percentiles, and HSV value used to construct gain. Specify that metric calculations in reflectance and display domains differ.
- **B. Enhancement and shared gain:** Define CLAHE, inherited local transform, five bounded parameters, robust rescaling, positive shared gain, and final per-band clipping. Cite [L01-L02]. Clearly mark implementation assumptions.
- **C. Preservation and constraints:** Give the short ratio/SAM invariance argument; define NDVI, green-NIR NDWI, SAM, and clipped-band-sample fraction. Explain epsilon, dark-vector, and clipping exceptions. State thresholds and non-guaranteed feasibility.
- **D. Search and evaluation:** Explain normalized visual score versus stable bookkeeping utility, feasibility-first selection, inherited PSO/GWO steps, proxy/full-resolution elites, and early stopping. The optimizer is not a new invention.

**Algorithm 1:** Input cube/mask/settings; build original display and proxy context; initialize parameters; evaluate candidates; rank feasibility then visual score; update PSO then GWO; record stable progress and check stopping; evaluate four elites at full resolution; return best feasible elite or least-violating elite. State that this last fallback can be infeasible. Invalid pixels are restored.

**Fig. 1:** An original pipeline diagram of these operations, not a copied figure from the source paper. Distinguish display-domain search, four-band gain application, and reflectance-domain constraint checking. This diagram is planned, not yet drawn.

### IV. Experimental Setup: approximately 1.25 pages

- **A. Dataset and partition:** Describe the selected Sentinel-2 L2A cloud-cover dataset [L07], four 10-m bands and 512 x 512 chips, 40 available validation and 200 test chips. Report that only six validation chips calibrated settings. Report metadata group separation, selection procedure, masks, and the mostly clear selection caveat.
- **B. Methods and settings:** List Original, HE, CLAHE, AGCWD, common-gain CLAHE, PSO, GWO, HGPSO, and SRP-CLAHE-HGPSO. Say the classical and optimization baselines are independent implementations/adaptations. Disclose visible-only versus four-band adapters and gain-bound differences. Provide actual population/generation/proxy/elite settings.
- **C. Metrics and statistics:** Define descriptor domains, input-relative spectral errors, input SSIM, timed method-stage runtime, paired units, direction-oriented effect sizes, and per-metric Holm correction. State the post hoc group sensitivity separately [L11-L12, L16-L18].
- **D. Reproducibility:** Report manifest-derived software/hardware, frozen configuration, seeds, and evidence availability. Do not report unused `max_workers=2` as executed parallelism or generic processor text as an exact CPU model.

**Table I:** Compact settings and dataset summary. Its main/auxiliary sample counts, calibration scope, budgets, and thresholds must match archived evidence.

### V. Results: approximately 2 pages

Recommended ordering:

1. **Main visual-spectral comparison:** Present Table II, leading with proposed versus common-gain CLAHE, then the RGB-only methods. Report contrast, spectral errors, input fidelity, and clipping without omitting unfavorable results.
2. **Statistics and feasibility:** Present selected Table IV comparisons, significance versus common-gain and HGPSO, and 190/200 constraint compliance. Explain the ten clipping failures and worst-case clipping; means alone are insufficient.
3. **Cost and convergence:** Report runtime alongside search/evaluation counts. Explain unequal budgets and the 18.58x runtime relative to common-gain CLAHE. Use the corrected main-test-only convergence plot, not the mixed-history archived figure.
4. **Auxiliary sensitivity:** Table III summarizes a small, selected set of ablations; discuss within-chip seed variation and synthetic scores briefly. Full tables can go in permitted supplements, but negative synthetic results must still be stated in the paper.

**Fig. 2:** A compact same-display-bounds grid. Include a typical chip, a low-contrast case, and a difficult/clipping case selected by a predeclared descriptive rule applied to saved outputs. Do not cherry-pick scenes that only favor the proposed method. Retain full grids in supplementary evidence.

**Fig. 3:** Two panels for visual-spectral trade-off and quality-cost trade-off. Show per-chip variation or a suitable distribution summary; mark logarithmic axes and handling of zeros explicitly. Use method labels, not "parent" labels. Current archived scatter/boxplot assets require caption and axis review before manuscript insertion.

**Fig. 4:** [Audited convergence](evidence/convergence_main_test.pdf), median best stable visual utility over 200 main-test chips per optimizer. Carry early-stopped runs' last values forward within each method's observed horizon; proposed ends at generation 12 and baselines at 20. Generation is not equal evaluation count or cost. Do not compare utility as an independently validated perceptual metric.

### VI. Discussion and Limitations: approximately 0.5 page

Prioritize these conclusions:

- The shared gain largely explains spectral consistency; optimization adds contrast over the closest common-gain control, not established significant spectral improvement over it.
- The observed HGPSO cost difference combines budget and implementation choices; a matched-budget experiment is still needed.
- Feasibility checking is not a guarantee: proxy-to-full-resolution transfer and a least-violating fallback leave clipping failures.
- Increasing contrast reduces input SSIM and does not restore the synthetic clean reference. Shared gain changes absolute radiometry, so preserve original products for quantitative radiometric use.
- Small calibration/ablation/stability subsets, mostly clear selected chips, correlated acquisitions, no learned-method comparisons, and no labeled downstream task limit generalization.

### VII. Conclusion and Availability: approximately 0.25 page

Answer the main question with one qualified sentence per demonstrated outcome: increased contrast over common-gain CLAHE; low input-relative spectral errors; 95% threshold compliance; measured budget-dependent cost. Do not introduce new results.

Future work should name matched-budget comparisons, clipping-safe/full-resolution feasible fallbacks, geographically verified holdouts, and downstream task assessment. State real code/data links when available; a local path is not a public release. Add dataset attribution and license obligations [L07].

### References and Acknowledgments: approximately 1 page

Start with the literature notes' core sources, then retain only those cited. Roughly 16-20 well-chosen references may fit, but reference count is not an IEEE rule. Use numbered IEEE citations in first-citation order and verified bibliographic metadata. Follow the exact target venue's template and policy [L19]. Do not invent a grant, author contribution, public repository, or institutional approval.

## 4. Method Details That Must Match the Implementation

### Domains and Mask

Let x(p) = [B,G,R,N] be the stored four-band reflectance vector at valid pixel p, corresponding to B02, B03, B04, B08. Only the displayed visible channels are reordered to RGB. The original cube's per-visible-band 2nd/98th percentiles define a display mapping D; reuse D for all methods on that chip. The HSV value V0 is obtained from D(x). CLAHE acts on V0 with a normalized clip limit of 0.01, nominal 8 x 8 tiles, and 256 bins.

The display mapping is not physical reflectance, and its offsets/clipping mean that a target HSV value is not necessarily reproduced exactly after gain is applied to reflectance. Display luma is 0.2126 R_d + 0.7152 G_d + 0.0722 B_d; no sRGB gamma linearization is performed. Invalid pixels are filled for filtering and restored in output; reported metrics are averaged on the valid mask. Filter neighborhoods can still include filled pixels.

Entropy uses 256 bins after 8-bit display-luma quantization. Local RMS contrast is the mean local standard deviation from a 7 x 7 reflect-boundary uniform filter. Edge density is the valid-pixel fraction detected by OpenCV Canny with thresholds 50/150 on 8-bit luma, not average gradient intensity. Sharpness is the variance of an OpenCV Laplacian on 8-bit luma. Input SSIM uses a full similarity map on display luma and then a valid-mask mean.

### Inherited Transform

For CLAHE value o, local mean m, local second moment E_W[o^2], and global mean mu:

```text
theta = (a,b,c,k,p)
sigma_c = sqrt(max(E_W[o^2] + (c^2 - 2c)m^2, 1e-10))
residual = o - c m
E_theta = [k mu^g / max(sigma_c^l + b, 1e-8)]
          * sign(residual)(abs(residual) + 1e-12)^p + max(m,0)^a
V_theta = clip((E_theta - q_1)/(q_99 - q_1), 0, 1)
```

Use a 7 x 7 reflect-boundary uniform window, g = l = 1, and valid-pixel percentiles for robust rescaling. Include the flat-range safeguards by reference to code rather than filling the manuscript with exceptional-case equations. Parameter bounds: a [0.1,1.5], b [0.1,0.5], c [0.1,1.0], k [0.5,1.5], p [0.1,2.0].

These exact choices, signed fractional powers, local-variance interpretation, boundary rule, and robust rescaling are reproduction assumptions. The source and this study do not use identical evaluation protocols/objectives. The manuscript must not claim exact numerical reproduction of the source results. Code anchor: `src/image_ops.py::parent_transform`.

### Shared Gain and Invariance

```text
r(p) = clip((V_theta(p) + 1e-4)/(V0(p) + 1e-4), 0.5, 2.0)
y_b(p) = clip(r(p) x_b(p), 0, 1), for b in R,G,B,N
```

The optional mask-normalized Gaussian gain smoothing has selected sigma = 0, so smoothing is **not active in the main experiment**. Any smoothed gain still remains common across bands at each pixel.

Without final per-band clipping, with r > 0 and nonzero denominators, y_i/y_j = x_i/x_j. Consequently NDVI = (N-R)/(N+R), McFeeters NDWI = (G-N)/(G+N), and vector angle are invariant. A common positive scalar changes vector magnitude, not direction.

The measured indices use delta = 1e-8 in the denominator: after scaling, `(u-v)/(u+v+delta/r)` replaces `(u-v)/(u+v+delta)`. Thus exact cancellation need not hold in dark pixels. SAM also has numerical floors/snap tolerances. Per-band clipping can break invariance substantially. Do not describe near-zero recorded errors as exact symbolic zeros or perfect recovery.

### Constraints and Objectives

Input-relative masked MAE for NDVI and NDWI must each be <= 0.005, mean SAM <= 0.5 degree, and clipped-band-sample fraction <= 0.005. Define the last metric as:

```text
count of out-of-range band samples before final clipping
-------------------------------------------------------
             4 * number of valid pixels
```

It is **not** the fraction of unique pixels that have any clipped band.

Visual weights for entropy, local RMS contrast, edge density, sharpness, and input SSIM are (0.25,0.25,0.20,0.15,0.15). In each population, normalize the first four with the 10th/90th percentiles to [0,1], with a 0.5 fallback for flat ranges; SSIM is clipped to [0,1] and used directly. Denote the resulting population-relative score Q_vis.

Stable visual utility is a separate fixed-reference bookkeeping score: entropy/8, clipped contrast and edge ratios with `(ratio-0.5)/(2.5-0.5)`, sharpness with `(ratio-0.5)/(3-0.5)`, and SSIM, using the same weights. Check the exact clipping/reference safeguards in `src/metrics.py` when typesetting. It is not a newly validated perceptual metric.

Normalized total constraint violation is the sum over constraints of `max(metric/threshold - 1, 0)`. Feasible population candidates rank by visual score then stable utility; infeasible candidates rank by smaller violation then stable utility, below every feasible candidate. Historical-best bookkeeping uses feasibility and stable utility or lower violation. Full-resolution final selection uses feasibility then stable utility for feasible elites, or least violation if none is feasible. Distinguish the ranking score from the convergence/stopping score.

### Search and Timing

The inherited hybrid applies a PSO update followed by a GWO leader update per generation, without evaluating an independent intermediate PSO population. PSO inertia is 0.729 and both acceleration constants are 1.49445. Early stopping uses patience 8 and stable-utility tolerance 1e-4. Parameter and velocity boundary handling should be summarized from `src/optimizers.py` rather than copied from a generic optimizer description.

Main proposed: population 8, maximum 12 generations, proxy 256 x 256, four full-resolution elites. PSO/GWO/HGPSO baselines: population 10, maximum 20 generations, same proxy, one full-resolution candidate. These are deliberately different configurations, not matched-budget controls.

Reported runtime excludes scene loading and preprocessing/context construction, and includes candidate metric evaluation and elite evaluation. Simple-method and optimized-method boundaries are not identical end-to-end pipelines. Call it **timed method-stage runtime** and disclose these boundaries.

## 5. Results to Use

All main entries below are arithmetic means over the same 200 chips, not means over pixels or acquisition groups. Standard deviations are available in [verified summary](evidence/main_summary_verified.csv); include mean +/- standard deviation in the paper's main table. Round labels and values for readability without turning tiny errors into falsely exact zero.

| Method | Entropy | Local RMS contrast | Input SSIM | NDVI MAE | NDWI MAE | Mean SAM (deg) | Clip fraction | Stage time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 7.44479 | 0.08391 | 1.00000 | 0 | 0 | 0 | 0 | 0.08164 |
| HE | 6.84581 | 0.14984 | 0.49897 | 0.16413 | 0.16452 | 8.85807 | 0.002977 | 0.12650 |
| CLAHE | 7.22594 | 0.17130 | 0.53574 | 0.12844 | 0.13014 | 7.05724 | 0.004953 | 0.15202 |
| AGCWD | 6.72474 | 0.10047 | 0.52673 | 0.12659 | 0.12652 | 6.81203 | 0.007180 | 0.12965 |
| Common-gain CLAHE | 7.25646 | 0.16724 | 0.54840 | 4.142e-5 | 9.619e-5 | 0.011549 | 0.002885 | 0.15095 |
| PSO | 7.31589 | 0.21170 | 0.43850 | 0.14864 | 0.15052 | 8.14938 | 0.003333 | 5.03178 |
| GWO | 7.27188 | 0.22050 | 0.41829 | 0.15563 | 0.15743 | 8.48250 | 0.003548 | 3.61493 |
| HGPSO | 7.31200 | 0.21680 | 0.42555 | 0.15050 | 0.15234 | 8.22454 | 0.003316 | 3.90631 |
| SRP-CLAHE-HGPSO | 7.22639 | 0.22306 | 0.42917 | 1.948e-5 | 5.267e-5 | 0.005299 | 0.001391 | 2.80509 |

Baseline qualification for the table caption: HE/CLAHE/AGCWD and PSO/GWO/HGPSO use this study's visible-band gain adapters with NIR unchanged and gain bounds [0.05,20]. Common-gain CLAHE and the proposed method apply shared gain to all four bands with bounds [0.5,2]. HGPSO is independently reproduced under disclosed assumptions. A brief caption plus Experimental Setup avoids repeating a long disclaimer in every figure.

### Paired Tests to Highlight

Two-sided Wilcoxon signed-rank tests with seven proposed-versus-baseline comparisons corrected separately for each metric; Original is excluded from those families. Positive direction-oriented rank-biserial effect favors the proposed method. Use audited exact-equality ranks from [chip audit](evidence/pairwise_chip_audited.csv).

| Control | Metric | Holm p | Audited effect | Interpretation |
| --- | --- | ---: | ---: | --- |
| Common-gain CLAHE | Contrast | 1.108e-30 | +0.95154 | Higher display contrast |
| Common-gain CLAHE | Input SSIM | 9.498e-27 | -0.88766 | Lower input fidelity |
| Common-gain CLAHE | NDVI MAE | 0.74274 | -0.02677 | No demonstrated difference |
| Common-gain CLAHE | NDWI MAE | 0.71888 | -0.02935 | No demonstrated difference |
| Common-gain CLAHE | SAM | 0.27046 | +0.16497 | No demonstrated difference |
| Common-gain CLAHE | Runtime | 1.005e-33 | -1.00000 | Proposed method is slower |
| HGPSO | Contrast | 1.00000 | +0.05383 | No demonstrated superiority |
| HGPSO | NDVI/NDWI/SAM | 1.005e-33 each | +1.00000 each | Lower spectral error for this RGB-only control |
| HGPSO | Runtime | 9.879e-27 | +0.87801 | Lower measured stage time, unequal budgets |

Non-significance does not prove equivalence. Wilcoxon assumes appropriately independent pairs and its location-shift interpretation depends on the difference distribution; do not reduce it to a universal test of medians. All output rows are retained, including infeasible proposed outputs.

The archived effect-size helper merges near ties using `numpy.isclose`; the audit uses SciPy exact-equality ranks. Effects differ by at most 0.01920; adjusted p-values differ only at floating-point precision and no significance decision changes. Do not mix effect values from the two implementations in one table.

Archived Friedman omnibus tests use the eight enhancement methods (excluding Original) on 200 complete blocks. All eight metric tests are significant; contrast has statistic 805.202, p = 1.400e-169. This indicates some methods differ, not that the proposed method beats each baseline. Retain full omnibus results in supplementary evidence rather than consuming the main statistical table with redundant tests.

### Acquisition-Group Sensitivity

Neighboring chips may be dependent. Average each method's metric within a location/acquisition-time group and compare the 50 equal-weight group means as an **exploratory, post hoc** sensitivity analysis [L16]. This is not proof of geographic independence; verified footprints are still needed.

Contrast versus common-gain CLAHE remains significant (Holm p = 2.132e-14), and contrast versus HGPSO remains non-significant (p = 0.45950). HGPSO spectral-error and runtime comparisons remain significant. Some conclusions change: proposed entropy is lower than HGPSO at group level (p = 0.02863); SAM and clipping versus common-gain CLAHE become significant (p = 0.00582 and 0.00566), with tiny/zero-centered practical differences. Include these changes honestly, not only the results supporting the main story.

### Feasibility and Cost

- All 200 proposed outputs meet NDVI, NDWI, and mean-SAM thresholds. Only 190 meet the clipping threshold, for 95% joint feasibility. The ten failures are listed in [infeasible chips](evidence/infeasible_test_chips.csv).
- Maximum proposed NDVI MAE is approximately 0.000897, NDWI MAE 0.004046, mean SAM 0.48981 degree, and clipped-band-sample fraction 0.100465. The last corresponds to 10.0465% of valid band samples, not 10.0465% of unique pixels.
- Proposed mean stage time is 2.80509 s, versus HGPSO 3.90631 s (-28.19%) and common-gain CLAHE 0.15095 s (18.58x). These percentages use ratios of arithmetic means.
- Proposed mean proxy evaluations: 92.68, plus four full evaluations. HGPSO: 146 proxy evaluations, plus one full evaluation. Mean pixel-equivalent work is 27.17 versus 37.5, calculated as proxy evaluations x proxy/full pixel-count ratio plus full evaluations. This is a descriptive workload proxy, not measured computational complexity or a hardware-normalized cost model.

### Ablations: Descriptive Evidence, Not Strong Causal Proof

Use selected settings in Table III and keep all 20 in supplementary evidence. Each setting uses only eight chips and different seed tags; setting and optimization randomness are confounded.

- Shared-gain and constraints: removal of constraints has tiny errors on this small subset, so it does not prove constraints are essential for spectral preservation. The algebraic shared gain is the primary preservation mechanism.
- Gain smoothing: sigma 0, 0.5, 1, 2 have mean contrasts about 0.2584, 0.2410, 0.1984, 0.1354. Smoothing lowers contrast in these runs, but do not claim a general causal optimum from differently seeded trials.
- Gain bounds: the narrow [0.7,1.5] setting achieves similar contrast and zero mean clipping in this subset; the selected [0.5,2] range is not uniquely optimal.
- Proxy size 128, 256, 512 gives approximately 0.904, 2.215, 11.361 s. The 256 proxy reduces stage time relative to full-resolution search here, but contrast/utility do not establish equal-quality equivalence.
- Larger search budgets do not improve every metric monotonically. The main 8 x 12 configuration is not one of the A7 budget variants; use [main methods on the same eight chips](evidence/main_methods_on_ablation_subset.csv) if a contextual main-method comparison is needed.
- Objective-weight variants define different utilities. Do not rank their utilities as though they were a single common quality scale; compare raw metrics instead.

### Repeated Seeds and Synthetic Pairing

Report seed variability **within each chip**, then summarize those standard deviations. The archived pooled coefficient of variation combines scene and seed differences and is not pure optimizer stability. Across eight chips and three seeds, the median within-chip stable-utility SD is about 0.00852 for proposed and 0.00600 for HGPSO. Proposed is therefore not uniformly more stable in visual utility. Near-zero spectral error also makes a coefficient of variation unstable or misleading.

The synthetic experiment applies spatial dimming, additive band-dependent haze, and Gaussian noise to 12 observed L2A chips, then compares with the undegraded chips using shared clean-fitted display bounds. The reference is undegraded observed imagery, not pristine physical ground truth.

| Method | Clean-reference PSNR (dB), mean | Clean-reference SSIM, mean |
| --- | ---: | ---: |
| No enhancement of degraded input | 12.1424 | 0.51835 |
| CLAHE | 9.8189 | 0.35172 |
| HGPSO | 9.2123 | 0.29299 |
| SRP-CLAHE-HGPSO | 9.3899 | 0.28838 |

All three enhancement methods are worse than leaving the degraded input unchanged on these reference-based scores. Include this finding as a limitation of enhancement-versus-restoration, even if detailed synthetic tables are supplementary. See [verified synthetic summary](evidence/synthetic_summary_verified.csv).

## 6. Dataset and Reproducibility Details

- The selected dataset comes from a cloud-cover segmentation challenge, not an enhancement benchmark with clean targets [L07]. Its masks are used to exclude cloud/invalid pixels, not to train an enhancement network.
- Selected test valid-pixel fractions have minimum about 0.9503 and mean 0.9894; most chips are very clear. Do not generalize to dense clouds or heavy real haze.
- There are 50 test and 13 validation location/time groups, with no overlap in those labels and no overlapping location labels between splits. This metadata check does not guarantee non-overlapping geographic footprints.
- Representative selection sorts by cloud fraction, valid fraction, and chip ID, then selects spaced indices. Its accepted seed argument is unused; do not describe the selection as seeded random sampling.
- The loading mask requires finite, non-nodata, positive values in all four bands and excludes cloud labels 1/255; configured minimum valid fraction is 0.70. Automatic scaling divides by 10,000 if the valid-sample 99.5th percentile exceeds 2, otherwise by 1. Describe the resulting arrays as reflectance-like scaled values unless radiometric calibration provenance is separately verified.
- Calibration sequentially considers local windows {7,15,31}, gain sigma {0,1,2}, and gain maximum {1.5,2,2.5} on six chips. Each stage has 18 evaluations, totaling 54. Selected settings are window 7, sigma 0, gain [0.5,2]. It is not a full joint grid search over 40 validation chips.
- Primary record sources: frozen configuration, run manifest, dataset validation, and runtime columns. Report Python 3.12.4, Windows 11, 16 logical/10 physical CPUs and approximately 15.77 GB RAM as recorded, while marking the exact CPU model unresolved. Use recorded package versions, not the current environment's versions.
- Execution is sequential in the current experiment code despite a `max_workers` configuration entry. No GPU acceleration claim is supported.
- Provide enough implementation details to reproduce independently: masks, scaling, sorting/selection, seeds, display mapping, boundary rules, baseline adapters, search budgets, metric definitions, and software versions.

## 7. Remaining Work Before Stronger Claims or Submission

### Possible to Draft Now

A transparent 10-page manuscript can be drafted from the completed experiment, provided it uses the qualified scope and reports the failures and negative auxiliary results. The preparation is enough to start writing; it is not a guarantee of publication readiness or acceptance.

### High-Priority Experimental Gaps

1. Matched-budget and matched-adapter comparisons: evaluate shared-gain transform variants with identical populations, evaluations, and gain bounds, and include other simple spectral-preserving gain choices. The current comparisons cannot isolate every proposed component.
2. Repeated seeds on broader subsets and same-seed ablations. If claiming optimizer novelty or causal contribution, these are necessary.
3. Full-resolution feasible fallback or clipping-safe scalar gain projection. Changing the algorithm requires a new version and new results; do not retrofit a guarantee into the archived study.
4. Geographically verified train/validation/test footprints and group-aware inference. Current metadata group sensitivity is exploratory.
5. Broader acquisitions/sensors and genuine low-light/haze cases, plus appropriate learned baselines if claiming competitiveness with contemporary methods.
6. Labeled downstream evaluation if claiming improved vegetation/water mapping or classification. Index closeness alone is not a task-performance result.

### Editorial and Provenance Gaps

- Select the exact IEEE venue, check its page limit, required template, reference style, reproducibility policy, and AI-use disclosure policy. IEEE-style two columns alone do not imply IEEE submission compliance.
- Verify the source article's final publisher citation and any other metadata-only source before bibliography finalization; retain no uncited references.
- Confirm actual authorship, affiliation, corresponding email, funding, and acknowledgments.
- Review dataset attribution/CC BY obligations, and publish a real code/evidence release if an availability link is claimed.
- Create the new pipeline figure and a documented compact qualitative selection; audit every caption and axis.
- Compile the complete paper, verify at most 10 pages, and check overflow and cross-references. At the preparation stage no compiler was installed; a portable compiler is now available in `paper/build-tools`, and the package verification record documents the manuscript build.

## 8. Writing Order

1. Freeze which result archive and audited derived files are being cited.
2. Write Method and Experimental Setup directly from implementation/evidence.
3. Build the compact main and statistical tables, then write Results including limitations.
4. Write Introduction and Related Work using the literature map, with narrow contributions.
5. Write Discussion, Conclusion, and then Abstract.
6. Finalize captions, numbered references, author details, and the 10-page compiled layout.

The next requested step should be the manuscript draft based on this brief, not fabricated experiments or a rewritten narrative implying outcomes the evidence does not show.
