"""
Configuration settings for the leak detection system.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Sensor Configuration
SENSOR_CONFIG = {
    "zones": ["Zone_A", "Zone_B", "Zone_C", "Zone_D"],
    "pressure_sensors_per_zone": 5,
    "acoustic_sensors_per_zone": 2,
    "normal_pressure_psi": 125,
    "normal_humidity_percent": 45,  # Normal ambient humidity
    "sampling_rate_hz": 1,  # 1 sample per second
}

# Leak Configuration
LEAK_CONFIG = {
    "leak_probability": 0.05,  # 5% chance of leak in any zone
    "small_leak_threshold_psi": 5,  # < 5 psi drop
    "medium_leak_threshold_psi": 15,  # 5-15 psi drop
    "large_leak_threshold_psi": 15,  # > 15 psi drop
}

# Model Configuration
MODEL_CONFIG = {
    "isolation_forest": {
        "contamination": 0.16,  # Match actual anomaly rate (15.86%)
        "n_estimators": 200,  # More trees = better accuracy
        "random_state": 42,
    },
    "severity_classifier": {
        "pressure_drop_thresholds": {
            "small": 5,
            "medium": 15,
            "large": float("inf"),
        },
        "flow_deviation_thresholds": {
            "small": 50,
            "medium": 150,
            "large": float("inf"),
        },
    },
    "leak_size_estimator": {
        "train_test_split": 0.2,
        "random_state": 42,
    },
    "acoustic_classifier": {
        "sample_rate": 44100,
        "n_mfcc": 40,
        "n_fft": 2048,
        "hop_length": 512,
        "epochs": 50,
        "batch_size": 32,
    },
    "predictive_forecast": {
        "forecast_days": 30,
        "seasonality_mode": "multiplicative",
        "interval_width": 0.95,
    },
}

# Cost Calculation
COST_CONFIG = {
    "electricity_rate_per_kwh": 0.37,  # 0.37 TND per kWh (converted from $0.12 at 1 USD = 3.1 TND)
    "compressor_efficiency": 0.75,  # 75% efficient
    "hours_per_year": 8760,  # 24/7 operation
    "leak_size_to_cfm": {  # leak diameter (mm) -> CFM loss
        1: 2.5,
        2: 10,
        3: 22.5,
        4: 40,
        5: 62.5,
    },
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "refresh_interval_seconds": 5,
    "max_alerts_displayed": 20,
    "zone_colors": {
        "OK": "#28a745",
        "WARNING": "#ffc107",
        "CRITICAL": "#dc3545",
    },
}

# Data Generation
DATA_GENERATION_CONFIG = {
    "num_days": 0.25,  # Generate 6 hours of data (~432K rows - fast training)
    "sensors_per_zone": 5,
    "leak_injection_probability": 0.25,  # 25% - ensures multiple leaks for training
    "noise_level": 0.02,  # 2% noise
}
