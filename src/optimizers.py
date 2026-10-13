from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any

import numpy as np


PARAM_NAMES = ("a", "b", "c", "k", "p")


@dataclass
class Candidate:
    theta: np.ndarray
    visual_metrics: dict[str, float]
    spectral_metrics: dict[str, float]
    stable_utility: float
    feasible: bool
    violation: float
    qvis: float = 0.0
    generation: int = 0

    def copy(self) -> "Candidate":
        return Candidate(
            theta=self.theta.copy(),
            visual_metrics=dict(self.visual_metrics),
            spectral_metrics=dict(self.spectral_metrics),
            stable_utility=float(self.stable_utility),
            feasible=bool(self.feasible),
            violation=float(self.violation),
            qvis=float(self.qvis),
            generation=int(self.generation),
        )


@dataclass
class OptimizationResult:
    best: Candidate
    history: list[dict[str, Any]]
    final_population: list[Candidate]
    evaluations: int
    iterations_run: int
    stopped_early: bool


def bounds_arrays(bounds: dict[str, list[float]]) -> tuple[np.ndarray, np.ndarray]:
    lo = np.array([bounds[k][0] for k in PARAM_NAMES], dtype=np.float64)
    hi = np.array([bounds[k][1] for k in PARAM_NAMES], dtype=np.float64)
    return lo, hi


def _robust01(vals: np.ndarray) -> np.ndarray:
    vals = np.asarray(vals, dtype=float)
    finite = np.isfinite(vals)
    if finite.sum() == 0:
        return np.zeros_like(vals)
    good = vals[finite]
    lo, hi = np.percentile(good, [10, 90]) if good.size >= 4 else (np.min(good), np.max(good))
    if hi <= lo + 1e-12:
        out = np.full_like(vals, 0.5)
    else:
        out = (vals - lo) / (hi - lo)
        out = np.clip(out, 0, 1)
    out[~finite] = 0.0
    return out


def assign_generation_qvis(pop: list[Candidate], weights: dict[str, float]) -> None:
    if not pop:
        return
    # First four use robust within-generation normalization per manuscript draft.
    mapping = {
        "entropy": "entropy",
        "contrast": "local_rms_contrast",
        "edge": "edge_density",
        "sharpness": "laplacian_variance",
    }
    normed: dict[str, np.ndarray] = {}
    for term, metric in mapping.items():
        normed[term] = _robust01(np.array([c.visual_metrics.get(metric, np.nan) for c in pop]))
    ssim = np.clip(np.array([c.visual_metrics.get("ssim_to_input", 0.0) for c in pop], dtype=float), 0, 1)

    for i, c in enumerate(pop):
        c.qvis = float(
            weights["entropy"] * normed["entropy"][i]
            + weights["contrast"] * normed["contrast"][i]
            + weights["edge"] * normed["edge"][i]
            + weights["sharpness"] * normed["sharpness"][i]
            + weights["ssim"] * ssim[i]
        )


def current_rank_key(c: Candidate) -> tuple[float, float, float]:
    # Feasibility-first: feasible > infeasible; then Qvis or smaller violation.
    if c.feasible:
        return (1.0, c.qvis, c.stable_utility)
    return (0.0, -c.violation, c.stable_utility)


def historical_better(a: Candidate, b: Candidate | None) -> bool:
    if b is None:
        return True
    if a.feasible != b.feasible:
        return a.feasible
    if a.feasible:
        return a.stable_utility > b.stable_utility
    if abs(a.violation - b.violation) > 1e-12:
        return a.violation < b.violation
    return a.stable_utility > b.stable_utility


def evaluate_population(
    positions: np.ndarray,
    evaluator: Callable[[np.ndarray], Candidate],
    generation: int,
    weights: dict[str, float],
) -> list[Candidate]:
    pop = []
    for x in positions:
        c = evaluator(x)
        c.generation = generation
        pop.append(c)
    assign_generation_qvis(pop, weights)
    return pop


def _leader_positions(pop: list[Candidate], count: int = 3) -> list[np.ndarray]:
    ranked = sorted(pop, key=current_rank_key, reverse=True)
    if len(ranked) < count:
        ranked = ranked + [ranked[-1]] * (count - len(ranked))
    return [ranked[i].theta.copy() for i in range(count)]


