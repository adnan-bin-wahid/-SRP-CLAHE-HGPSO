from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from .image_ops import (
    agcwd_value,
    apply_gain_cube,
    clahe_value,
    gain_from_values,
    histogram_equalize_value,
    parent_transform,
    prepare_transform_cache,
    rgb_to_hsv,
)
from .io import Scene, DisplayModel, cube_to_rgb, fit_display_model
from .metrics import (
    bounded_quality_terms,
    original_visual_reference,
    quality_utility,
    spectral_metrics,
    visual_metrics,
)
from .optimizers import Candidate, OptimizationResult, current_rank_key, gwo_only, hybrid_pso_gwo, pso_only
from .utils import stable_seed, timed_memory


@dataclass
class MethodResult:
    method: str
    chip_id: str
    metrics: dict[str, float]
    parameters: dict[str, float]
    runtime_sec: float
    peak_rss_mb: float
    evaluations_proxy: int = 0
    evaluations_full: int = 0
    iterations_run: int = 0
    stopped_early: bool = False
    feasible: bool | None = None
    violation: float | None = None
    stable_visual_utility: float | None = None
    history: list[dict[str, Any]] | None = None
    enhanced_cube: np.ndarray | None = None
    enhanced_rgb: np.ndarray | None = None
    gain: np.ndarray | None = None
    notes: str = ""


def _resize_cube(cube: np.ndarray, size: int) -> np.ndarray:
    h, w, c = cube.shape
    if max(h, w) <= size and h == w:
        return cube.copy()
    out = np.stack(
        [cv2.resize(cube[..., i], (size, size), interpolation=cv2.INTER_AREA) for i in range(c)],
        axis=-1,
    )
    return out.astype(np.float32)


def _resize_mask(mask: np.ndarray, size: int) -> np.ndarray:
    if mask.shape == (size, size):
        return mask.copy()
    return cv2.resize(mask.astype(np.uint8), (size, size), interpolation=cv2.INTER_NEAREST).astype(bool)


def _param_dict(theta: np.ndarray) -> dict[str, float]:
    names = ["a", "b", "c", "k", "p"]
    return {n: float(v) for n, v in zip(names, theta)}


def _constraint_status(spec: dict[str, float], thresholds: dict[str, float]) -> tuple[bool, float]:
    violation = 0.0
    for key in ("ndvi_mae", "ndwi_mae", "sam_mean_deg", "clip_fraction"):
        val = float(spec[key])
        thr = float(thresholds[key])
        if not np.isfinite(val):
            violation += 100.0
        elif val > thr:
            violation += (val - thr) / max(thr, 1e-12)
    return violation <= 1e-12, float(violation)


def _prepare_context(scene: Scene, cfg: dict[str, Any], proxy_size: int):
    model = fit_display_model(scene, tuple(cfg["preprocessing"]["display_percentiles"]))
    full_rgb = cube_to_rgb(scene.cube, model)

    proxy_cube = _resize_cube(scene.cube, min(proxy_size, scene.height, scene.width))
    proxy_mask = _resize_mask(scene.valid_mask, proxy_cube.shape[0])
    proxy_scene = Scene(
        chip_id=scene.chip_id,
        split=scene.split,
        cube=proxy_cube,
        valid_mask=proxy_mask,
        profile=scene.profile,
        scale_used=scene.scale_used,
        source_dir=scene.source_dir,
        cloud_fraction=scene.cloud_fraction,
        location=scene.location,
        datetime=scene.datetime,
    )
    proxy_rgb = cube_to_rgb(proxy_cube, model)

    hsv_proxy = rgb_to_hsv(proxy_rgb)
    v_proxy = hsv_proxy[..., 2]
    clahe_proxy = clahe_value(
        v_proxy,
        proxy_mask,
        cfg["preprocessing"]["clahe_clip_limit"],
        tuple(cfg["preprocessing"]["clahe_tile_grid"]),
    )
    cache_proxy = prepare_transform_cache(clahe_proxy, proxy_mask, cfg["preprocessing"]["local_window"])

    hsv_full = rgb_to_hsv(full_rgb)
    v_full = hsv_full[..., 2]
    clahe_full = clahe_value(
        v_full,
        scene.valid_mask,
        cfg["preprocessing"]["clahe_clip_limit"],
        tuple(cfg["preprocessing"]["clahe_tile_grid"]),
    )
    cache_full = prepare_transform_cache(clahe_full, scene.valid_mask, cfg["preprocessing"]["local_window"])

    orig_proxy_metrics = original_visual_reference(proxy_rgb, proxy_mask)
    orig_full_metrics = original_visual_reference(full_rgb, scene.valid_mask)
    return model, full_rgb, proxy_scene, proxy_rgb, v_proxy, cache_proxy, v_full, cache_full, orig_proxy_metrics, orig_full_metrics


