from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def resolve_preset(cfg: dict[str, Any], preset: str) -> dict[str, Any]:
    if preset not in cfg["presets"]:
        raise KeyError(f"Unknown preset {preset!r}. Available: {list(cfg['presets'])}")
    out = deepcopy(cfg)
    out["active_preset_name"] = preset
    out["active_preset"] = deepcopy(cfg["presets"][preset])
    return out


def save_yaml(data: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