def hybrid_pso_gwo(
    evaluator: Callable[[np.ndarray], Candidate],
    bounds: dict[str, list[float]],
    population: int,
    generations: int,
    seed: int,
    weights: dict[str, float],
    pso_w: float = 0.729,
    pso_c1: float = 1.49445,
    pso_c2: float = 1.49445,
    patience: int = 8,
    tolerance: float = 1e-4,
) -> OptimizationResult:
    rng = np.random.default_rng(seed)
    lo, hi = bounds_arrays(bounds)
    span = hi - lo
    pos = rng.uniform(lo, hi, size=(population, len(lo)))
    vel = rng.uniform(-0.1 * span, 0.1 * span, size=pos.shape)

    pbest: list[Candidate | None] = [None] * population
    history = []
    evaluations = 0
    best_hist: Candidate | None = None
    stagnant = 0
    stopped = False
    last_improvement_score = -np.inf
    final_pop: list[Candidate] = []

    for gen in range(generations):
        pop = evaluate_population(pos, evaluator, gen, weights)
        evaluations += len(pop)
        final_pop = pop

        for i, c in enumerate(pop):
            if historical_better(c, pbest[i]):
                pbest[i] = c.copy()
            if historical_better(c, best_hist):
                best_hist = c.copy()

        leaders = _leader_positions(pop, 3)
        alpha, beta, delta = leaders

        # Current progress is tracked by a stable cross-generation utility.
        if best_hist is not None:
            score = best_hist.stable_utility if best_hist.feasible else -best_hist.violation
        else:
            score = -np.inf
        improvement = score - last_improvement_score
        if improvement > tolerance:
            stagnant = 0
            last_improvement_score = score
        else:
            stagnant += 1

        ranked = sorted(pop, key=current_rank_key, reverse=True)
        history.append({
            "generation": gen + 1,
            "best_qvis_generation": ranked[0].qvis,
            "best_stable_utility": None if best_hist is None else best_hist.stable_utility,
            "best_feasible": None if best_hist is None else best_hist.feasible,
            "best_violation": None if best_hist is None else best_hist.violation,
            "feasible_fraction": float(np.mean([c.feasible for c in pop])),
        })

        if gen + 1 >= max(4, patience) and stagnant >= patience:
            stopped = True
            break

        # PSO exploration.
        pbest_pos = np.stack([p.theta if p is not None else pos[i] for i, p in enumerate(pbest)])
        gbest = best_hist.theta if best_hist is not None else alpha
        r1 = rng.random(pos.shape)
        r2 = rng.random(pos.shape)
        vel = pso_w * vel + pso_c1 * r1 * (pbest_pos - pos) + pso_c2 * r2 * (gbest - pos)
        pso_pos = np.clip(pos + vel, lo, hi)

        # GWO refinement applied after the PSO step, using current alpha/beta/delta.
        acoef = 2.0 - 2.0 * (gen / max(generations - 1, 1))
        x_accum = []
        for leader in (alpha, beta, delta):
            r1g = rng.random(pos.shape)
            r2g = rng.random(pos.shape)
            A = 2.0 * acoef * r1g - acoef
            C = 2.0 * r2g
            D = np.abs(C * leader[None, :] - pso_pos)
            X = leader[None, :] - A * D
            x_accum.append(X)
        pos = np.clip(sum(x_accum) / 3.0, lo, hi)

    assert best_hist is not None
    return OptimizationResult(
        best=best_hist,
        history=history,
        final_population=final_pop,
        evaluations=evaluations,
        iterations_run=len(history),
        stopped_early=stopped,
    )


