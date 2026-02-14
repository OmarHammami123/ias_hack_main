import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch
import yaml

from settings import get_default_config


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    if config_path is None:
        return get_default_config()
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config: Dict[str, Any], out_path: str) -> None:
    ensure_dir(Path(out_path).parent)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)


def ensure_dir(path: str | Path) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def save_json(payload: Dict[str, Any], out_path: str | Path) -> None:
    ensure_dir(Path(out_path).parent)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def read_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def set_seed(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)


def get_device(device_cfg: str) -> torch.device:
    if device_cfg == "cpu":
        return torch.device("cpu")
    if device_cfg == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("Config requested CUDA, but CUDA is unavailable.")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def resolve_project_paths(config: Dict[str, Any], config_path: str | None = None) -> Dict[str, Path]:
    if config_path is None:
        config_dir = Path(__file__).resolve().parent.parent / "configs"
    else:
        config_dir = Path(config_path).resolve().parent
    project_root = config_dir.parent

    paths_cfg = config["paths"]
    output_root = (project_root / paths_cfg["output_root"]).resolve()
    manifests_dir = output_root / paths_cfg["manifests_dirname"]
    checkpoints_dir = output_root / paths_cfg["checkpoints_dirname"]
    logs_dir = output_root / paths_cfg["logs_dirname"]
    eval_dir = output_root / paths_cfg["eval_dirname"]
    data_root = (project_root / paths_cfg["data_root"]).resolve()

    for path in [output_root, manifests_dir, checkpoints_dir, logs_dir, eval_dir]:
        ensure_dir(path)

    return {
        "project_root": project_root,
        "data_root": data_root,
        "output_root": output_root,
        "manifests_dir": manifests_dir,
        "checkpoints_dir": checkpoints_dir,
        "logs_dir": logs_dir,
        "eval_dir": eval_dir,
    }
