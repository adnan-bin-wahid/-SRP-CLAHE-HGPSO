# SRP-CLAHE-HGPSO Execution Report

## Research-integrity status

This report contains **measured outputs from this run only**. It does not convert design targets into results. The parent HGPSO method is an independent reproduction because the source paper leaves implementation details underspecified. PSNR/SSIM against a real degraded input are treated as fidelity/change measures, not restoration accuracy; restoration claims are reserved for the optional paired synthetic track.

## Run manifest

```json
{
  "project": "SRP-CLAHE-HGPSO",
  "preset": "quick",
  "started_unix": 1786990984.9692078,
  "dataset_root": "E:\\IIT\\8th_semester\\image\\SRP_CLAHE_HGPSO_Paper_Experiment_Suite_v1_2\\SRP_CLAHE_HGPSO_Paper_Experiment_Suite_v1_2\\data\\demo_dataset",
  "validation_images_available": 4,
  "test_images_used": 3,
  "environment": {
    "python": "3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)]",
    "platform": "Windows-11-10.0.26200-SP0",
    "machine": "AMD64",
    "processor": "Intel64 Family 6 Model 191 Stepping 2, GenuineIntel",
    "logical_cpu_count": 16,
    "physical_cpu_count": 10,
    "cpu_max_mhz": 2500.0,
    "ram_gb": 15.773,
    "packages": {
      "numpy": "2.5.2",
      "scipy": "1.18.0",
      "pandas": "2.3.3",
      "opencv-python": "4.14.0.94",
      "scikit-image": "0.26.0",
      "matplotlib": "3.11.1",
      "rasterio": "1.5.1",
      "psutil": "7.2.2",
      "PyYAML": "6.0.3",
      "Pillow": "11.3.0",
      "tqdm": "4.70.0"
    }
  },
  "git_commit": null,
  "dataset_adaptation": "Radiant Earth Sentinel-2 L2A 512x512 B02/B03/B04/B08 chips with expert cloud_mask.tif; cloud mask is used instead of SCL.",
  "finished_unix": 1786990988.0127838,
  "frozen_config": {
    "display_percentiles": [
      2.0,
      98.0
    ],
    "clahe_clip_limit": 0.01,
    "clahe_tile_grid": [
      8,
      8
    ],
    "local_window": 15,
    "transform_g": 1.0,
    "transform_l": 1.0,
    "transform_rescale_percentiles": [
      1.0,
      99.0
    ],
    "epsilon": 0.0001,
    "gain_min": 0.5,
    "gain_max": 1.5,
    "gain_sigma": 0.0,
    "baseline_gain_min": 0.05,
    "baseline_gain_max": 20.0
  },
  "warnings": []
}
```

## Automatic protocol warnings

- No automatic protocol warning was triggered.

## Main same-data results