def _evaluate_theta(
    theta: np.ndarray,
    cube: np.ndarray,
    mask: np.ndarray,
    model: DisplayModel,
    original_rgb: np.ndarray,
    original_v: np.ndarray,
    cache,
    orig_metrics: dict[str, float],
    cfg: dict[str, Any],
    shared_nir: bool,
    constrained: bool,
) -> tuple[Candidate, np.ndarray, np.ndarray, np.ndarray, float]:
    prep = cfg["preprocessing"]
    v_star = parent_transform(
        cache,
        theta,
        g=prep["transform_g"],
        l=prep["transform_l"],
        rescale_percentiles=tuple(prep["transform_rescale_percentiles"]),
    )
    gain = gain_from_values(
        original_v,
        v_star,
        mask,
        prep["epsilon"],
        prep["gain_min"] if shared_nir else prep.get("baseline_gain_min", 0.05),
        prep["gain_max"] if shared_nir else prep.get("baseline_gain_max", 20.0),
        prep["gain_sigma"] if shared_nir else 0.0,
    )
    enhanced_cube, _, clip_fraction = apply_gain_cube(cube, gain, shared_nir, mask)
    enhanced_rgb = cube_to_rgb(enhanced_cube, model)
    vis = visual_metrics(original_rgb, enhanced_rgb, mask)
    spec = spectral_metrics(cube, enhanced_cube, mask, clip_fraction)
    terms = bounded_quality_terms(orig_metrics, vis)
    utility = quality_utility(terms, cfg["objective"]["weights"])
    if constrained:
        feasible, violation = _constraint_status(spec, cfg["objective"]["thresholds"])
    else:
        feasible, violation = True, 0.0
    cand = Candidate(
        theta=np.asarray(theta, dtype=np.float64),
        visual_metrics=vis,
        spectral_metrics=spec,
        stable_utility=utility,
        feasible=feasible,
        violation=violation,
    )
    return cand, enhanced_cube, enhanced_rgb, gain, clip_fraction


def _full_metrics_dict(vis: dict[str, float], spec: dict[str, float]) -> dict[str, float]:
    out = dict(vis)
    out.update(spec)
    return out


