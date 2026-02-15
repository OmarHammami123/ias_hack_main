"""
Backend server: ties data_generator → isolation forest → dashboard via WebSocket.

Every second:
  1. data_generator produces sensor readings for all 10 pipes
  2. Each pipe's 3 features (pressure_psi, temperature_c, humidity_percent)
     are fed into the trained Isolation Forest model
  3. The full payload (readings + model-detected anomalies) is pushed
     to every connected React dashboard over WebSocket

Run:
    cd ias_hack_main
    python -m backend.server
"""

import asyncio
import json
import time
import sys
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import pandas as pd
import joblib

# ── paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

MODEL_DIR   = PROJECT_ROOT / "models" / "01_isolation_forest" / "trained_model"
MODEL_PATH  = MODEL_DIR / "isolation_forest.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# ── pipe network (mirrors dashboard3/src/data/network.js) ─────────────────────
PIPE_IDS = [
    "P-001", "P-002", "P-003", "P-004", "P-005",
    "P-006", "P-007", "P-008", "P-009", "P-010",
]

# ── import data generator logic ───────────────────────────────────────────────
from data.data_generator import PipeNetwork

# ── Isolation Forest wrapper ──────────────────────────────────────────────────

# Feature order expected by the trained model (from infer.py)
FEATURES = [
    "pressure_psi",
    "humidity_percent",
    "temperature_c",
    "pressure_psi_rolling_mean_60s",
    "humidity_percent_rolling_mean_60s",
    "temperature_c_rolling_mean_60s",
    "pressure_psi_rolling_std_60s",
    "humidity_percent_rolling_std_60s",
    "temperature_c_rolling_std_60s",
    "pressure_psi_diff",
    "humidity_percent_diff",
    "temperature_c_diff",
    "hour_sin",
    "hour_cos",
    "is_work_hours",
    "pressure_deviation",
    "humidity_deviation",
]

HISTORY_LEN = 60  # rolling window in ticks (seconds)


class AnomalyDetector:
    """Wraps the trained Isolation Forest for per-pipe real-time inference."""

    def __init__(self):
        print("[*] Loading Isolation Forest model...")
        self.model  = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        # per-pipe history buffers for rolling stats
        self.buffers: dict[str, deque] = {
            pid: deque(maxlen=HISTORY_LEN) for pid in PIPE_IDS
        }
        print("[OK] Model loaded")

    def _build_features(self, pipe_id: str, pressure: float, temp: float, humidity: float) -> pd.DataFrame:
        """Build the 17-feature row for one pipe using its rolling history."""
        buf = self.buffers[pipe_id]
        buf.append({"pressure": pressure, "temperature": temp, "humidity": humidity})

        pres_arr = [d["pressure"]    for d in buf]
        temp_arr = [d["temperature"] for d in buf]
        hum_arr  = [d["humidity"]    for d in buf]

        h = datetime.now().hour
        hour_sin     = np.sin(2 * np.pi * h / 24)
        hour_cos     = np.cos(2 * np.pi * h / 24)
        is_work_hrs  = 1 if 7 <= h <= 19 else 0

        pres_mean = float(np.mean(pres_arr))
        hum_mean  = float(np.mean(hum_arr))
        temp_mean = float(np.mean(temp_arr))

        row = {
            "pressure_psi":                      pressure,
            "humidity_percent":                   humidity,
            "temperature_c":                      temp,
            "pressure_psi_rolling_mean_60s":      pres_mean,
            "humidity_percent_rolling_mean_60s":   hum_mean,
            "temperature_c_rolling_mean_60s":      temp_mean,
            "pressure_psi_rolling_std_60s":        float(np.std(pres_arr)) if len(pres_arr) > 1 else 0.0,
            "humidity_percent_rolling_std_60s":     float(np.std(hum_arr))  if len(hum_arr)  > 1 else 0.0,
            "temperature_c_rolling_std_60s":        float(np.std(temp_arr)) if len(temp_arr) > 1 else 0.0,
            "pressure_psi_diff":                   pressure - pres_arr[-2] if len(pres_arr) > 1 else 0.0,
            "humidity_percent_diff":               humidity - hum_arr[-2]  if len(hum_arr)  > 1 else 0.0,
            "temperature_c_diff":                  temp     - temp_arr[-2] if len(temp_arr) > 1 else 0.0,
            "hour_sin":                            hour_sin,
            "hour_cos":                            hour_cos,
            "is_work_hours":                       is_work_hrs,
            "pressure_deviation":                  pressure - pres_mean,
            "humidity_deviation":                  humidity - hum_mean,
        }
        df = pd.DataFrame([[row[f] for f in FEATURES]], columns=FEATURES)
        return df

    def predict(self, pipe_id: str, pressure: float, temp: float, humidity: float) -> tuple[int, float]:
        """Return (is_anomaly: 0|1, score: float) for a single pipe reading."""
        df = self._build_features(pipe_id, pressure, temp, humidity)
        # align to scaler's column order
        if hasattr(self.scaler, "feature_names_in_"):
            needed = list(self.scaler.feature_names_in_)
            for col in needed:
                if col not in df.columns:
                    df[col] = 0.0
            df = df[needed]
        X = self.scaler.transform(df)
        pred = self.model.predict(X)
        score = float(-self.model.score_samples(X)[0])
        return int(pred[0] == -1), score