| Method              |   n | entropy         | local_rms_contrast   | ssim_to_input   | ndvi_mae             | ndwi_mae             | sam_mean_deg    | clip_fraction        | runtime_sec     |
|:--------------------|----:|:----------------|:---------------------|:----------------|:---------------------|:---------------------|:----------------|:---------------------|:----------------|
| AGCWD               |   3 | 7.4781 ± 0.0039 | 0.0767 ± 0.0002      | 0.5277 ± 0.0059 | 1.262e-01 ± 8.37e-04 | 1.301e-01 ± 8.42e-04 | 7.2028 ± 0.0444 | 0.000e+00 ± 0.00e+00 | 0.0028 ± 0.0002 |
| CLAHE               |   3 | 7.8026 ± 0.0096 | 0.0894 ± 0.0002      | 0.7223 ± 0.0051 | 6.264e-02 ± 1.56e-03 | 6.434e-02 ± 1.55e-03 | 3.5894 ± 0.0820 | 0.000e+00 ± 0.00e+00 | 0.0046 ± 0.0002 |
| Common gain + CLAHE |   3 | 7.8075 ± 0.0100 | 0.0891 ± 0.0002      | 0.7235 ± 0.0052 | 1.697e-08 ± 1.80e-10 | 1.447e-08 ± 7.52e-11 | 0.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.0048 ± 0.0002 |
| GWO                 |   3 | 7.5493 ± 0.4604 | 0.1202 ± 0.0282      | 0.6014 ± 0.1596 | 7.392e-02 ± 2.64e-02 | 7.697e-02 ± 2.89e-02 | 4.3798 ± 1.7574 | 1.024e-03 ± 7.93e-04 | 0.0576 ± 0.0030 |
| HE                  |   3 | 7.0710 ± 0.0188 | 0.0851 ± 0.0002      | 0.6353 ± 0.0010 | 9.320e-02 ± 9.02e-04 | 9.856e-02 ± 1.09e-03 | 5.8363 ± 0.0655 | 0.000e+00 ± 0.00e+00 | 0.0027 ± 0.0003 |
| Original            |   3 | 7.7734 ± 0.0015 | 0.0592 ± 0.0001      | 1.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.000e+00 ± 0.00e+00 | 0.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.0017 ± 0.0001 |
| PSO                 |   3 | 7.6393 ± 0.0596 | 0.1631 ± 0.0318      | 0.3961 ± 0.0873 | 1.270e-01 ± 7.41e-03 | 1.301e-01 ± 7.96e-03 | 7.0291 ± 0.4421 | 1.413e-03 ± 9.16e-04 | 0.0589 ± 0.0013 |
| Parent HGPSO*       |   3 | 7.6956 ± 0.1673 | 0.1313 ± 0.0426      | 0.5964 ± 0.1771 | 8.002e-02 ± 4.13e-02 | 8.256e-02 ± 4.25e-02 | 4.5656 ± 2.2901 | 2.625e-03 ± 1.15e-03 | 0.0571 ± 0.0022 |
| Proposed SRP-HGPSO  |   3 | 7.6343 ± 0.1214 | 0.1128 ± 0.0347      | 0.5551 ± 0.0718 | 1.807e-08 ± 5.97e-11 | 1.509e-08 ± 1.53e-10 | 0.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.0544 ± 0.0004 |

The columns `ssim_to_input` and any input-referenced PSNR/MSE quantify similarity/change relative to the real input. They are **not** clean-reference restoration metrics.

## Friedman omnibus tests

| metric             |   n |   methods |   friedman_stat |    p_value | significant   |
|:-------------------|----:|----------:|----------------:|-----------:|:--------------|
| entropy            |   3 |         8 |         14.4444 | 0.0438181  | True          |
| local_rms_contrast |   3 |         8 |         16.2222 | 0.0231619  | True          |
| ssim_to_input      |   3 |         8 |         12.7778 | 0.0777115  | False         |
| ndvi_mae           |   3 |         8 |         19      | 0.00818734 | True          |
| ndwi_mae           |   3 |         8 |         19      | 0.00818734 | True          |
| sam_mean_deg       |   3 |         8 |         18.9759 | 0.00826316 | True          |
| clip_fraction      |   3 |         8 |         20.7083 | 0.00422669 | True          |
| runtime_sec        |   3 |         8 |         19.8889 | 0.00581475 | True          |

## Proposed-vs-baseline Wilcoxon tests with Holm correction

