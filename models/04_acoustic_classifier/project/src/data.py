from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import soundfile as sf

from utils import ensure_dir


@dataclass
class SplitManifests:
    train_normal: Path
    val_normal: Path
    test_normal: Path
    test_abnormal: Path


def _scan_files(base_dir: Path, ext: str) -> List[Path]:
    if not base_dir.exists():
        return []
    return sorted(p for p in base_dir.rglob(f"*{ext}") if p.is_file())


def _get_all_machine_ids(data_root: Path, machine_type: str) -> List[str]:
    """Discover all machine IDs in the dataset directory."""
    type_dir = data_root / machine_type
    if not type_dir.exists():
        raise FileNotFoundError(f"Machine type directory not found: {type_dir}")
    
    machine_ids = []
    for item in sorted(type_dir.iterdir()):
        if item.is_dir() and (item / "normal").exists():
            machine_ids.append(item.name)
    
    if len(machine_ids) == 0:
        raise FileNotFoundError(f"No machine IDs found in: {type_dir}")
    
    return machine_ids


def scan_mimii_style_dataset(data_root: Path, machine_type: str, machine_id: str, audio_ext: str) -> Dict[str, List[Path]]:
    """
    Scan dataset files. If machine_id is "all", scans all available machine IDs.
    Otherwise, scans only the specified machine_id.
    """
    if machine_id.lower() == "all":
        # Scan all machine IDs
        all_machine_ids = _get_all_machine_ids(data_root, machine_type)
        print(f"[data] scanning all machine IDs: {all_machine_ids}")
        
        all_normal_files = []
        all_abnormal_files = []
        
        for mid in all_machine_ids:
            id_root = data_root / machine_type / mid
            normal_dir = id_root / "normal"
            abnormal_dir = id_root / "abnormal"
            
            normal_files = _scan_files(normal_dir, audio_ext)
            abnormal_files = _scan_files(abnormal_dir, audio_ext)
            
            all_normal_files.extend(normal_files)
            all_abnormal_files.extend(abnormal_files)
            
            print(f"[data]   {mid}: {len(normal_files)} normal, {len(abnormal_files)} abnormal")
        
        if len(all_normal_files) == 0:
            raise FileNotFoundError(f"No normal files found across all machine IDs in {machine_type}")
        if len(all_abnormal_files) == 0:
            raise FileNotFoundError(f"No abnormal files found across all machine IDs in {machine_type}")
        
        return {"normal": all_normal_files, "abnormal": all_abnormal_files}
    else:
        # Scan single machine ID
        id_root = data_root / machine_type / machine_id
        normal_dir = id_root / "normal"
        abnormal_dir = id_root / "abnormal"

        normal_files = _scan_files(normal_dir, audio_ext)
        abnormal_files = _scan_files(abnormal_dir, audio_ext)

        if len(normal_files) == 0:
            raise FileNotFoundError(f"No normal files found in: {normal_dir}")
        if len(abnormal_files) == 0:
            raise FileNotFoundError(f"No abnormal files found in: {abnormal_dir}")

        return {"normal": normal_files, "abnormal": abnormal_files}


def _to_manifest_df(filepaths: List[Path], label: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "filepath": [str(p.resolve()) for p in filepaths],
            "true_label": [label] * len(filepaths),
        }
    )


def _assert_no_overlap(named_splits: Dict[str, pd.DataFrame]) -> None:
    sets = {name: set(df["filepath"].tolist()) for name, df in named_splits.items()}
    keys = list(sets.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            overlap = sets[keys[i]].intersection(sets[keys[j]])
            if overlap:
                raise ValueError(f"Found overlap between splits {keys[i]} and {keys[j]} ({len(overlap)} files).")


def _sanity_check_audio(manifest_df: pd.DataFrame) -> List[int]:
    sample_rates = []
    for fpath in manifest_df["filepath"].tolist():
        # Use soundfile directly for better compatibility
        info = sf.info(fpath)
        
        if info.frames <= 0:
            raise ValueError(f"Empty audio file detected: {fpath}")
        sample_rates.append(info.samplerate)
    return sample_rates


def create_or_load_splits(config: Dict, paths: Dict[str, Path]) -> SplitManifests:
    manifests_dir = ensure_dir(paths["manifests_dir"])
    train_csv = manifests_dir / "train_normal.csv"
    val_csv = manifests_dir / "val_normal.csv"
    test_normal_csv = manifests_dir / "test_normal.csv"
    test_abnormal_csv = manifests_dir / "test_abnormal.csv"

    manifests = SplitManifests(
        train_normal=train_csv,
        val_normal=val_csv,
        test_normal=test_normal_csv,
        test_abnormal=test_abnormal_csv,
    )

    required_exist = all(p.exists() for p in [train_csv, val_csv, test_normal_csv, test_abnormal_csv])
    if required_exist and not config["data"]["force_regenerate_manifests"]:
        return manifests

    scanned = scan_mimii_style_dataset(
        data_root=paths["data_root"],
        machine_type=config["paths"]["machine_type"],
        machine_id=config["paths"]["machine_id"],
        audio_ext=config["data"]["audio_ext"],
    )

    normal_files = scanned["normal"]
    abnormal_files = scanned["abnormal"]

    train_ratio = float(config["data"]["train_ratio"])
    val_ratio = float(config["data"]["val_ratio"])
    test_ratio = float(config["data"]["test_ratio"])
    if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
        raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.0")

    seed = int(config["seed"])
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(normal_files))
    shuffled = [normal_files[i] for i in perm]

    n_total = len(shuffled)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    n_test = n_total - n_train - n_val

    if min(n_train, n_val, n_test) <= 0:
        raise ValueError(
            f"Invalid split sizes from {n_total} normal files: train={n_train}, val={n_val}, test={n_test}. "
            "Adjust split ratios or use more data."
        )

    train_files = shuffled[:n_train]
    val_files = shuffled[n_train : n_train + n_val]
    test_normal_files = shuffled[n_train + n_val :]

    train_df = _to_manifest_df(train_files, "normal")
    val_df = _to_manifest_df(val_files, "normal")
    test_normal_df = _to_manifest_df(test_normal_files, "normal")
    test_abnormal_df = _to_manifest_df(abnormal_files, "abnormal")

    _assert_no_overlap(
        {
            "train_normal": train_df,
            "val_normal": val_df,
            "test_normal": test_normal_df,
            "test_abnormal": test_abnormal_df,
        }
    )

    all_df = pd.concat([train_df, val_df, test_normal_df, test_abnormal_df], ignore_index=True)
    sample_rates = _sanity_check_audio(all_df)
    unique_sample_rates = sorted(set(sample_rates))
    print(f"[data] scanned {len(all_df)} files | sample rates found: {unique_sample_rates}")

    train_df.to_csv(train_csv, index=False)
    val_df.to_csv(val_csv, index=False)
    test_normal_df.to_csv(test_normal_csv, index=False)
    test_abnormal_df.to_csv(test_abnormal_csv, index=False)

    return manifests
