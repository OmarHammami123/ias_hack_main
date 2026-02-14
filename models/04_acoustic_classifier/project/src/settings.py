from typing import Any, Dict


# Edit these variables when your dataset is downloaded.
DATA_ROOT = "../data"
MACHINE_TYPE = "valve"
MACHINE_ID = "id_00"
OUTPUT_ROOT = "outputs"

SEED = 1337


def get_default_config() -> Dict[str, Any]:
    return {
        "seed": SEED,
        "paths": {
            "data_root": DATA_ROOT,
            "machine_type": MACHINE_TYPE,
            "machine_id": MACHINE_ID,
            "output_root": OUTPUT_ROOT,
            "manifests_dirname": "manifests",
            "checkpoints_dirname": "checkpoints",
            "logs_dirname": "logs",
            "eval_dirname": "eval",
        },
        "data": {
            "audio_ext": ".wav",
            "train_ratio": 0.8,
            "val_ratio": 0.1,
            "test_ratio": 0.1,
            "force_regenerate_manifests": False,
        },
        "features": {
            "sample_rate": 16000,
            "n_fft": 1024,
            "hop_length": 512,
            "n_mels": 64,
            "patch_frames": 64,
            "patch_hop_frames": 32,
            "eps": 1.0e-10,
        },
        "training": {
            "batch_size": 64,
            "num_workers": 0,
            "epochs": 100,
            "learning_rate": 0.001,
            "weight_decay": 0.0,
            "loss": "mse",
            "early_stopping_patience": 12,
            "min_delta": 1.0e-5,
            "device": "auto",
        },
        "inference": {
            "aggregation": "mean",
            "threshold_percentile": 99.0,
        },
        "evaluation": {
            "enable_supervised_threshold_tuning": False,
        },
    }
