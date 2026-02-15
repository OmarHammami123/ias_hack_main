# Dashboard2: Industrial Leak Network (Dash)

A Plotly Dash app that simulates an industrial compressed-air network with pipes, valves, and zones. You can select a pipe to mark a leak (highlighted in red), view live KPIs, pressure trend, and an acoustic spectrogram.

## Quick start
```bash
# from the project root
python -m pip install -r dashboard2/requirements.txt
python dashboard2/app.py
# open http://localhost:8502
```

## Features
- Interactive pipe network: pipes turn red on the selected leak; valves shown as squares.
- KPIs: pressure, flow, leak probability, timestamp (auto-refresh every 5s).
- Pressure trend: last 10-minute synthetic trace with leak-induced drop.
- Acoustic spectrogram: simulated energy map to visualize leak acoustic signature.

## Notes
- Data is simulated for demo; replace `simulate_metrics`, `build_pressure_chart`, and `build_spectrogram` with live feeds when available.
- App runs on port 8502 to avoid conflicts with existing Streamlit apps.
