import numpy as np

from src.image_ops import apply_gain_cube
from src.metrics import spectral_metrics


def test_shared_gain_preserves_ratios_without_clipping():
    rng = np.random.default_rng(1)
    cube = rng.uniform(0.05, 0.35, size=(32, 32, 4)).astype(np.float32)
    mask = np.ones((32, 32), dtype=bool)
    gain = rng.uniform(0.8, 1.2, size=(32, 32)).astype(np.float32)
    enhanced, _, clip = apply_gain_cube(cube, gain, shared_nir=True, mask=mask)
    m = spectral_metrics(cube, enhanced, mask, clip)
    assert clip == 0.0
    assert m["ndvi_mae"] < 1e-6
    assert m["ndwi_mae"] < 1e-6
    assert m["sam_mean_deg"] < 1e-5


def test_visible_only_gain_changes_nir_ratios():
    rng = np.random.default_rng(2)
    cube = rng.uniform(0.05, 0.35, size=(32, 32, 4)).astype(np.float32)
    mask = np.ones((32, 32), dtype=bool)
    gain = np.full((32, 32), 1.3, dtype=np.float32)
    enhanced, _, clip = apply_gain_cube(cube, gain, shared_nir=False, mask=mask)
    m = spectral_metrics(cube, enhanced, mask, clip)
    assert m["ndvi_mae"] > 1e-3
    assert m["ndwi_mae"] > 1e-3