def _run_simple(scene: Scene, cfg: dict[str, Any], method: str) -> MethodResult:
    model = fit_display_model(scene, tuple(cfg["preprocessing"]["display_percentiles"]))
    original_rgb = cube_to_rgb(scene.cube, model)
    hsv = rgb_to_hsv(original_rgb)
    v = hsv[..., 2]
    prep = cfg["preprocessing"]

    with timed_memory() as tm:
        if method == "Original":
            cube = scene.cube.copy()
            gain = np.ones(scene.valid_mask.shape, dtype=np.float32)
            clip_fraction = 0.0
        elif method == "HE":
            ve = histogram_equalize_value(v, scene.valid_mask)
            gain = gain_from_values(v, ve, scene.valid_mask, prep["epsilon"], prep.get("baseline_gain_min", 0.05), prep.get("baseline_gain_max", 20.0), 0.0)
            cube, _, clip_fraction = apply_gain_cube(scene.cube, gain, False, scene.valid_mask)
        elif method == "CLAHE":
            ve = clahe_value(v, scene.valid_mask, prep["clahe_clip_limit"], tuple(prep["clahe_tile_grid"]))
            gain = gain_from_values(v, ve, scene.valid_mask, prep["epsilon"], prep.get("baseline_gain_min", 0.05), prep.get("baseline_gain_max", 20.0), 0.0)
            cube, _, clip_fraction = apply_gain_cube(scene.cube, gain, False, scene.valid_mask)
        elif method == "AGCWD":
            ve = agcwd_value(v, scene.valid_mask)
            gain = gain_from_values(v, ve, scene.valid_mask, prep["epsilon"], prep.get("baseline_gain_min", 0.05), prep.get("baseline_gain_max", 20.0), 0.0)
            cube, _, clip_fraction = apply_gain_cube(scene.cube, gain, False, scene.valid_mask)
        elif method == "CommonGain_CLAHE":
            ve = clahe_value(v, scene.valid_mask, prep["clahe_clip_limit"], tuple(prep["clahe_tile_grid"]))
            gain = gain_from_values(v, ve, scene.valid_mask, prep["epsilon"], prep["gain_min"], prep["gain_max"], prep["gain_sigma"])
            cube, _, clip_fraction = apply_gain_cube(scene.cube, gain, True, scene.valid_mask)
        else:
            raise KeyError(method)

        rgb = cube_to_rgb(cube, model)
        if method == "Original":
            vis = original_visual_reference(original_rgb, scene.valid_mask)
        else:
            vis = visual_metrics(original_rgb, rgb, scene.valid_mask)
        spec = spectral_metrics(scene.cube, cube, scene.valid_mask, clip_fraction)

    return MethodResult(
        method=method,
        chip_id=scene.chip_id,
        metrics=_full_metrics_dict(vis, spec),
        parameters={},
        runtime_sec=tm["runtime_sec"],
        peak_rss_mb=tm["peak_rss_mb"],
        feasible=None,
        enhanced_cube=cube,
        enhanced_rgb=rgb,
        gain=gain,
    )


def _optimizer_call(kind: str, evaluator, cfg: dict[str, Any], population: int, generations: int, seed: int, bounds=None) -> OptimizationResult:
    bounds = cfg["bounds"] if bounds is None else bounds
    opt = cfg["optimizer"]
    kwargs = dict(
        evaluator=evaluator,
        bounds=bounds,
        population=population,
        generations=generations,
        seed=seed,
        weights=cfg["objective"]["weights"],
        patience=opt["early_stop_patience"],
        tolerance=opt["early_stop_tolerance"],
    )
    if kind == "hybrid":
        return hybrid_pso_gwo(
            **kwargs,
            pso_w=opt["pso_w"],
            pso_c1=opt["pso_c1"],
            pso_c2=opt["pso_c2"],
        )
    if kind == "pso":
        return pso_only(
            **kwargs,
            pso_w=opt["pso_w"],
            pso_c1=opt["pso_c1"],
            pso_c2=opt["pso_c2"],
        )
    if kind == "gwo":
        return gwo_only(**kwargs)
    raise KeyError(kind)


def _unique_elite_thetas(res: OptimizationResult, n: int) -> list[np.ndarray]:
    candidates = [res.best] + sorted(res.final_population, key=current_rank_key, reverse=True)
    out = []
    seen = set()
    for c in candidates:
        key = tuple(np.round(c.theta, 10))
        if key not in seen:
            out.append(c.theta.copy())
            seen.add(key)
        if len(out) >= n:
            break
    return out


