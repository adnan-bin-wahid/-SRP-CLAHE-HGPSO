# Research Integrity Rules

1. Never fill a manuscript table from expected values, targets, or another paper's different dataset.
2. `Parent_HGPSO_Reproduction` is an independent reproduction, not author source code.
3. Keep `raw/per_image_metrics.csv` and the run manifest archived.
4. Do not describe SSIM/PSNR to the unpaired real input as restoration accuracy.
5. Clean-reference restoration metrics are only valid in the paired synthetic stress track or a genuine paired dataset.
6. Do not hide clipping when discussing spectral invariance.
7. Common gain preserves normalized ratios/direction under stated conditions; it does not preserve absolute reflectance magnitude.
8. Report the dataset adaptation: Radiant Earth L2A chips + expert cloud masks instead of raw SAFE products + SCL.
9. Validation-only configuration selection must finish before the frozen test benchmark. Do not tune from the final test outputs.
10. Report non-significant statistical findings as non-significant. Do not cherry-pick metrics.
11. Keep effect sizes with p-values.
12. Run a final novelty search before claiming priority or "first" status.
