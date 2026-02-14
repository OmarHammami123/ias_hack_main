# 🏭 Silent Sabotage - Industrial Leak Detection System

An AI-powered system for detecting, localizing, and predicting compressed air leaks in industrial facilities.

## 🎯 Project Overview

This hackathon project implements a multi-modal leak detection system using:
- **Pressure & Flow Analysis** - Primary detection method
- **Acoustic Classification** - Secondary confirmation
- **Zone-Based Localization** - Pinpoint leak locations
- **Predictive Forecasting** - Anticipate future failures

## 📁 Project Structure

```
ias_hack_main/
├── models/                      # ML model implementations
│   ├── 01_isolation_forest/     # Anomaly detection (PRIORITY: Must Have)
│   ├── 02_severity_classifier/  # Rule-based severity scoring (PRIORITY: Must Have)
│   ├── 03_leak_size_estimator/  # Linear regression for leak size (PRIORITY: Should Have)
│   ├── 04_acoustic_classifier/  # CNN on spectrograms (PRIORITY: Nice to Have)
│   └── 05_predictive_forecast/  # Prophet/LSTM for prediction (PRIORITY: Nice to Have)
├── data/                        # Data generation and storage
│   ├── raw/                     # Raw synthetic sensor data
│   ├── processed/               # Processed features
│   └── generate_data.py         # Synthetic data generator
├── notebooks/                   # Jupyter notebooks for experimentation
├── dashboard/                   # Streamlit dashboard
│   └── app.py                   # Main dashboard application
├── utils/                       # Shared utilities
│   ├── config.py                # Configuration settings
│   └── helpers.py               # Helper functions
├── tests/                       # Unit tests
├── docs/                        # Documentation and pitch deck
├── requirements.txt             # Python dependencies (legacy - for reference)
├── pyproject.toml              # Project config & dependencies (for uv)
├── uv.lock                     # Locked dependency versions (auto-generated)
└── README.md                    # This file
```

## 🚀 Quick Start

> **💡 We use [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management (10-100x faster than pip!)**

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ias_hack_main

# Install uv (if not already installed)
pip install uv

# Sync dependencies (creates venv automatically!)
uv sync

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

> **Note:** `uv sync` automatically creates a virtual environment, installs all dependencies from `pyproject.toml`, and locks versions in `uv.lock`!

### 2. Generate Synthetic Data (IMPORTANT - DO THIS FIRST!)
```bash
python data/generate_data.py
```
This generates:
- 7 days of pressure sensor data (~1.6M rows)
- Acoustic sensor data (~160K rows)  
- Sensor metadata (locations, pipe info)

### 3. Train Models
Each team member can work on their assigned model:
```bash
> 📖 **See [TEAM_GUIDE.md](TEAM_GUIDE.md) for complete collaboration guide**

| Team Member | Model | Priority | Est. Time | README |
|-------------|-------|----------|-----------|--------|
| Member 1 | Isolation Forest | ✅ Must Have | 1-2h | [📖 Guide](models/01_isolation_forest/README.md) |
| Member 2 | Severity Classifier | ✅ Must Have | 30min | [📖 Guide](models/02_severity_classifier/README.md) |
| Member 3 | Leak Size Estimator | ⚠️ Should Have | 1h | [📖 Guide](models/03_leak_size_estimator/README.md) |
| Member 4 | Acoustic Classifier | 💡 Nice to Have | 2-3h | [📖 Guide](models/04_acoustic_classifier/README.md) |
| Member 5 | Predictive Forecast | 💡 Differentiator | 2-3h | [📖 Guide](models/05_predictive_forecast/README.md) |
| ALL | Dashboard | ✅ Must Have | 3-4h | [📖 Guide](dashboard/README.md) |

**Each model has a detailed README with:**
- Task description and objectives
- Success criteria
- Code examples and tips
- Troubleshooting guide
- Integration points
python models/03_leak_size_estimator/train.py

# Model 04: Acoustic Classification (Priority: Nice to Have)
python models/04_acoustic_classifier/train.py

# Model 05: Predictive Forecasting (Priority: Differentiator!)
python models/05_predictive_forecast/train.py
```

### 4. Run Dashboard
```bash
streamlit run dashboard/app.py
```
Open browser to: `http://localhost:8501`

## 👥 Team Task Assignment

| Team Member | Model | Priority | Est. Time |
|-------------|-------|----------|-----------|
| Member 1 | Isolation Forest | ✅ Must Have | 1-2h |
| Member 2 | Severity Classifier | ✅ Must Have | 30min |
| Member 3 | Leak Size Estimator | ⚠️ Should Have | 1h |
| Member 4 | Acoustic Classifier | 💡 Nice to Have | 2-3h |
| Member 5 | Predictive Forecast | 💡 Nice to Have | 2-3h |

## 📊 Data Schema

### Pressure Sensor Data
```json
{
  "timestamp": "2026-02-14T10:30:00Z",
  "sensor_id": "S001",
  "zone": "Zone_A",
  "pressure_psi": 125.3,
  "flow_rate_cfm": 450.2,
  "temperature_c": 22.5
}
```

### Acoustic Sensor Data
```json
{
  "timestamp": "2026-02-14T10:30:00Z",
  "sensor_id": "A001",
  "zone": "Zone_A",
  "frequency_bands": [/* 10 frequency bands */],
  "amplitude_db": 65.2
}
```

## 🎯 Success Criteria

- [x] Generate realistic synthetic sensor data
- [ ] Implement Isolation Forest anomaly detection (>90% accuracy)
- [ ] Implement severity classification
- [ ] Implement leak size estimation
- [ ] Build Streamlit dashboard with zone visualization
- [ ] Add pressure gradient charts
- [ ] Calculate cost estimates ($/year waste)
- [ ] (Bonus) Add acoustic classification
- [ ] (Bonus) Add predictive forecasting

## 📈 24-Hour Sprint Timeline

| Hours | Tasks |
|-------|-------|
| 0-2 | Setup, data generation |
| 2-5 | Train core models (isolation forest, severity) |
| 5-8 | Build dashboard skeleton |
| 8-11 | Add visualizations and metrics |
| 11-14 | IoT simulation integration |
| 14-17 | Polish UI, add bonus models |
| 17-20 | Pitch deck creation |
| 20-22 | Video recording, rehearsal |
| 22-24 | Final polish and submission |

## 🛠️ Tech Stack

- **ML**: scikit-learn, TensorFlow/PyTorch, Prophet
- **Dashboard**: Streamlit, Plotly
- **Data**: Pandas, NumPy
- **IoT Simulation**: Wokwi (ESP32)

## 📝 Git Workflow

```bash
# Create feature branch for your model
git checkout -b feature/isolation-forest

# Make changes, commit regularly
git add .
git commit -m "feat: implement isolation forest anomaly detection"

# Push to remote
git push origin feature/isolation-forest

# Create pull request for review
```

## 🎤 Pitch Highlights

1. **Multi-modal detection** - Pressure + Acoustic sensors
2. **Smart localization** - Zone-based + pressure gradient mapping
3. **Business impact** - Clear ROI with cost estimates
4. **Predictive maintenance** - Don't just detect, predict future leaks
5. **Real-world ready** - Uses industry-standard sensors and methods

## 📞 Contact

For questions during the hackathon, reach out in the team channel.

---

**Let's build something amazing! 🚀**
