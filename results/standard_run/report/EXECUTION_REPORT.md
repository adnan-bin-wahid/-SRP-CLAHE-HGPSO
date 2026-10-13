# SRP-CLAHE-HGPSO Execution Report

## Research-integrity status

This report contains **measured outputs from this run only**. It does not convert design targets into results. HGPSO is an independently implemented baseline with assumptions documented in `docs/METHOD_MAPPING.md`; cite the source method and describe these assumptions in the manuscript's experimental setup. PSNR/SSIM against a real degraded input are treated as fidelity/change measures, not restoration accuracy; restoration claims are reserved for the optional paired synthetic track.

## Run manifest

```json
{
  "project": "SRP-CLAHE-HGPSO",
  "preset": "standard",
  "started_unix": 1786991886.4705162,
  "dataset_root": "E:\\IIT\\8th_semester\\image\\SRP_Sentinel2_Final_240\\SRP_Sentinel2_Final_240",
  "validation_images_available": 40,
  "test_images_used": 200,
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
  "finished_unix": 1786996105.3313117,
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
    "local_window": 7,
    "transform_g": 1.0,
    "transform_l": 1.0,
    "transform_rescale_percentiles": [
      1.0,
      99.0
    ],
    "epsilon": 0.0001,
    "gain_min": 0.5,
    "gain_max": 2.0,
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
| AGCWD               | 200 | 6.7247 ± 1.3434 | 0.1005 ± 0.0468      | 0.5267 ± 0.2017 | 1.266e-01 ± 4.81e-02 | 1.265e-01 ± 4.79e-02 | 6.8120 ± 2.9435 | 7.180e-03 ± 5.07e-02 | 0.1296 ± 0.0302 |
| CLAHE               | 200 | 7.2259 ± 0.5935 | 0.1713 ± 0.0782      | 0.5357 ± 0.1372 | 1.284e-01 ± 4.79e-02 | 1.301e-01 ± 4.94e-02 | 7.0572 ± 3.0391 | 4.953e-03 ± 2.26e-02 | 0.1520 ± 0.0348 |
| Common gain + CLAHE | 200 | 7.2565 ± 0.6014 | 0.1672 ± 0.0799      | 0.5484 ± 0.1422 | 4.142e-05 ± 2.98e-04 | 9.619e-05 ± 7.16e-04 | 0.0115 ± 0.1002 | 2.885e-03 ± 2.19e-02 | 0.1509 ± 0.0367 |
| GWO                 | 200 | 7.2719 ± 0.5061 | 0.2205 ± 0.0819      | 0.4183 ± 0.1300 | 1.556e-01 ± 8.62e-02 | 1.574e-01 ± 8.92e-02 | 8.4825 ± 5.0318 | 3.548e-03 ± 1.48e-02 | 3.6149 ± 1.2673 |
| HE                  | 200 | 6.8458 ± 0.8177 | 0.1498 ± 0.0717      | 0.4990 ± 0.2149 | 1.641e-01 ± 1.21e-01 | 1.645e-01 ± 1.25e-01 | 8.8581 ± 6.6294 | 2.977e-03 ± 1.96e-02 | 0.1265 ± 0.0280 |
| Original            | 200 | 7.4448 ± 0.4701 | 0.0839 ± 0.0423      | 1.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.000e+00 ± 0.00e+00 | 0.0000 ± 0.0000 | 0.000e+00 ± 0.00e+00 | 0.0816 ± 0.0182 |
| PSO                 | 200 | 7.3159 ± 0.4813 | 0.2117 ± 0.0856      | 0.4385 ± 0.1232 | 1.486e-01 ± 8.71e-02 | 1.505e-01 ± 9.20e-02 | 8.1494 ± 5.1467 | 3.333e-03 ± 1.55e-02 | 5.0318 ± 1.5641 |
| HGPSO               | 200 | 7.3120 ± 0.5140 | 0.2168 ± 0.0824      | 0.4255 ± 0.1286 | 1.505e-01 ± 7.50e-02 | 1.523e-01 ± 7.67e-02 | 8.2245 ± 4.3211 | 3.316e-03 ± 1.50e-02 | 3.9063 ± 1.4812 |
| Proposed SRP-HGPSO  | 200 | 7.2264 ± 0.5999 | 0.2231 ± 0.0941      | 0.4292 ± 0.1260 | 1.948e-05 ± 9.94e-05 | 5.267e-05 ± 3.29e-04 | 0.0053 ± 0.0374 | 1.391e-03 ± 8.34e-03 | 2.8051 ± 0.7788 |

The columns `ssim_to_input` and any input-referenced PSNR/MSE quantify similarity/change relative to the real input. They are **not** clean-reference restoration metrics.

## Friedman omnibus tests

| metric             |   n |   methods |   friedman_stat |      p_value | significant   |
|:-------------------|----:|----------:|----------------:|-------------:|:--------------|
| entropy            | 200 |         8 |         201.675 | 5.07188e-40  | True          |
| local_rms_contrast | 200 |         8 |         805.202 | 1.39952e-169 | True          |
| ssim_to_input      | 200 |         8 |         306.448 | 2.5381e-62   | True          |
| ndvi_mae           | 200 |         8 |         839.452 | 5.673e-177   | True          |
| ndwi_mae           | 200 |         8 |         845.238 | 3.19665e-178 | True          |
| sam_mean_deg       | 200 |         8 |         863.898 | 2.9959e-182  | True          |
| clip_fraction      | 200 |         8 |         331.975 | 8.86575e-68  | True          |
| runtime_sec        | 200 |         8 |        1287.52  | 8.34808e-274 | True          |

## Proposed-vs-baseline Wilcoxon tests with Holm correction

| metric             | proposed           | baseline            |   n |   wilcoxon_stat |     p_value |   rank_biserial |   median_oriented_difference |      p_holm | significant_holm   |
|:-------------------|:-------------------|:--------------------|----:|----------------:|------------:|----------------:|-----------------------------:|------------:|:-------------------|
| entropy            | Proposed SRP-HGPSO | AGCWD               | 200 |            4681 | 5.71172e-11 |      0.534229   |                  0.153591    | 3.42703e-10 | True               |
| entropy            | Proposed SRP-HGPSO | CLAHE               | 200 |            9374 | 0.409465    |      0.0672637  |                  0.0191539   | 0.81893     | False              |
| entropy            | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |            9106 | 0.249387    |     -0.0939303  |                 -0.0231132   | 0.74816     | False              |
| entropy            | Proposed SRP-HGPSO | GWO                 | 200 |            9889 | 0.84426     |     -0.0160199  |                  0.0120132   | 0.84426     | False              |
| entropy            | Proposed SRP-HGPSO | HE                  | 200 |            3722 | 1.15206e-14 |      0.629652   |                  0.267137    | 8.06443e-14 | True               |
| entropy            | Proposed SRP-HGPSO | PSO                 | 200 |            8141 | 0.0198429   |     -0.18995    |                 -0.0129849   | 0.0992146   | False              |
| entropy            | Proposed SRP-HGPSO | HGPSO               | 200 |            8329 | 0.0357365   |     -0.171244   |                 -0.0170091   | 0.142946    | False              |
| local_rms_contrast | Proposed SRP-HGPSO | AGCWD               | 200 |              47 | 2.9101e-34  |      0.995323   |                  0.125292    | 2.03707e-33 | True               |
| local_rms_contrast | Proposed SRP-HGPSO | CLAHE               | 200 |             662 | 2.22072e-30 |      0.934129   |                  0.0486359   | 1.11036e-29 | True               |
| local_rms_contrast | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |             487 | 1.84677e-31 |      0.951542   |                  0.0524478   | 1.10806e-30 | True               |
| local_rms_contrast | Proposed SRP-HGPSO | GWO                 | 200 |            9883 | 0.838534    |     -0.0166169  |                 -0.0016144   | 1           | False              |
| local_rms_contrast | Proposed SRP-HGPSO | HE                  | 200 |             797 | 1.46645e-29 |      0.920697   |                  0.0769509   | 5.86578e-29 | True               |
| local_rms_contrast | Proposed SRP-HGPSO | PSO                 | 200 |            6835 | 8.75087e-05 |      0.3199     |                  0.00555777  | 0.000262526 | True               |
| local_rms_contrast | Proposed SRP-HGPSO | HGPSO               | 200 |            9509 | 0.509182    |      0.0538806  |                 -0.00072147  | 1           | False              |
| ssim_to_input      | Proposed SRP-HGPSO | AGCWD               | 200 |            4304 | 2.36455e-12 |     -0.571741   |                 -0.0993089   | 1.18228e-11 | True               |
| ssim_to_input      | Proposed SRP-HGPSO | CLAHE               | 200 |            1468 | 1.16777e-25 |     -0.85393    |                 -0.0951515   | 7.00662e-25 | True               |
| ssim_to_input      | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |            1129 | 1.35693e-27 |     -0.887662   |                 -0.104465    | 9.49849e-27 | True               |
| ssim_to_input      | Proposed SRP-HGPSO | GWO                 | 200 |            9962 | 0.914492    |      0.00875622 |                 -0.00319684  | 0.914492    | False              |
| ssim_to_input      | Proposed SRP-HGPSO | HE                  | 200 |            5774 | 1.81405e-07 |     -0.425473   |                 -0.0690532   | 7.25622e-07 | True               |
| ssim_to_input      | Proposed SRP-HGPSO | PSO                 | 200 |            6947 | 0.000152976 |     -0.308756   |                 -0.0144497   | 0.000458928 | True               |
| ssim_to_input      | Proposed SRP-HGPSO | HGPSO               | 200 |            9178 | 0.287334    |     -0.0867662  |                 -0.00206733  | 0.574668    | False              |
| ndvi_mae           | Proposed SRP-HGPSO | AGCWD               | 200 |               0 | 1.43615e-34 |      1          |                  0.120494    | 1.0053e-33  | True               |
| ndvi_mae           | Proposed SRP-HGPSO | CLAHE               | 200 |               0 | 1.43615e-34 |      1          |                  0.124122    | 1.0053e-33  | True               |
| ndvi_mae           | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |            9781 | 0.742741    |     -0.0459701  |                  4.023e-12   | 0.742741    | False              |
| ndvi_mae           | Proposed SRP-HGPSO | GWO                 | 200 |               0 | 1.43615e-34 |      1          |                  0.13896     | 1.0053e-33  | True               |
| ndvi_mae           | Proposed SRP-HGPSO | HE                  | 200 |               0 | 1.43615e-34 |      1          |                  0.131009    | 1.0053e-33  | True               |
| ndvi_mae           | Proposed SRP-HGPSO | PSO                 | 200 |               0 | 1.43615e-34 |      1          |                  0.136435    | 1.0053e-33  | True               |
| ndvi_mae           | Proposed SRP-HGPSO | HGPSO               | 200 |               0 | 1.43615e-34 |      1          |                  0.136304    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | AGCWD               | 200 |               0 | 1.43615e-34 |      1          |                  0.117136    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | CLAHE               | 200 |               0 | 1.43615e-34 |      1          |                  0.119672    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |            9755 | 0.718884    |     -0.0446766  |                  1.18181e-11 | 0.718884    | False              |
| ndwi_mae           | Proposed SRP-HGPSO | GWO                 | 200 |               0 | 1.43615e-34 |      1          |                  0.138599    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | HE                  | 200 |               0 | 1.43615e-34 |      1          |                  0.128223    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | PSO                 | 200 |               0 | 1.43615e-34 |      1          |                  0.134726    | 1.0053e-33  | True               |
| ndwi_mae           | Proposed SRP-HGPSO | HGPSO               | 200 |               0 | 1.43615e-34 |      1          |                  0.135226    | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | AGCWD               | 200 |               0 | 1.43615e-34 |      1          |                  6.65164     | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | CLAHE               | 200 |               0 | 1.43615e-34 |      1          |                  6.89439     | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |             739 | 0.27046     |      0.164972   |                  0           | 0.27046     | False              |
| sam_mean_deg       | Proposed SRP-HGPSO | GWO                 | 200 |               0 | 1.43615e-34 |      1          |                  7.64964     | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | HE                  | 200 |               0 | 1.43615e-34 |      1          |                  7.02247     | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | PSO                 | 200 |               0 | 1.43615e-34 |      1          |                  7.5438      | 1.0053e-33  | True               |
| sam_mean_deg       | Proposed SRP-HGPSO | HGPSO               | 200 |               0 | 1.43615e-34 |      1          |                  7.60298     | 1.0053e-33  | True               |
| clip_fraction      | Proposed SRP-HGPSO | AGCWD               | 200 |             759 | 0.180374    |     -0.197779   |                  0           | 0.51362     | False              |
| clip_fraction      | Proposed SRP-HGPSO | CLAHE               | 200 |             734 | 2.47943e-17 |      0.840087   |                  0.000101882 | 1.7356e-16  | True               |
| clip_fraction      | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |             683 | 0.348201    |      0.143484   |                  0           | 0.51362     | False              |
| clip_fraction      | Proposed SRP-HGPSO | GWO                 | 200 |             968 | 6.73588e-16 |      0.795197   |                  4.71528e-05 | 4.04153e-15 | True               |
| clip_fraction      | Proposed SRP-HGPSO | HE                  | 200 |             755 | 0.171207    |     -0.20201    |                  0           | 0.51362     | False              |
| clip_fraction      | Proposed SRP-HGPSO | PSO                 | 200 |             988 | 4.17929e-15 |      0.781647   |                  2.97174e-05 | 2.08964e-14 | True               |
| clip_fraction      | Proposed SRP-HGPSO | HGPSO               | 200 |            1151 | 2.58005e-14 |      0.752898   |                  1.43051e-05 | 1.03202e-13 | True               |
| runtime_sec        | Proposed SRP-HGPSO | AGCWD               | 200 |               0 | 1.43615e-34 |     -1          |                 -2.21033     | 1.0053e-33  | True               |
| runtime_sec        | Proposed SRP-HGPSO | CLAHE               | 200 |               0 | 1.43615e-34 |     -1          |                 -2.19012     | 1.0053e-33  | True               |
| runtime_sec        | Proposed SRP-HGPSO | Common gain + CLAHE | 200 |               0 | 1.43615e-34 |     -1          |                 -2.19494     | 1.0053e-33  | True               |
| runtime_sec        | Proposed SRP-HGPSO | GWO                 | 200 |            2228 | 1.372e-21   |      0.778308   |                  0.677179    | 1.372e-21   | True               |
| runtime_sec        | Proposed SRP-HGPSO | HE                  | 200 |               0 | 1.43615e-34 |     -1          |                 -2.21289     | 1.0053e-33  | True               |
| runtime_sec        | Proposed SRP-HGPSO | PSO                 | 200 |               7 | 1.59576e-34 |      0.999303   |                  1.91726     | 1.0053e-33  | True               |
| runtime_sec        | Proposed SRP-HGPSO | HGPSO               | 200 |            1226 | 4.93967e-27 |      0.87801    |                  0.859609    | 9.87934e-27 | True               |

Effect-size orientation is normalized so positive rank-biserial values favor the proposed method according to the metric direction.

## Ablation results

| ablation                      |   n |   stable_visual_utility_median |   stable_visual_utility_mean |   entropy_median |   entropy_mean |   local_rms_contrast_median |   local_rms_contrast_mean |   ndvi_mae_median |   ndvi_mae_mean |   ndwi_mae_median |   ndwi_mae_mean |   sam_mean_deg_median |   sam_mean_deg_mean |   clip_fraction_median |   clip_fraction_mean |   runtime_sec_median |   runtime_sec_mean |   pixel_equivalent_evaluations_median |   pixel_equivalent_evaluations_mean |   feasible_rate |
|:------------------------------|----:|-------------------------------:|-----------------------------:|-----------------:|---------------:|----------------------------:|--------------------------:|------------------:|----------------:|------------------:|----------------:|----------------------:|--------------------:|-----------------------:|---------------------:|---------------------:|-------------------:|--------------------------------------:|------------------------------------:|----------------:|
| A3_no_constraints             |   8 |                       0.763445 |                     0.756792 |          7.1863  |        6.89568 |                    0.233631 |                  0.236959 |       4.1817e-08  |     8.07128e-08 |       3.9378e-08  |     8.23476e-08 |                     0 |         2.73836e-06 |                      0 |          1.31155e-06 |             2.22665  |           2.18161  |                                 28    |                             27.25   |             nan |
| A4_gain_sigma_0.0             |   8 |                       0.737029 |                     0.753696 |          7.10107 |        6.80437 |                    0.298628 |                  0.258407 |       4.50978e-08 |     8.21123e-08 |       3.84815e-08 |     8.22085e-08 |                     0 |         2.73274e-06 |                      0 |          1.19258e-06 |             2.1966   |           2.16553  |                                 28    |                             27.25   |               1 |
| A4_gain_sigma_0.5             |   8 |                       0.754624 |                     0.75359  |          7.3875  |        6.87795 |                    0.233329 |                  0.240971 |       4.63947e-08 |     4.59064e-08 |       3.97664e-08 |     4.53087e-08 |                     0 |         6.45094e-07 |                      0 |          4.77324e-07 |             2.38259  |           2.37239  |                                 28    |                             27.75   |               1 |
| A4_gain_sigma_1.0             |   8 |                       0.649363 |                     0.691275 |          7.60403 |        7.21834 |                    0.203943 |                  0.198381 |       3.33032e-08 |     4.01712e-08 |       3.52608e-08 |     3.80447e-08 |                     0 |         4.85136e-07 |                      0 |          2.38419e-07 |             2.43801  |           2.60078  |                                 28    |                             28      |               1 |
| A4_gain_sigma_2.0             |   8 |                       0.562196 |                     0.598794 |          7.67841 |        7.43468 |                    0.130826 |                  0.135421 |       1.85291e-08 |     3.39562e-08 |       2.41659e-08 |     3.08582e-08 |                     0 |         0           |                      0 |          0           |             2.485    |           2.56049  |                                 28    |                             26.5    |               1 |
| A5_gain_0.4_2.5               |   8 |                       0.75671  |                     0.758467 |          7.20427 |        7.14379 |                    0.219715 |                  0.217123 |       4.72608e-08 |     8.39459e-06 |       4.0377e-08  |     8.8302e-06  |                     0 |         0.000542376 |                      0 |          0.00016096  |             2.26009  |           2.38712  |                                 28    |                             27      |               1 |
| A5_gain_0.5_2.0               |   8 |                       0.752381 |                     0.757427 |          7.20641 |        6.98335 |                    0.227366 |                  0.227125 |       4.19308e-08 |     7.72421e-08 |       3.845e-08   |     7.75491e-08 |                     0 |         2.41251e-06 |                      0 |          9.53918e-07 |             2.24173  |           2.32826  |                                 28    |                             26.75   |               1 |
| A5_gain_0.7_1.5               |   8 |                       0.769048 |                     0.7588   |          7.5303  |        7.21244 |                    0.240581 |                  0.226747 |       1.94761e-08 |     3.34714e-08 |       2.41866e-08 |     3.15123e-08 |                     0 |         0           |                      0 |          0           |             2.27359  |           2.36829  |                                 28    |                             27      |               1 |
| A6_proxy_128                  |   8 |                       0.760369 |                     0.742544 |          7.16597 |        6.68368 |                    0.256047 |                  0.254992 |       4.32738e-08 |     7.88249e-08 |       3.67697e-08 |     7.92722e-08 |                     0 |         2.49741e-06 |                      0 |          1.07337e-06 |             0.852664 |           0.904321 |                                  9.25 |                              9.4375 |               1 |
| A6_proxy_256                  |   8 |                       0.754718 |                     0.755026 |          7.26426 |        6.84715 |                    0.268464 |                  0.240109 |       4.58848e-08 |     8.10264e-08 |       3.94318e-08 |     8.12178e-08 |                     0 |         2.62116e-06 |                      0 |          1.19258e-06 |             2.13184  |           2.21484  |                                 26    |                             25.25   |               1 |
| A6_proxy_512                  |   8 |                       0.763168 |                     0.765341 |          7.18714 |        7.15596 |                    0.185455 |                  0.212679 |       3.18445e-08 |     7.30401e-08 |       3.37271e-08 |     7.24341e-08 |                     0 |         2.19316e-06 |                      0 |          8.34465e-07 |            11.0975   |          11.3611   |                                100    |                             97      |               1 |
| A7_budget_12x30               |   8 |                       0.7549   |                     0.758299 |          7.17749 |        6.94832 |                    0.236203 |                  0.230987 |       4.5177e-08  |     7.87295e-08 |       3.87053e-08 |     7.9139e-08  |                     0 |         2.49741e-06 |                      0 |          1.07337e-06 |             3.52903  |           3.79768  |                                 43    |                             49.375  |               1 |
| A7_budget_16x50               |   8 |                       0.737087 |                     0.753617 |          7.17816 |        7.06384 |                    0.251528 |                  0.222237 |       4.58547e-08 |     1.11422e-07 |       3.90174e-08 |     1.12579e-07 |                     0 |         4.62161e-06 |                      0 |          2.26546e-06 |             3.91713  |           4.08642  |                                 52    |                             53.5    |               1 |
| A7_budget_30x100              |   8 |                       0.758466 |                     0.761368 |          7.39056 |        7.14572 |                    0.238917 |                  0.221179 |       3.21759e-08 |     1.09258e-07 |       3.42714e-08 |     1.10449e-07 |                     0 |         4.57147e-06 |                      0 |          2.14577e-06 |             7.88692  |           7.78565  |                                105.25 |                            103.375  |               1 |
| A7_budget_8x20                |   8 |                       0.751712 |                     0.755722 |          7.24755 |        7.0139  |                    0.213799 |                  0.219977 |       3.19364e-08 |     1.04158e-07 |       3.41647e-08 |     1.06282e-07 |                     0 |         4.30471e-06 |                      0 |          1.90735e-06 |             2.48731  |           2.65098  |                                 31    |                             33.25   |               1 |
| A8_reduced_kp                 |   8 |                       0.740855 |                     0.745847 |          7.24753 |        6.87543 |                    0.214951 |                  0.230818 |       4.60009e-08 |     1.17074e-07 |       3.82882e-08 |     1.19407e-07 |                     0 |         5.06659e-06 |                      0 |          2.62309e-06 |             2.1797   |           2.09578  |                                 27    |                             26      |               1 |
| A9_weights_contrast_emphasis  |   8 |                       0.741979 |                     0.748678 |          7.25497 |        7.15882 |                    0.186213 |                  0.205259 |       4.54227e-08 |     1.09992e-07 |       3.82726e-08 |     1.11335e-07 |                     0 |         4.60897e-06 |                      0 |          2.14625e-06 |             2.20386  |           2.15678  |                                 28    |                             26.75   |               1 |
| A9_weights_default            |   8 |                       0.752329 |                     0.75247  |          7.41078 |        7.10587 |                    0.226581 |                  0.224878 |       4.20876e-08 |     8.16063e-08 |       3.93613e-08 |     8.11872e-08 |                     0 |         2.72385e-06 |                      0 |          1.19258e-06 |             2.20384  |           2.16354  |                                 28    |                             27      |               1 |
| A9_weights_entropy_emphasis   |   8 |                       0.755858 |                     0.747953 |          7.42596 |        7.22018 |                    0.240127 |                  0.206888 |       4.62106e-08 |     7.89402e-08 |       3.89822e-08 |     7.86875e-08 |                     0 |         2.49741e-06 |                      0 |          1.07337e-06 |             2.20756  |           2.15318  |                                 28    |                             27.25   |               1 |
| A9_weights_structure_emphasis |   8 |                       0.669902 |                     0.663538 |          7.37496 |        6.94182 |                    0.19807  |                  0.207981 |       4.50899e-08 |     4.40733e-08 |       3.85447e-08 |     4.13652e-08 |                     0 |         6.01465e-07 |                      0 |          4.77324e-07 |             2.08762  |           2.07096  |                                 26    |                             25.75   |               1 |

## Optimizer stability

| method             |   images |   seeds |   stable_visual_utility_mean |   stable_visual_utility_std |   stable_visual_utility_cv |   ndvi_mae_mean |   ndvi_mae_std |   ndvi_mae_cv |   ndwi_mae_mean |   ndwi_mae_std |   ndwi_mae_cv |   sam_mean_deg_mean |   sam_mean_deg_std |   sam_mean_deg_cv |   runtime_sec_mean |   runtime_sec_std |   runtime_sec_cv |
|:-------------------|---------:|--------:|-----------------------------:|----------------------------:|---------------------------:|----------------:|---------------:|--------------:|----------------:|---------------:|--------------:|--------------------:|-------------------:|------------------:|-------------------:|------------------:|-----------------:|
| HGPSO              |        8 |       3 |                     0.748854 |                   0.0787232 |                   0.105125 |     0.121849    |    0.0548314   |      0.449994 |     0.127799    |    0.0500097   |      0.391315 |         6.84087     |        2.63218     |          0.384772 |            3.13874 |          0.703094 |        0.224005  |
| Proposed SRP-HGPSO |        8 |       3 |                     0.754584 |                   0.0819035 |                   0.108541 |     7.40541e-08 |    1.14668e-07 |      1.54844  |     7.40753e-08 |    1.18527e-07 |      1.60009  |         2.23563e-06 |        7.38414e-06 |          3.30294  |            2.03772 |          0.201971 |        0.0991159 |

## Paired synthetic stress-test results

| method             |   n |   psnr_to_clean_db_mean |   psnr_to_clean_db_std |   psnr_to_clean_db_median |   psnr_to_clean_db_q1 |   psnr_to_clean_db_q3 |   ssim_to_clean_mean |   ssim_to_clean_std |   ssim_to_clean_median |   ssim_to_clean_q1 |   ssim_to_clean_q3 |   runtime_sec_mean |   runtime_sec_std |   runtime_sec_median |   runtime_sec_q1 |   runtime_sec_q3 |
|:-------------------|----:|------------------------:|-----------------------:|--------------------------:|----------------------:|----------------------:|---------------------:|--------------------:|-----------------------:|-------------------:|-------------------:|-------------------:|------------------:|---------------------:|-----------------:|-----------------:|
| CLAHE              |  12 |                 9.81889 |                2.97925 |                  10.0971  |               7.90671 |               11.2222 |             0.35172  |            0.163047 |               0.371276 |           0.252119 |           0.462868 |          0.124294  |        0.00707641 |            0.122982  |        0.119825  |        0.12648   |
| Original           |  12 |                12.1424  |                4.74976 |                  12.2768  |               9.21256 |               14.8249 |             0.518348 |            0.222951 |               0.539454 |           0.373437 |           0.678207 |          0.0638628 |        0.00323614 |            0.0644251 |        0.0618471 |        0.0662796 |
| HGPSO              |  12 |                 9.21228 |                2.13979 |                   9.99539 |               8.10682 |               10.4389 |             0.292985 |            0.113083 |               0.313074 |           0.232078 |           0.358724 |          2.91111   |        0.653668   |            2.61124   |        2.46433   |        3.27664   |
| Proposed SRP-HGPSO |  12 |                 9.38991 |                3.08187 |                   9.06424 |               8.21171 |               10.0534 |             0.288382 |            0.128201 |               0.291659 |           0.19487  |           0.374469 |          2.13787   |        0.136622   |            2.18644   |        2.09998   |        2.2111    |

The synthetic track is a controlled stress test with a known clean target; it is not presented as a complete physical atmospheric/sensor simulator.

## Hypothesis diagnostics

```json
{
  "H1_ndvi_median_error_reduction_factor_vs_parent": 4313510.752890114,
  "H2_parent_to_proposed_median_runtime_ratio": 1.373207774203236
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
