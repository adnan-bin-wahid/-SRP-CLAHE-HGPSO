from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling


BAND_ORDER = ("B02", "B03", "B04", "B08")


@dataclass
class Scene:
    chip_id: str
    split: str
    cube: np.ndarray  # H x W x 4, float32 reflectance-like values
    valid_mask: np.ndarray  # H x W bool
    profile: dict[str, Any]
    scale_used: float
    source_dir: str
    cloud_fraction: float | None = None
    location: str | None = None
    datetime: str | None = None

    @property
    def height(self) -> int:
        return int(self.cube.shape[0])

    @property
    def width(self) -> int:
        return int(self.cube.shape[1])


@dataclass
class DisplayModel:
    lo: np.ndarray  # B,G,R source order bounds
    hi: np.ndarray


def _read_single(path: Path) -> tuple[np.ndarray, dict[str, Any], float | None]:
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float32)
        profile = ds.profile.copy()
        nodata = ds.nodata
    return arr, profile, nodata


def infer_scale(cube_raw: np.ndarray, mask: np.ndarray) -> float:
    vals = cube_raw[mask]
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return 1.0
    q = float(np.percentile(vals, 99.5))
    # Sentinel-2 L2A competition chips are uint16 DN-like values around 0..10000+
    # while an already scaled reflectance cube is typically around 0..1.
    return 10000.0 if q > 2.0 else 1.0


def load_scene(
    scene_dir: str | Path,
    split: str,
    reflectance_scale: str | float = "auto",
    cloud_mask_name: str = "cloud_mask.tif",
    cloud_values: list[int] | tuple[int, ...] = (1, 255),
    min_valid_fraction: float = 0.70,
    manifest_row: dict[str, Any] | None = None,
) -> Scene:
    scene_dir = Path(scene_dir)
    chip_id = scene_dir.name

    raw = []
    profiles = []
    nodatas = []
    for band in BAND_ORDER:
        path = scene_dir / f"{band}.tif"
        if not path.exists():
            raise FileNotFoundError(f"Missing required band: {path}")
        arr, profile, nodata = _read_single(path)
        raw.append(arr)
        profiles.append(profile)
        nodatas.append(nodata)

    shapes = {a.shape for a in raw}
    if len(shapes) != 1:
        raise ValueError(f"Band shapes are not co-registered in {scene_dir}: {shapes}")

    transforms = [str(p.get("transform")) for p in profiles]
    crss = [str(p.get("crs")) for p in profiles]
    if len(set(transforms)) != 1 or len(set(crss)) != 1:
        raise ValueError(f"Band CRS/transform mismatch in {scene_dir}")

    cube_raw = np.stack(raw, axis=-1)
    valid = np.all(np.isfinite(cube_raw), axis=-1)
    for i, nodata in enumerate(nodatas):
        if nodata is not None:
            valid &= cube_raw[..., i] != float(nodata)
    # Competition data use nodata=0. Retain only pixels with positive signal in all bands.
    valid &= np.all(cube_raw > 0, axis=-1)

    cloud_fraction = None
    cloud_path = scene_dir / cloud_mask_name
    if cloud_path.exists():
        cloud, cprof, cnodata = _read_single(cloud_path)
        if cloud.shape != valid.shape:
            raise ValueError(f"Cloud mask shape mismatch for {chip_id}: {cloud.shape} vs {valid.shape}")
        cloud_bool = np.isin(cloud.astype(np.int32), np.asarray(cloud_values, dtype=np.int32))
        if cnodata is not None:
            valid &= cloud != float(cnodata)
        denominator = max(1, int(np.count_nonzero(np.isfinite(cloud))))
        cloud_fraction = float(np.count_nonzero(cloud_bool) / denominator)
        valid &= ~cloud_bool

    vf = float(valid.mean())
    if vf < min_valid_fraction:
        raise ValueError(
            f"{chip_id} has only {vf:.1%} valid clear pixels; minimum is {min_valid_fraction:.1%}"
        )

    if isinstance(reflectance_scale, str) and reflectance_scale.lower() == "auto":
        scale = infer_scale(cube_raw, valid)
    else:
        scale = float(reflectance_scale)
        if scale <= 0:
            raise ValueError("reflectance_scale must be positive")

    cube = (cube_raw / scale).astype(np.float32)
    cube[~np.isfinite(cube)] = 0.0

    location = None
    dt = None
    if manifest_row:
        location = manifest_row.get("location")
        dt = manifest_row.get("datetime")
        if cloud_fraction is None and manifest_row.get("cloud_fraction") is not None:
            cloud_fraction = float(manifest_row["cloud_fraction"])

    return Scene(
        chip_id=chip_id,
        split=split,
        cube=cube,
        valid_mask=valid,
        profile=profiles[0],
        scale_used=scale,
        source_dir=str(scene_dir),
        cloud_fraction=cloud_fraction,
        location=None if location is None else str(location),
        datetime=None if dt is None else str(dt),
    )


def find_dataset_splits(dataset_root: str | Path) -> dict[str, list[Path]]:
    dataset_root = Path(dataset_root)
    out: dict[str, list[Path]] = {}
    for split in ("validation", "test"):
        p = dataset_root / split
        if p.exists():
            dirs = sorted([d for d in p.iterdir() if d.is_dir()])
            out[split] = dirs
    if not out:
        raise FileNotFoundError(
            f"Expected validation/ and test/ folders under {dataset_root}."
        )
    return out


def load_manifest(dataset_root: str | Path) -> pd.DataFrame:
    p = Path(dataset_root) / "dataset_manifest.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p, dtype={"chip_id": str})
    if "chip_id" in df.columns:
        df["chip_id"] = df["chip_id"].astype(str).str.strip()
    return df


def manifest_lookup(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if df.empty or "chip_id" not in df.columns:
        return {}
    return {str(row["chip_id"]): row.to_dict() for _, row in df.iterrows()}


def fit_display_model(scene: Scene, percentiles=(2.0, 98.0)) -> DisplayModel:
    # Cube order B,G,R,N; display channels derive from B,G,R but bounds stay B,G,R.
    vis = scene.cube[..., :3]
    lo = []
    hi = []
    for c in range(3):
        vals = vis[..., c][scene.valid_mask]
        l, h = np.percentile(vals, percentiles)
        if h <= l:
            h = l + 1e-6
        lo.append(float(l))
        hi.append(float(h))
    return DisplayModel(np.asarray(lo, dtype=np.float32), np.asarray(hi, dtype=np.float32))


def cube_to_rgb(cube: np.ndarray, model: DisplayModel) -> np.ndarray:
    # B,G,R,N -> RGB display, using original-scene bounds for fair comparisons.
    bgr = cube[..., :3]
    scaled = (bgr - model.lo[None, None, :]) / (model.hi - model.lo)[None, None, :]
    scaled = np.clip(scaled, 0.0, 1.0)
    return scaled[..., [2, 1, 0]].astype(np.float32)


def write_geotiff(path: str | Path, arr: np.ndarray, profile: dict[str, Any], dtype="float32") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = profile.copy()
    prof.update(count=1, dtype=dtype, nodata=None, compress="deflate")
    with rasterio.open(path, "w", **prof) as ds:
        ds.write(arr.astype(dtype), 1)