def pso_only(
    evaluator: Callable[[np.ndarray], Candidate],
    bounds: dict[str, list[float]],
    population: int,
    generations: int,
    seed: int,
    weights: dict[str, float],
    pso_w: float = 0.729,
    pso_c1: float = 1.49445,
    pso_c2: float = 1.49445,
    patience: int = 8,
    tolerance: float = 1e-4,
) -> OptimizationResult:
    rng = np.random.default_rng(seed)
    lo, hi = bounds_arrays(bounds)
    span = hi - lo
    pos = rng.uniform(lo, hi, size=(population, len(lo)))
    vel = rng.uniform(-0.1 * span, 0.1 * span, size=pos.shape)
    pbest: list[Candidate | None] = [None] * population
    best_hist: Candidate | None = None
    history = []
    evaluations = 0
    stagnant = 0
    last = -np.inf
    stopped = False
    final_pop: list[Candidate] = []

    for gen in range(generations):
        pop = evaluate_population(pos, evaluator, gen, weights)
        evaluations += len(pop)
        final_pop = pop
        for i, c in enumerate(pop):
            if historical_better(c, pbest[i]):
                pbest[i] = c.copy()
            if historical_better(c, best_hist):
                best_hist = c.copy()
        assert best_hist is not None
        score = best_hist.stable_utility if best_hist.feasible else -best_hist.violation
        if score - last > tolerance:
            last = score
            stagnant = 0
        else:
            stagnant += 1
        ranked = sorted(pop, key=current_rank_key, reverse=True)
        history.append({
            "generation": gen + 1,
            "best_qvis_generation": ranked[0].qvis,
            "best_stable_utility": best_hist.stable_utility,
            "best_feasible": best_hist.feasible,
            "best_violation": best_hist.violation,
            "feasible_fraction": float(np.mean([c.feasible for c in pop])),
        })
        if gen + 1 >= max(4, patience) and stagnant >= patience:
            stopped = True
            break
        pbest_pos = np.stack([p.theta if p is not None else pos[i] for i, p in enumerate(pbest)])
        r1, r2 = rng.random(pos.shape), rng.random(pos.shape)
        vel = pso_w * vel + pso_c1 * r1 * (pbest_pos - pos) + pso_c2 * r2 * (best_hist.theta - pos)
        pos = np.clip(pos + vel, lo, hi)

    assert best_hist is not None
    return OptimizationResult(best_hist, history, final_pop, evaluations, len(history), stopped)


def gwo_only(
    evaluator: Callable[[np.ndarray], Candidate],
    bounds: dict[str, list[float]],
    population: int,
    generations: int,
    seed: int,
    weights: dict[str, float],
    patience: int = 8,
    tolerance: float = 1e-4,
) -> OptimizationResult:
    rng = np.random.default_rng(seed)
    lo, hi = bounds_arrays(bounds)
    pos = rng.uniform(lo, hi, size=(population, len(lo)))
    best_hist: Candidate | None = None
    history = []
    evaluations = 0
    stagnant = 0
    last = -np.inf
    stopped = False
    final_pop: list[Candidate] = []

    for gen in range(generations):
        pop = evaluate_population(pos, evaluator, gen, weights)
        evaluations += len(pop)
        final_pop = pop
        for c in pop:
            if historical_better(c, best_hist):
                best_hist = c.copy()
        assert best_hist is not None
        ranked = sorted(pop, key=current_rank_key, reverse=True)
        alpha, beta, delta = [ranked[min(i, len(ranked)-1)].theta for i in range(3)]
        score = best_hist.stable_utility if best_hist.feasible else -best_hist.violation
        if score - last > tolerance:
            last = score
            stagnant = 0
        else:
            stagnant += 1
        history.append({
            "generation": gen + 1,
            "best_qvis_generation": ranked[0].qvis,
            "best_stable_utility": best_hist.stable_utility,
            "best_feasible": best_hist.feasible,
            "best_violation": best_hist.violation,
            "feasible_fraction": float(np.mean([c.feasible for c in pop])),
        })
        if gen + 1 >= max(4, patience) and stagnant >= patience:
            stopped = True
            break
        acoef = 2.0 - 2.0 * (gen / max(generations - 1, 1))
        xs = []
        for leader in (alpha, beta, delta):
            r1, r2 = rng.random(pos.shape), rng.random(pos.shape)
            A = 2 * acoef * r1 - acoef
            C = 2 * r2
            D = np.abs(C * leader[None, :] - pos)
            xs.append(leader[None, :] - A * D)
        pos = np.clip(sum(xs) / 3.0, lo, hi)

    assert best_hist is not None
    return OptimizationResult(best_hist, history, final_pop, evaluations, len(history), stopped)
