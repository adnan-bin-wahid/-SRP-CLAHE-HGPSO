# Troubleshooting

## The experiment is taking too long

Run `standard` first. `paper_full` intentionally includes heavy 30×100 optimizer baselines and repeated seeds.

You can stop and re-run later; completed method results are cached.

## Memory usage is high

Keep one run at a time. This suite evaluates candidate images sequentially and does not store a full image per swarm particle.

## A scene fails validation

Open `manifest/dataset_validation.csv`. Check missing B02/B03/B04/B08, mask shape, CRS/transform mismatch, or too few clear pixels.

## Proposed feasibility rate is low

Do not simply loosen constraints after looking at the test results. First inspect validation selection and clipping. Any threshold change after test inspection invalidates the frozen-test protocol and should trigger a new preregistered/frozen run.

## I changed source code/config after a partial run

Use a new output folder. Avoid mixing cached results from different implementations. `--force` only invalidates the main namespace, so a new output folder is safer for publishable runs.

## Windows PowerShell activation blocked

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```
