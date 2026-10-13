from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from scipy.ndimage import uniform_filter
from skimage.metrics import structural_similarity


EPS = 1e-8


def rgb_luma(rgb: np.ndarray) -> np.ndarray:
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).astype(np.float32)


def entropy_gray(gray: np.ndarray, mask: np.ndarray) -> float:
    vals = np.clip(gray[mask] * 255.0, 0, 255).astype(np.uint8)
    if vals.size == 0:
        return float("nan")
    hist = np.bincount(vals.ravel(), minlength=256).astype(np.float64)
    p = hist[hist > 0] / hist.sum()
    return float(-(p * np.log2(p)).sum())


def local_rms_contrast(gray: np.ndarray, mask: np.ndarray, window: int = 7) -> float:
    x = gray.astype(np.float32)
    mean = uniform_filter(x, size=window, mode="reflect")
    mean2 = uniform_filter(x * x, size=window, mode="reflect")
    std = np.sqrt(np.maximum(mean2 - mean * mean, 0.0))
    vals = std[mask]
    return float(np.mean(vals)) if vals.size else float("nan")


def edge_density(gray: np.ndarray, mask: np.ndarray) -> float:
    u8 = np.clip(gray * 255, 0, 255).astype(np.uint8)
    edges = cv2.Canny(u8, 50, 150) > 0
    vals = edges[mask]
    return float(np.mean(vals)) if vals.size else float("nan")


def laplacian_variance(gray: np.ndarray, mask: np.ndarray) -> float:
    u8 = np.clip(gray * 255, 0, 255).astype(np.uint8)
    lap = cv2.Laplacian(u8, cv2.CV_32F)
    vals = lap[mask]
    return float(np.var(vals)) if vals.size else float("nan")


