# Method-to-Manuscript Mapping

This file maps the implementation to the proposed manuscript draft.

## Manuscript Eq. (1): RGB -> HSV

Implementation: `src/image_ops.py::rgb_to_hsv`.

The RGB display is constructed from B04/B03/B02 using percentile bounds fitted only to the original scene. The same display bounds are reused for all methods to avoid independent post-hoc stretching that could make one method look artificially better.

## Eq. (2): CLAHE

Implementation: `src/image_ops.py::clahe_value` using `skimage.exposure.equalize_adapthist`.

Default clip limit: 0.01. Tile grid: 8×8. Kernel size is computed from image dimensions / grid count. The exact library version is stored in `manifest/run_manifest.json`.

## Eqs. (3)-(6): theta = [a,b,c,k,p]

Bounds are in `configs/paper.yaml`.

## Parent local-statistics transform

Implementation: `src/image_ops.py::parent_transform`.

Research-integrity note: the source paper does not fully specify all constants/window semantics. This independent reproduction fixes `g=l=1`, publishes the chosen local window, uses a c-dependent local variance form, signed fractional power, reflect boundaries, and robust 1st-99th percentile output rescaling. These assumptions must be disclosed.

## Shared gain, manuscript Eqs. (12)-(14)

Implementation:

- `gain_from_values`
- `apply_gain_cube`

The gain is derived from optimized display V and applied identically to B02/B03/B04/B08 for the proposed method.

## Analytical preservation, manuscript Eqs. (15)-(20)

The code does not "prove" the equations; it numerically verifies their consequences via NDVI, NDWI and SAM. The analytical proof remains a manuscript result.

## Qvis, manuscript Eq. (21)

The optimizer normalizes entropy, local RMS contrast, edge density, and Laplacian variance robustly within each generation. SSIM-to-input is already bounded [0,1]. The specified weights are applied.

For cross-generation PSO personal-best bookkeeping, an auxiliary bounded stable utility is used because within-generation normalization is not directly comparable across generations. This is an implementation detail that should be reported.

## Feasibility constraints, Eqs. (22)-(25)

Default thresholds:

- NDVI MAE <= 0.005
- NDWI MAE <= 0.005
- mean SAM <= 0.5 degrees
- clip fraction <= 0.005

Candidate ranking is feasibility-first.

## Algorithm 1

Implementation is distributed across `src/methods.py` and `src/optimizers.py`:

1. load four co-registered bands and cloud mask;
2. build RGB/HSV/V;
3. proxy arrays;
4. evaluate population;
5. PSO update;
6. sequential GWO refinement;
7. early stopping;
8. elite full-resolution confirmation;
9. return cube, gain, metrics and audit information.

## Budget adaptation for the selected benchmark

The draft discussed 1024 full / 512 proxy. Radiant Earth chips are 512×512, so the primary proposed run uses 256×256 proxy and full 512×512 elite verification. The report computes actual pixel-equivalent evaluations rather than copying the draft's 1024-based estimate.
