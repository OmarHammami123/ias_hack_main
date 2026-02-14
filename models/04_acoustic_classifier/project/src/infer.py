import argparse
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

from data import SplitManifests
from features import LogMelExtractor, load_norm_stats, normalize_patches
from model import ConvAutoencoder
from utils import get_device, load_config, resolve_project_paths, save_json, set_seed


def load_manifests(paths: Dict[str, Path]) -> SplitManifests:
    mdir = paths["manifests_dir"]
    manifests = SplitManifests(
        train_normal=mdir / "train_normal.csv",
        val_normal=mdir / "val_normal.csv",
        test_normal=mdir / "test_normal.csv",
        test_abnormal=mdir / "test_abnormal.csv",
    )
    missing = [p for p in [manifests.train_normal, manifests.val_normal, manifests.test_normal, manifests.test_abnormal] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing manifest files: {missing}. Run train.py first.")
    return manifests


def score_file(filepath: str, model: ConvAutoencoder, extractor: LogMelExtractor, norm_stats: Dict[str, float], device: torch.device) -> np.ndarray:
    patches = extractor.file_to_patches(filepath)
    patches = normalize_patches(patches, norm_stats["mean"], norm_stats["std"]).to(device)

    with torch.no_grad():
        recon = model(patches)
        err = (recon - patches) ** 2
        patch_scores = err.mean(dim=(1, 2, 3)).detach().cpu().numpy()
    return patch_scores


def aggregate_score(patch_scores: np.ndarray, method: str) -> float:
    if method == "mean":
        return float(np.mean(patch_scores))
    if method == "p95":
        return float(np.percentile(patch_scores, 95))
    raise ValueError(f"Unsupported aggregation: {method}")


def score_manifest(
    manifest_csv: Path,
    split_name: str,
    model: ConvAutoencoder,
    extractor: LogMelExtractor,
    norm_stats: Dict[str, float],
    agg_method: str,
    device: torch.device,
) -> pd.DataFrame:
    df = pd.read_csv(manifest_csv)
    rows: List[Dict] = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"[infer] scoring {split_name}"):
        filepath = row["filepath"]
        label = row["true_label"]
        patch_scores = score_file(filepath, model, extractor, norm_stats, device)
        anomaly_score = aggregate_score(patch_scores, agg_method)
        rows.append(
            {
                "filepath": filepath,
                "true_label": label,
                "split": split_name,
                "anomaly_score": anomaly_score,
            }
        )
    return pd.DataFrame(rows)


def run_inference(config_path: str | None) -> None:
    config = load_config(config_path)
    set_seed(int(config["seed"]))
    paths = resolve_project_paths(config, config_path)
    manifests = load_manifests(paths)

    ckpt_path = paths["checkpoints_dir"] / "best.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}. Run train.py first.")

    norm_stats_path = paths["output_root"] / "norm_stats.json"
    if not norm_stats_path.exists():
        raise FileNotFoundError(f"Normalization stats not found: {norm_stats_path}. Run train.py first.")

    device = get_device(config["training"]["device"])
    model = ConvAutoencoder().to(device)
    ckpt = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    extractor = LogMelExtractor(config)
    norm_stats = load_norm_stats(norm_stats_path)

    agg_method = config["inference"]["aggregation"]
    val_df = score_manifest(manifests.val_normal, "val_normal", model, extractor, norm_stats, agg_method, device)
    test_n_df = score_manifest(manifests.test_normal, "test_normal", model, extractor, norm_stats, agg_method, device)
    test_a_df = score_manifest(manifests.test_abnormal, "test_abnormal", model, extractor, norm_stats, agg_method, device)

    threshold = float(np.percentile(val_df["anomaly_score"].values, float(config["inference"]["threshold_percentile"])))

    pred_df = pd.concat([test_n_df, test_a_df], ignore_index=True)
    pred_df["threshold"] = threshold
    pred_df["predicted_label"] = np.where(pred_df["anomaly_score"] >= threshold, "abnormal", "normal")
    pred_df = pred_df.sort_values(by="anomaly_score", ascending=False).reset_index(drop=True)

    pred_path = paths["eval_dir"] / "predictions.csv"
    pred_df.to_csv(pred_path, index=False)
    val_scores_path = paths["eval_dir"] / "val_normal_scores.csv"
    val_df.to_csv(val_scores_path, index=False)

    save_json(
        {
            "threshold": threshold,
            "threshold_percentile": float(config["inference"]["threshold_percentile"]),
            "aggregation": agg_method,
            "checkpoint": str(ckpt_path),
        },
        paths["eval_dir"] / "threshold.json",
    )
    print(f"[infer] saved predictions: {pred_path}")
    print(f"[infer] threshold: {threshold:.8f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()
    run_inference(args.config)


if __name__ == "__main__":
    main()
