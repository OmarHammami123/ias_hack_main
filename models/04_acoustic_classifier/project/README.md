# MIMII Valve 6 dB Anomaly Detection (PyTorch Autoencoder)

Complete, runnable anomaly detection pipeline for MIMII-style valve data.

## What this does

- Trains a convolutional autoencoder on `normal` audio only.
- Uses `abnormal` audio only for evaluation/testing.
- Computes anomaly scores from reconstruction error.
- Saves manifests, checkpoints, metrics, predictions, and plots automatically.

## Project layout

```text
project/
  configs/default.yaml
  src/
    data.py
    features.py
    model.py
    train.py
    infer.py
    evaluate.py
    utils.py
  scripts/
    run_train.sh
    run_eval.sh
  outputs/
  requirements.txt
  README.md
```

## Dataset expected format

```text
data/
  valve/
    id_00/
      normal/*.wav
      abnormal/*.wav
```

By default, config expects `../data` relative to `project/`.

## Install

```bash
cd project
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python src/train.py --config configs/default.yaml
python src/infer.py --config configs/default.yaml
python src/evaluate.py --config configs/default.yaml
```

Or:

```bash
bash scripts/run_train.sh
bash scripts/run_eval.sh
```

## Outputs

All outputs are written to `project/outputs/`:

- `manifests/train_normal.csv`
- `manifests/val_normal.csv`
- `manifests/test_normal.csv`
- `manifests/test_abnormal.csv`
- `checkpoints/best.pt`
- `checkpoints/last.pt`
- `logs/training_log.csv`
- `norm_stats.json`
- `eval/predictions.csv`
- `eval/metrics.json`
- `eval/roc_curve.png`
- `eval/pr_curve.png`
- `eval/confusion_matrix.png`

## Notes on data policy

- Training and validation use normal data only.
- Abnormal data is never included in train/val split.
- Threshold defaults to percentile on `val_normal` scores (`inference.threshold_percentile`).
- Optional supervised threshold tuning is disabled by default and must be explicitly enabled:
  - `evaluation.enable_supervised_threshold_tuning: true`

## Reproducibility

The pipeline enforces fixed seed and deterministic settings (`seed` in config).
Re-running with same seed and environment should produce near-identical results.

## How to adapt from `id_00` to multiple ids

1. Single-id switch:
   - Change `paths.machine_id` in `configs/default.yaml` (e.g., `id_02`).

2. Run per-id and compare:
   - Keep one config per id (e.g., `configs/id_00.yaml`, `configs/id_02.yaml`).
   - Run train/infer/evaluate for each config and compare `outputs/eval/metrics.json`.

3. Extend to multi-id training:
   - Update `src/data.py` scan logic to accept list of ids.
   - Merge normal files from all training ids into train/val manifests.
   - Keep abnormal files only in test/eval manifests.
