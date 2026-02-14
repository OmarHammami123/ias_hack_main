import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from utils import load_config, read_json, resolve_project_paths, save_json, set_seed


def tune_threshold_for_best_f1(y_true: np.ndarray, scores: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    f1_vals = (2 * precision * recall) / np.clip(precision + recall, a_min=1e-12, a_max=None)
    if len(thresholds) == 0:
        return float(np.median(scores))
    idx = int(np.nanargmax(f1_vals[:-1]))
    return float(thresholds[idx])


def run_evaluation(config_path: str | None) -> None:
    config = load_config(config_path)
    set_seed(int(config["seed"]))
    paths = resolve_project_paths(config, config_path)

    pred_path = paths["eval_dir"] / "predictions.csv"
    th_path = paths["eval_dir"] / "threshold.json"
    if not pred_path.exists():
        raise FileNotFoundError(f"Missing predictions file: {pred_path}. Run infer.py first.")
    if not th_path.exists():
        raise FileNotFoundError(f"Missing threshold file: {th_path}. Run infer.py first.")

    pred_df = pd.read_csv(pred_path)
    th_payload = read_json(th_path)

    y_true = np.where(pred_df["true_label"].values == "abnormal", 1, 0).astype(int)
    scores = pred_df["anomaly_score"].values.astype(float)
    threshold = float(th_payload["threshold"])

    if bool(config["evaluation"]["enable_supervised_threshold_tuning"]):
        threshold = tune_threshold_for_best_f1(y_true, scores)

    y_pred = (scores >= threshold).astype(int)

    metrics = {
        "threshold": threshold,
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "pr_auc": float(average_precision_score(y_true, scores)),
        "f1": float(f1_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
    }

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    metrics["confusion_matrix"] = {
        "tn": int(cm[0, 0]),
        "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]),
        "tp": int(cm[1, 1]),
    }

    pred_df["predicted_label"] = np.where(y_pred == 1, "abnormal", "normal")
    pred_df["threshold"] = threshold
    pred_df.to_csv(pred_path, index=False)

    metrics_path = paths["eval_dir"] / "metrics.json"
    save_json(metrics, metrics_path)

    fpr, tpr, _ = roc_curve(y_true, scores)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"AUC={metrics['roc_auc']:.4f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(paths["eval_dir"] / "roc_curve.png", dpi=140)
    plt.close()

    precision, recall, _ = precision_recall_curve(y_true, scores)
    plt.figure(figsize=(6, 5))
    plt.plot(recall, precision, label=f"AP={metrics['pr_auc']:.4f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(paths["eval_dir"] / "pr_curve.png", dpi=140)
    plt.close()

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["normal", "abnormal"])
    disp.plot(values_format="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(paths["eval_dir"] / "confusion_matrix.png", dpi=140)
    plt.close()

    print(f"[evaluate] metrics saved: {metrics_path}")
    for k, v in metrics.items():
        if k == "confusion_matrix":
            print(f"[evaluate] {k}: {v}")
        else:
            print(f"[evaluate] {k}: {v:.6f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()
    run_evaluation(args.config)


if __name__ == "__main__":
    main()