def ssim_masked(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float:
    a = np.clip(a.astype(np.float32), 0, 1)
    b = np.clip(b.astype(np.float32), 0, 1)
    try:
        _, sim = structural_similarity(a, b, data_range=1.0, full=True)
        vals = sim[mask]
        return float(np.mean(vals)) if vals.size else float("nan")
    except ValueError:
        return float("nan")


def mse_masked(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float:
    d = (a - b)[mask]
    return float(np.mean(d * d)) if d.size else float("nan")


def psnr_from_mse(mse: float, data_range: float = 1.0) -> float:
    if not np.isfinite(mse):
        return float("nan")
    if mse <= 0:
        return float("inf")
    return float(10 * np.log10((data_range * data_range) / mse))


def visual_metrics(original_rgb: np.ndarray, enhanced_rgb: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    go = rgb_luma(original_rgb)
    ge = rgb_luma(enhanced_rgb)
    mse = mse_masked(go, ge, mask)
    return {
        "entropy": entropy_gray(ge, mask),
        "local_rms_contrast": local_rms_contrast(ge, mask),
        "edge_density": edge_density(ge, mask),
        "laplacian_variance": laplacian_variance(ge, mask),
        "ssim_to_input": ssim_masked(go, ge, mask),
        "mse_to_input": mse,
        "psnr_to_input_db": psnr_from_mse(mse),
        "brightness_mean": float(np.mean(ge[mask])) if np.any(mask) else float("nan"),
    }


def ndvi(cube: np.ndarray) -> np.ndarray:
    # cube: B,G,R,N
    r = cube[..., 2]
    n = cube[..., 3]
    return (n - r) / (n + r + EPS)


def ndwi(cube: np.ndarray) -> np.ndarray:
    g = cube[..., 1]
    n = cube[..., 3]
    return (g - n) / (g + n + EPS)


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 3:
        return float("nan")
    sa, sb = float(np.std(a)), float(np.std(b))
    if sa < 1e-12 or sb < 1e-12:
        return 1.0 if np.allclose(a, b) else float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spectral_angle_deg(original: np.ndarray, enhanced: np.ndarray) -> np.ndarray:
    # Use float64 and snap values extremely close to one. Without this, identical
    # float32 vectors can report a small artificial angle (~0.005 degrees).
    o = original.astype(np.float64, copy=False)
    e = enhanced.astype(np.float64, copy=False)
    dot = np.sum(o * e, axis=-1)
    no = np.linalg.norm(o, axis=-1)
    ne = np.linalg.norm(e, axis=-1)
    cosv = dot / np.maximum(no * ne, EPS)
    cosv = np.clip(cosv, -1.0, 1.0)
    cosv = np.where(cosv > 1.0 - 1e-12, 1.0, cosv)
    return np.degrees(np.arccos(cosv)).astype(np.float32)


def spectral_metrics(
    original_cube: np.ndarray,
    enhanced_cube: np.ndarray,
    mask: np.ndarray,
    clip_fraction: float,
) -> dict[str, float]:
    o_ndvi = ndvi(original_cube)
    e_ndvi = ndvi(enhanced_cube)
    o_ndwi = ndwi(original_cube)
    e_ndwi = ndwi(enhanced_cube)

    v1 = mask & np.isfinite(o_ndvi) & np.isfinite(e_ndvi)
    v2 = mask & np.isfinite(o_ndwi) & np.isfinite(e_ndwi)
    d1 = e_ndvi[v1] - o_ndvi[v1]
    d2 = e_ndwi[v2] - o_ndwi[v2]

    sam = spectral_angle_deg(original_cube, enhanced_cube)
    vs = sam[mask & np.isfinite(sam)]

    return {
        "ndvi_mae": float(np.mean(np.abs(d1))) if d1.size else float("nan"),
        "ndvi_rmse": float(np.sqrt(np.mean(d1 * d1))) if d1.size else float("nan"),
        "ndvi_corr": safe_corr(o_ndvi[v1], e_ndvi[v1]),
        "ndvi_sign_flip_fraction": float(np.mean(np.signbit(o_ndvi[v1]) != np.signbit(e_ndvi[v1]))) if d1.size else float("nan"),
        "ndwi_mae": float(np.mean(np.abs(d2))) if d2.size else float("nan"),
        "ndwi_rmse": float(np.sqrt(np.mean(d2 * d2))) if d2.size else float("nan"),
        "ndwi_corr": safe_corr(o_ndwi[v2], e_ndwi[v2]),
        "ndwi_sign_flip_fraction": float(np.mean(np.signbit(o_ndwi[v2]) != np.signbit(e_ndwi[v2]))) if d2.size else float("nan"),
        "sam_mean_deg": float(np.mean(vs)) if vs.size else float("nan"),
        "sam_median_deg": float(np.median(vs)) if vs.size else float("nan"),
        "sam_p95_deg": float(np.percentile(vs, 95)) if vs.size else float("nan"),
        "clip_fraction": float(clip_fraction),
    }


def original_visual_reference(original_rgb: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    g = rgb_luma(original_rgb)
    return {
        "entropy": entropy_gray(g, mask),
        "local_rms_contrast": local_rms_contrast(g, mask),
        "edge_density": edge_density(g, mask),
        "laplacian_variance": laplacian_variance(g, mask),
        "ssim_to_input": 1.0,
        "mse_to_input": 0.0,
        "psnr_to_input_db": float("inf"),
        "brightness_mean": float(np.mean(g[mask])) if np.any(mask) else float("nan"),
    }


def bounded_quality_terms(
    original_metrics: dict[str, float],
    candidate_metrics: dict[str, float],
) -> dict[str, float]:
    """Bounded [0,1] terms used for cross-generation historical comparison.

    The paper's stated Qvis normalization is performed within each generation.
    These bounded terms are retained as an auxiliary stable utility for PSO
    personal-best bookkeeping and reporting.
    """
    def improve_ratio(k: str, cap: float = 2.0) -> float:
        o = max(float(original_metrics[k]), 1e-8)
        c = max(float(candidate_metrics[k]), 0.0)
        ratio = c / o
        return float(np.clip((ratio - 0.5) / (cap - 0.5), 0, 1))

    return {
        "entropy": float(np.clip(candidate_metrics["entropy"] / 8.0, 0, 1)),
        "contrast": improve_ratio("local_rms_contrast", cap=2.5),
        "edge": improve_ratio("edge_density", cap=2.5),
        "sharpness": improve_ratio("laplacian_variance", cap=3.0),
        "ssim": float(np.clip(candidate_metrics["ssim_to_input"], 0, 1)),
    }


def quality_utility(terms: dict[str, float], weights: dict[str, float]) -> float:
    return float(sum(float(weights[k]) * float(terms[k]) for k in weights))


def paired_clean_metrics(clean_rgb: np.ndarray, enhanced_rgb: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    gc = rgb_luma(clean_rgb)
    ge = rgb_luma(enhanced_rgb)
    mse = mse_masked(gc, ge, mask)
    return {
        "mse_to_clean": mse,
        "psnr_to_clean_db": psnr_from_mse(mse),
        "ssim_to_clean": ssim_masked(gc, ge, mask),
    }
