"""
Command-line inference for the Isolation Forest leak detector.
Prompts for sensor readings, builds the same feature layout as training,
loads the trained model + scaler, and prints anomaly flag and score.

Usage (from project root):
    python -m models.01_isolation_forest.infer

Ensure trained artifacts exist:
    models/01_isolation_forest/trained_model/isolation_forest.pkl
    models/01_isolation_forest/trained_model/scaler.pkl
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd

# Add project root
sys.path.append(str(Path(__file__).parent.parent.parent))

MODEL_DIR = Path(__file__).parent / "trained_model"
MODEL_PATH = MODEL_DIR / "isolation_forest.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# Ordered feature list as created in train.py
FEATURES = [
    "pressure_psi",
    "humidity_percent",
    "temperature_c",
    # rolling means
    "pressure_psi_rolling_mean_60s",
    "humidity_percent_rolling_mean_60s",
    "temperature_c_rolling_mean_60s",
    # rolling stds
    "pressure_psi_rolling_std_60s",
    "humidity_percent_rolling_std_60s",
    "temperature_c_rolling_std_60s",
    # deltas
    "pressure_psi_diff",
    "humidity_percent_diff",
    "temperature_c_diff",
    # time features
    "hour_sin",
    "hour_cos",
    "is_work_hours",
    # deviations
    "pressure_deviation",
    "humidity_deviation",
]


def prompt_float(label: str, default: float | None = None) -> float:
    while True:
        raw = input(f"Enter {label}{' [' + str(default) + ']' if default is not None else ''}: ").strip()
        if not raw and default is not None:
            return float(default)
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")


def build_feature_row(pressure: float, humidity: float, temp: float, hour: int | None = None) -> pd.DataFrame:
    h = hour if hour is not None else datetime.now().hour
    hour_sin = np.sin(2 * np.pi * h / 24)
    hour_cos = np.cos(2 * np.pi * h / 24)
    is_work_hours = 1 if 7 <= h <= 19 else 0

    # With no history, approximate rolling stats to current value, std=0, diff=0, deviations=0
    row = {
        "pressure_psi": pressure,
        "humidity_percent": humidity,
        "temperature_c": temp,
        "pressure_psi_rolling_mean_60s": pressure,
        "humidity_percent_rolling_mean_60s": humidity,
        "temperature_c_rolling_mean_60s": temp,
        "pressure_psi_rolling_std_60s": 0.0,
        "humidity_percent_rolling_std_60s": 0.0,
        "temperature_c_rolling_std_60s": 0.0,
        "pressure_psi_diff": 0.0,
        "humidity_percent_diff": 0.0,
        "temperature_c_diff": 0.0,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "is_work_hours": is_work_hours,
        "pressure_deviation": 0.0,
        "humidity_deviation": 0.0,
    }
    # Preserve column order
    df = pd.DataFrame([[row[f] for f in FEATURES]], columns=FEATURES)
    return df


def load_artifacts():
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("Trained model/scaler not found. Run train.py first.")
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


def predict_single(df: pd.DataFrame, model, scaler):
    # Align columns to the scaler's training order and fill any missing with 0
    if hasattr(scaler, "feature_names_in_"):
        needed = list(scaler.feature_names_in_)
        # Add missing columns as zeros
        for col in needed:
            if col not in df.columns:
                df[col] = 0.0
        df = df[needed]
    X_scaled = scaler.transform(df)
    pred_raw = model.predict(X_scaled)  # -1 anomaly, 1 normal
    binary = int(pred_raw[0] == -1)
    score = -model.score_samples(X_scaled)[0]  # higher = more anomalous
    return binary, score


def main():
    parser = argparse.ArgumentParser(description="Isolation Forest CLI inference")
    parser.add_argument("--hour", type=int, default=None, help="Override hour-of-day feature (0-23)")
    args = parser.parse_args()

    pressure = prompt_float("pressure_psi")
    humidity = prompt_float("humidity_percent (0-100)")
    temp = prompt_float("temperature_c")

    df = build_feature_row(pressure, humidity, temp, hour=args.hour)
    model, scaler = load_artifacts()
    binary, score = predict_single(df, model, scaler)

    print("\n=== Inference Result ===")
    print(f"Anomaly flag: {binary} (1 = leak/anomaly, 0 = normal)")
    print(f"Anomaly score: {score:.4f} (higher = more anomalous)")


if __name__ == "__main__":
    main()