# ── FastAPI app ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application):
    """Modern lifespan handler — replaces deprecated on_event."""
    asyncio.create_task(tick_loop())
    yield

app = FastAPI(title="Pipe Network Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
generator = PipeNetwork()
detector  = AnomalyDetector()
clients: list[WebSocket] = []


async def broadcast(message: str):
    """Send message to all connected WebSocket clients."""
    dead = []
    for ws in clients:
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.remove(ws)


async def tick_loop():
    """Main loop: generate data → run model → broadcast every second."""
    print("\n[*] Tick loop started (1 Hz)\n")
    while True:
        t0 = time.time()
        row = generator.generate_tick()
        ts  = row["timestamp"]

        readings  = {}
        anomalies = []
        scores    = {}

        for pipe_id in PIPE_IDS:
            ps  = row[f"PS_{pipe_id}"]
            pe  = row[f"PE_{pipe_id}"]
            t   = row[f"T_{pipe_id}"]
            h   = row[f"H_{pipe_id}"]

            # Use PE (outlet pressure) as model input — a leak drops PE
            # while PS stays near normal, so PE carries the anomaly signal
            is_anom, score = detector.predict(pipe_id, pe, t, h)

            # Pressure differential: a real leak creates a big gap (PS >> PE)
            # Normal gap is ~1 psi; anomaly gap is 15-25 psi
            pressure_diff = ps - pe
            DIFF_THRESHOLD = 8.0  # flag only when gap > 8 psi

            readings[pipe_id] = {
                "pressureIn":  round(ps, 2),
                "pressureOut": round(pe, 2),
                "temperature": round(t, 2),
                "humidity":    round(h, 2),
                "pressureDiff": round(pressure_diff, 2),
                "ts":          int(time.time() * 1000),
            }
            scores[pipe_id] = round(score, 4)
            # Only flag as anomaly when BOTH model detects it AND pressure diff is large
            if is_anom and pressure_diff > DIFF_THRESHOLD:
                anomalies.append(pipe_id)

        payload = json.dumps({
            "timestamp": ts,
            "readings":  readings,
            "anomalies": anomalies,
            "scores":    scores,
        })

        await broadcast(payload)

        # log
        anom_str = f"  ANOMALIES: {anomalies}" if anomalies else ""
        print(f"[tick] {ts}  clients={len(clients)}{anom_str}")

        elapsed = time.time() - t0
        await asyncio.sleep(max(0, 1.0 - elapsed))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print(f"[+] Client connected ({len(clients)} total)")
    try:
        while True:
            # keep connection alive; ignore client messages
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)
        print(f"[-] Client disconnected ({len(clients)} total)")


@app.get("/health")
def health():
    return {"status": "ok", "pipes": len(PIPE_IDS)}


if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=False)
