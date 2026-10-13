from __future__ import annotations

import contextlib
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import threading
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import psutil


def stable_seed(base_seed: int, *parts: str) -> int:
    h = hashlib.sha256(("|".join(map(str, parts))).encode("utf-8")).digest()
    offset = int.from_bytes(h[:4], "little")
    return (int(base_seed) + offset) % (2**32 - 1)


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def to_builtin(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: to_builtin(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_builtin(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, Path):
        return str(obj)
    return obj


def write_json(data: Any, path: str | Path, indent: int = 2) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_builtin(data), indent=indent, ensure_ascii=False), encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class PeakRSSMonitor:
    """Approximate process peak RSS while a block runs.

    NumPy/OpenCV allocations are outside Python's tracemalloc, so sampling RSS is
    more meaningful for the paper's implementation-memory report.
    """

    def __init__(self, interval: float = 0.05):
        self.interval = interval
        self._stop = threading.Event()
        self.peak = 0
        self._thread: threading.Thread | None = None
        self.proc = psutil.Process(os.getpid())

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                rss = self.proc.memory_info().rss
                self.peak = max(self.peak, rss)
            except psutil.Error:
                pass
            self._stop.wait(self.interval)

    def __enter__(self) -> "PeakRSSMonitor":
        try:
            self.peak = self.proc.memory_info().rss
        except psutil.Error:
            self.peak = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    @property
    def peak_mb(self) -> float:
        return self.peak / (1024**2)


@contextlib.contextmanager
def timed_memory() -> Iterator[dict[str, float]]:
    stats: dict[str, float] = {}
    with PeakRSSMonitor() as monitor:
        t0 = time.perf_counter()
        yield stats
        stats["runtime_sec"] = time.perf_counter() - t0
        stats["peak_rss_mb"] = monitor.peak_mb


def environment_manifest() -> dict[str, Any]:
    import importlib.metadata as md

    packages = {}
    for name in [
        "numpy", "scipy", "pandas", "opencv-python", "scikit-image",
        "matplotlib", "rasterio", "psutil", "PyYAML", "Pillow", "tqdm"
    ]:
        try:
            packages[name] = md.version(name)
        except md.PackageNotFoundError:
            packages[name] = None

    cpu = platform.processor() or platform.machine()
    try:
        freq = psutil.cpu_freq()
        freq_mhz = None if freq is None else freq.max
    except Exception:
        freq_mhz = None

    return {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": cpu,
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "cpu_max_mhz": freq_mhz,
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 3),
        "packages": packages,
    }


def try_git_commit(root: str | Path) -> str | None:
    try:
        p = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True,
            text=True, timeout=5, check=True
        )
        return p.stdout.strip()
    except Exception:
        return None