def _run_optimized(
    scene: Scene,
    cfg: dict[str, Any],
    method: str,
    preset: dict[str, Any],
    base_seed: int,
    custom: dict[str, Any] | None = None,
) -> MethodResult:
    custom = custom or {}
    local_cfg = {
        **cfg,
        "preprocessing": {**cfg["preprocessing"], **custom.get("preprocessing", {})},
        "objective": {**cfg["objective"], **custom.get("objective", {})},
        "optimizer": {**cfg["optimizer"], **custom.get("optimizer", {})},
    }
    if "weights" in custom:
        local_cfg["objective"] = {**local_cfg["objective"], "weights": custom["weights"]}

    if method in ("PSO_Transform", "GWO_Transform", "Parent_HGPSO_Reproduction"):
        proxy_size = int(custom.get("proxy_size", preset["baseline_proxy_size"]))
        population = int(custom.get("population", preset["baseline_population"]))
        generations = int(custom.get("generations", preset["baseline_generations"]))
        shared_nir = False
        constrained = False
        elite_count = 1
        kind = {"PSO_Transform": "pso", "GWO_Transform": "gwo", "Parent_HGPSO_Reproduction": "hybrid"}[method]
    else:
        proxy_size = int(custom.get("proxy_size", preset["proposed_proxy_size"]))
        population = int(custom.get("population", preset["proposed_population"]))
        generations = int(custom.get("generations", preset["proposed_generations"]))
        shared_nir = True
        constrained = method != "SRP_no_constraints"
        elite_count = int(custom.get("elite_count", preset["proposed_elites"]))
        kind = "hybrid"

    bounds = {k: list(v) for k, v in cfg["bounds"].items()}
    if method == "SRP_reduced_kp":
        fixed = custom.get("fixed_abc", {"a": 0.8, "b": 0.3, "c": 0.5})
        for k in ("a", "b", "c"):
            bounds[k] = [float(fixed[k]), float(fixed[k])]

    (
        model, full_rgb, proxy_scene, proxy_rgb, v_proxy, cache_proxy,
        v_full, cache_full, orig_proxy_metrics, orig_full_metrics,
    ) = _prepare_context(scene, local_cfg, proxy_size)

    def evaluator(theta: np.ndarray) -> Candidate:
        c, *_ = _evaluate_theta(
            theta,
            proxy_scene.cube,
            proxy_scene.valid_mask,
            model,
            proxy_rgb,
            v_proxy,
            cache_proxy,
            orig_proxy_metrics,
            local_cfg,
            shared_nir=shared_nir,
            constrained=constrained,
        )
        return c

    seed = stable_seed(base_seed, scene.chip_id, method, str(custom.get("seed_tag", "main")))
    with timed_memory() as tm:
        opt_res = _optimizer_call(kind, evaluator, local_cfg, population, generations, seed, bounds=bounds)
        elite_thetas = _unique_elite_thetas(opt_res, elite_count)

        full_candidates = []
        full_payload = []
        for theta in elite_thetas:
            cand, cube, rgb, gain, _ = _evaluate_theta(
                theta,
                scene.cube,
                scene.valid_mask,
                model,
                full_rgb,
                v_full,
                cache_full,
                orig_full_metrics,
                local_cfg,
                shared_nir=shared_nir,
                constrained=constrained,
            )
            full_candidates.append(cand)
            full_payload.append((cube, rgb, gain))

        # Full-resolution final selection: feasibility first, then stable utility.
        def fkey(c: Candidate):
            return (1 if c.feasible else 0, c.stable_utility if c.feasible else -c.violation)

        best_i = max(range(len(full_candidates)), key=lambda i: fkey(full_candidates[i]))
        best = full_candidates[best_i]
        cube, rgb, gain = full_payload[best_i]

    metrics = _full_metrics_dict(best.visual_metrics, best.spectral_metrics)
    return MethodResult(
        method=method,
        chip_id=scene.chip_id,
        metrics=metrics,
        parameters=_param_dict(best.theta),
        runtime_sec=tm["runtime_sec"],
        peak_rss_mb=tm["peak_rss_mb"],
        evaluations_proxy=opt_res.evaluations,
        evaluations_full=len(elite_thetas),
        iterations_run=opt_res.iterations_run,
        stopped_early=opt_res.stopped_early,
        feasible=best.feasible if constrained else None,
        violation=best.violation if constrained else None,
        stable_visual_utility=best.stable_utility,
        history=opt_res.history,
        enhanced_cube=cube,
        enhanced_rgb=rgb,
        gain=gain,
        notes=(
            "Independent parent-style reproduction; source paper implementation details are partially underspecified."
            if method == "Parent_HGPSO_Reproduction" else ""
        ),
    )


def run_method(
    scene: Scene,
    cfg: dict[str, Any],
    method: str,
    preset: dict[str, Any],
    base_seed: int,
    custom: dict[str, Any] | None = None,
) -> MethodResult:
    if method in {"Original", "HE", "CLAHE", "AGCWD", "CommonGain_CLAHE"}:
        return _run_simple(scene, cfg, method)
    if method in {
        "PSO_Transform", "GWO_Transform", "Parent_HGPSO_Reproduction",
        "SRP_CLAHE_HGPSO", "SRP_no_constraints", "SRP_reduced_kp"
    }:
        return _run_optimized(scene, cfg, method, preset, base_seed, custom=custom)
    raise KeyError(f"Unknown method: {method}")
