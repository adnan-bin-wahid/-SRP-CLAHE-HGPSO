from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .io import Scene


def degrade_scene(scene: Scene, seed: int, mode: str = "mixed") -> Scene:
    """Create a paired synthetic stress-test scene.

    This is intentionally a controlled computational stress test, not a claim of
    a complete physical atmosphere/sensor model. The clean input remains the
    reference target, making PSNR/SSIM interpretable for this auxiliary track.
    """
    rng = np.random.default_rng(seed)
    cube = scene.cube.astype(np.float32).copy()
    h, w, _ = cube.shape
    yy, xx = np.mgrid[0:h, 0:w]

    # Smooth spatial illumination field, common to all bands.
    cx, cy = rng.uniform(0.2, 0.8) * w, rng.uniform(0.2, 0.8) * h
    sigma = rng.uniform(0.35, 0.65) * max(h, w)
    field = 0.45 + 0.35 * np.exp(-((xx-cx)**2 + (yy-cy)**2) / (2*sigma*sigma))
    field = np.clip(field, 0.35, 0.85).astype(np.float32)

    out = cube.copy()
    if mode in ("low_light", "mixed"):
        out *= field[..., None]

    if mode in ("haze", "mixed"):
        # Add low-frequency path-radiance-like term, slightly stronger in visible.
        haze = gaussian_filter(rng.normal(0, 1, (h, w)).astype(np.float32), sigma=max(8, h/20))
        haze = (haze - haze.min()) / max(float(haze.max() - haze.min()), 1e-6)
        strength = rng.uniform(0.03, 0.08)
        band_factor = np.array([1.15, 1.05, 1.0, 0.65], dtype=np.float32)
        out += strength * haze[..., None] * band_factor[None, None, :]

    if mode in ("noise", "mixed"):
        noise_sigma = rng.uniform(0.004, 0.012)
        out += rng.normal(0, noise_sigma, out.shape).astype(np.float32)

    out = np.clip(out, 0, 1)
    out[~scene.valid_mask] = scene.cube[~scene.valid_mask]
    return Scene(
        chip_id=f"{scene.chip_id}__synthetic_{mode}",
        split=scene.split,
        cube=out,
        valid_mask=scene.valid_mask.copy(),
        profile=scene.profile.copy(),
        scale_used=1.0,
        source_dir=scene.source_dir,
        cloud_fraction=scene.cloud_fraction,
        location=scene.location,
        datetime=scene.datetime,
    )
