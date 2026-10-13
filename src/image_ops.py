from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter
from skimage import exposure


@dataclass
class TransformCache:
    clahe_v: np.ndarray
    local_mean: np.ndarray
    local_second: np.ndarray
    global_mean: float
    valid_mask: np.ndarray
    window: int


def fill_invalid(arr: np.ndarray, mask: np.ndarray, default: float = 0.0) -> np.ndarray:
    out = np.asarray(arr, dtype=np.float32).copy()
    vals = out[mask & np.isfinite(out)]
    fill = float(np.median(vals)) if vals.size else float(default)
    out[~mask | ~np.isfinite(out)] = fill
    return out


def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    rgb = np.clip(rgb.astype(np.float32), 0, 1)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)


def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    return np.clip(cv2.cvtColor(hsv.astype(np.float32), cv2.COLOR_HSV2RGB), 0, 1)


def clahe_value(v: np.ndarray, mask: np.ndarray, clip_limit: float, tile_grid=(8, 8)) -> np.ndarray:
    vf = fill_invalid(v, mask)
    h, w = vf.shape
    grid_y, grid_x = int(tile_grid[0]), int(tile_grid[1])
    kernel_size = (max(2, h // grid_y), max(2, w // grid_x))
    out = exposure.equalize_adapthist(
        np.clip(vf, 0, 1), kernel_size=kernel_size, clip_limit=float(clip_limit), nbins=256
    ).astype(np.float32)
    out[~mask] = vf[~mask]
    return out


def histogram_equalize_value(v: np.ndarray, mask: np.ndarray) -> np.ndarray:
    vf = fill_invalid(v, mask)
    u8 = np.clip(vf * 255.0, 0, 255).astype(np.uint8)
    # Equalization only on full image after filling invalid; invalid restored later.
    out = cv2.equalizeHist(u8).astype(np.float32) / 255.0
    out[~mask] = vf[~mask]
    return out


def agcwd_value(v: np.ndarray, mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Independent AGCWD implementation on V in [0,1].

    This is a classical adaptive-gamma baseline; it is not claimed to be the
    original authors' source implementation.
    """
    vf = fill_invalid(v, mask)
    u8 = np.clip(vf * 255.0, 0, 255).astype(np.uint8)
    vals = u8[mask]
    hist = np.bincount(vals.ravel(), minlength=256).astype(np.float64)
    pdf = hist / max(hist.sum(), 1.0)
    pmin, pmax = float(pdf.min()), float(pdf.max())
    if pmax <= pmin + 1e-15:
        return vf
    weighted = pmax * np.power(np.clip((pdf - pmin) / (pmax - pmin), 0, 1), alpha)
    cdf = np.cumsum(weighted)
    cdf /= max(cdf[-1], 1e-12)
    gamma = 1.0 - cdf
    x = np.linspace(0, 1, 256)
    lut = np.power(np.clip(x, 1e-6, 1.0), gamma)
    lut[0] = 0.0
    out = lut[u8].astype(np.float32)
    out[~mask] = vf[~mask]
    return np.clip(out, 0, 1)


def prepare_transform_cache(
    clahe_v: np.ndarray,
    mask: np.ndarray,
    local_window: int,
) -> TransformCache:
    if local_window < 3 or local_window % 2 == 0:
        raise ValueError("local_window must be an odd integer >= 3")
    o = fill_invalid(clahe_v, mask)
    m = uniform_filter(o, size=local_window, mode="reflect")
    e2 = uniform_filter(o * o, size=local_window, mode="reflect")
    gm = float(np.mean(o[mask])) if np.any(mask) else float(np.mean(o))
    return TransformCache(
        clahe_v=o,
        local_mean=m.astype(np.float32),
        local_second=e2.astype(np.float32),
        global_mean=max(gm, 1e-6),
        valid_mask=mask,
        window=local_window,
    )


def signed_power(x: np.ndarray, p: float) -> np.ndarray:
    return np.sign(x) * np.power(np.abs(x) + 1e-12, float(p))


def robust_rescale(
    arr: np.ndarray,
    mask: np.ndarray,
    percentiles=(1.0, 99.0),
) -> np.ndarray:
    vals = arr[mask & np.isfinite(arr)]
    if vals.size < 10:
        return np.clip(np.nan_to_num(arr), 0, 1).astype(np.float32)
    lo, hi = np.percentile(vals, percentiles)
    if hi <= lo:
        hi = lo + 1e-6
    out = (arr - lo) / (hi - lo)
    out = np.clip(np.nan_to_num(out, nan=0.0, posinf=1.0, neginf=0.0), 0, 1)
    return out.astype(np.float32)


def parent_transform(
    cache: TransformCache,
    theta: np.ndarray | list[float],
    g: float = 1.0,
    l: float = 1.0,
    rescale_percentiles=(1.0, 99.0),
) -> np.ndarray:
    """Independent implementation of the manuscript's inherited transform.

    theta = [a,b,c,k,p]. The base paper leaves several implementation details
    ambiguous; this code publishes the exact assumptions used here.
    """
    a, b, c, k, p = [float(x) for x in theta]
    o = cache.clahe_v
    m = cache.local_mean
    # Reproduction assumption following the paper's c-dependent local variance.
    var_c = cache.local_second + (c * c - 2.0 * c) * (m * m)
    sigma = np.sqrt(np.maximum(var_c, 1e-10))
    residual = o - c * m
    numerator = k * (cache.global_mean ** g)
    denom = np.power(sigma, l) + b
    e = (numerator / np.maximum(denom, 1e-8)) * signed_power(residual, p) + np.power(
        np.maximum(m, 0.0), a
    )
    out = robust_rescale(e, cache.valid_mask, rescale_percentiles)
    out[~cache.valid_mask] = o[~cache.valid_mask]
    return out


def gain_from_values(
    v_original: np.ndarray,
    v_enhanced: np.ndarray,
    mask: np.ndarray,
    epsilon: float,
    gain_min: float,
    gain_max: float,
    sigma: float = 0.0,
) -> np.ndarray:
    r = (v_enhanced + float(epsilon)) / (v_original + float(epsilon))
    r = np.clip(r, gain_min, gain_max).astype(np.float32)
    r[~mask] = 1.0
    if sigma > 0:
        # Smooth the gain while preventing invalid/cloud pixels from bleeding in.
        m = mask.astype(np.float32)
        num = gaussian_filter(r * m, sigma=sigma, mode="reflect")
        den = gaussian_filter(m, sigma=sigma, mode="reflect")
        sm = num / np.maximum(den, 1e-6)
        r = np.where(mask, sm, 1.0).astype(np.float32)
        r = np.clip(r, gain_min, gain_max)
    return r


def apply_gain_cube(
    cube: np.ndarray,
    gain: np.ndarray,
    shared_nir: bool,
    mask: np.ndarray,
    clip_range=(0.0, 1.0),
) -> tuple[np.ndarray, np.ndarray, float]:
    pre = cube.astype(np.float32).copy()
    channels = 4 if shared_nir else 3
    pre[..., :channels] *= gain[..., None]
    # If shared_nir=False, NIR is kept unchanged: this models RGB-only enhancement.
    lo, hi = clip_range
    clipping = mask[..., None] & ((pre < lo) | (pre > hi))
    clip_fraction = float(np.count_nonzero(clipping) / max(1, np.count_nonzero(mask) * 4))
    out = np.clip(pre, lo, hi).astype(np.float32)
    out[~mask] = cube[~mask]
    return out, pre, clip_fraction