| metric             | proposed        | baseline                  |   n |   wilcoxon_stat |   p_value |   rank_biserial |   median_oriented_difference |   p_holm | significant_holm   |
|:-------------------|:----------------|:--------------------------|----:|----------------:|----------:|----------------:|-----------------------------:|---------:|:-------------------|
| entropy            | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |        1        |                  0.209025    |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |       -1        |                 -0.114135    |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      0.25 |       -1        |                 -0.11896     |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               3 |      1    |        0        |                 -0.057743    |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |        1        |                  0.598145    |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               3 |      1    |        0        |                  0.0304731   |        1 | False              |
| entropy            | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |       -1        |                 -0.0682073   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |        1        |                  0.0383983   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               1 |      0.5  |        0.666667 |                  0.0255935   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               1 |      0.5  |        0.666667 |                  0.0259792   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |       -1        |                 -0.0038709   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | HE                        |   3 |               1 |      0.5  |        0.666667 |                  0.0304488   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               1 |      0.5  |       -0.666667 |                 -0.0301583   |        1 | False              |
| local_rms_contrast | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               3 |      1    |        0        |                  0.0108464   |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               2 |      0.75 |        0.333333 |                  0.0250275   |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |       -1        |                 -0.175817    |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      0.25 |       -1        |                 -0.177125    |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               1 |      0.5  |       -0.666667 |                 -0.0901317   |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |       -1        |                 -0.0867697   |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  0.0997694   |        1 | False              |
| ssim_to_input      | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               2 |      0.75 |       -0.333333 |                 -0.0653391   |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |        1        |                  0.12624     |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |        1        |                  0.062788    |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      1    |       -1        |                 -1.16193e-09 |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |        1        |                  0.0671154   |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |        1        |                  0.0936277   |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  0.130508    |        1 | False              |
| ndvi_mae           | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |        1        |                  0.0864406   |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |        1        |                  0.130141    |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |        1        |                  0.0644521   |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      1    |       -1        |                 -5.51052e-10 |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |        1        |                  0.0690595   |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |        1        |                  0.0991265   |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  0.134711    |        1 | False              |
| ndwi_mae           | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |        1        |                  0.0890051   |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |        1        |                  7.20567     |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |        1        |                  3.59        |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      1    |        0        |                  0           |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |        1        |                  3.84485     |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |        1        |                  5.874       |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  7.23931     |        1 | False              |
| sam_mean_deg       | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |        1        |                  4.90049     |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      1    |        0        |                  0           |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      1    |        0        |                  0           |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      1    |        0        |                  0           |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |        1        |                  0.00146484  |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      1    |        0        |                  0           |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  0.00163559  |        1 | False              |
| clip_fraction      | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |        1        |                  0.00252279  |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | AGCWD                     |   3 |               0 |      0.25 |       -1        |                 -0.0515722   |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | CLAHE                     |   3 |               0 |      0.25 |       -1        |                 -0.049901    |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | CommonGain_CLAHE          |   3 |               0 |      0.25 |       -1        |                 -0.0497096   |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | GWO_Transform             |   3 |               0 |      0.25 |        1        |                  0.0027927   |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | HE                        |   3 |               0 |      0.25 |       -1        |                 -0.0517666   |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | PSO_Transform             |   3 |               0 |      0.25 |        1        |                  0.0050527   |        1 | False              |
| runtime_sec        | SRP_CLAHE_HGPSO | Parent_HGPSO_Reproduction |   3 |               0 |      0.25 |        1        |                  0.0036346   |        1 | False              |

Effect-size orientation is normalized so positive rank-biserial values favor the proposed method according to the metric direction.

## Ablation results

_No data available._

## Optimizer stability

_No data available._

## Paired synthetic stress-test results

_No data available._

The synthetic track is a controlled stress test with a known clean target; it is not presented as a complete physical atmospheric/sensor simulator.

## Hypothesis diagnostics

```json
{
  "H1_ndvi_median_error_reduction_factor_vs_parent": 4785860.946875472,
  "H2_parent_to_proposed_median_runtime_ratio": 1.0662498633909516
}
```

## Files to use when writing the paper

- `tables/TABLE_III_main_results.csv` — primary same-data results table.
- `tables/friedman_omnibus.csv` — omnibus nonparametric tests.
- `tables/wilcoxon_holm_pairwise.csv` — corrected paired tests and rank-biserial effect sizes.
- `tables/ablation_results.csv` — parameter/component ablations.
- `tables/optimizer_stability.csv` — repeated-seed analysis.
- `tables/synthetic_paired_results.csv` — clean-reference auxiliary stress test.
- `figures/` — publication-draft plots generated from measured data.
- `raw/per_image_metrics.csv` — full per-image evidence; keep this archived.
- `manifest/run_manifest.json` — hardware/software/configuration audit.
- `PAPER_RESULTS_PAYLOAD.json` — compact machine-readable handoff for paper writing.

## Interpretation guardrails

1. A visually higher contrast result is not automatically better if spectral error or clipping increases substantially.
2. Exact normalized-ratio and spectral-angle invariance is analytical only before clipping/quantization and for valid denominators.
3. Shared gain preserves spectral direction/ratios but **not absolute radiometry**.
4. The Radiant Earth challenge chips are Sentinel-2 L2A four-band 512×512 products. Their expert cloud mask is used here instead of the SCL layer in the original draft; this dataset adaptation must be stated explicitly.
5. Do not copy cross-paper PSNR/SSIM numbers into the same-data comparison table.
6. Statistical significance should be reported together with effect size and the actual per-image distribution.
