# 🏭 Silent Sabotage - Industrial Leak Detection System

> **AI-powered compressed air leak detection with real-time monitoring, cost analysis, and predictive maintenance**

An enterprise-grade leak detection system that combines machine learning, IoT sensors, and interactive dashboards to identify, classify, and estimate the financial impact of compressed air leaks in industrial facilities.

## 🎯 Project Overview

### Key Features

✨ **Multi-Modal Detection**
- **Pressure & Humidity Analysis** - Primary detection using Isolation Forest ML
- **Acoustic Classification** - Secondary confirmation with CNN on audio spectrograms
- **Real-time Streaming** - JSONL data stream for Kafka/MQTT integration

🗺️ **Factory Floor Mapping**
- Serial sensor placement along pipeline routes
- Interactive zone-based visualization
- Hotspot identification with severity color-coding

💰 **Cost Analysis**
- Automatic leak cost estimation in Tunisian Dinars (TND)
- Energy waste calculations using 0.37 TND/kWh electricity rate
- ROI projections for leak repairs

📊 **Advanced Analytics**
- 5 ML models working in pipeline
- Severity classification (SMALL/MEDIUM/LARGE)
- Predictive maintenance forecasting
- Trend analysis with 6-hour rolling windows

🎨 **Dark-Themed Dashboard**
- Streamlit-based interactive UI
- Real-time metrics and alerts
- Sensor floor maps with pipeline routing
- Zone analytics and detailed tables

## 📁 Project Structure

```
ias_hack_main/
├── models/                          # ML model implementations
│   ├── 01_isolation_forest/         # Anomaly detection (Isolation Forest)
│   ├── 02_severity_classifier/      # Rule-based severity scoring
│   ├── 03_leak_size_estimator/      # Linear regression for leak size
│   ├── 04_acoustic_classifier/      # Autoencoder for acoustic leak detection
│   └── 05_predictive_forecast/      # Prophet/LSTM time-series forecasting
├── data/                            # Data generation and streaming
│   ├── raw/                         # Generated sensor data (CSV)
│   ├── generate_data.py             # Synthetic data generator (7 days, ~1.6M rows)
│   └── stream_data.py               # Real-time JSONL streaming (NEW!)
├── dashboard/                       # Streamlit dashboard
│   ├── app.py                       # Main dashboard (dark theme, factory maps)
│   └── README.md                    # Dashboard documentation
├── IOT_Nodes/                       # IoT sensor integration scripts
│   ├── BMP180 OUTPUT_to_python.py   # BMP180 pressure/temperature sensor interface
│   └── Soundwaves to python.py      # Acoustic sensor data processing
├── IOT_Wokwi_Simulations/           # Hardware sensor simulations (Wokwi)
│   ├── BMP180_Simulation/           # BMP180 sensor simulator
│   └── INMP441_Simulation/          # INMP441 microphone simulator
├── Conceptions/                     # Hardware design files
│   ├── Conception_3D/               # 3D CAD models (Arduino, sensors, assembly)
│   └── Conception Electrique/       # Electrical circuit designs
├── utils/                           # Shared utilities
│   ├── config.py                    # Configuration (zones, costs, thresholds)
│   └── helpers.py                   # Helper functions (cost calc, noise gen)
├── pyproject.toml                   # Project config & dependencies (uv)
├── uv.lock                          # Locked dependency versions
└── README.md                        # This file
```

## 🚀 Quick Start

> **💡 We use [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management (10-100x faster than pip!)**

### 1. Clone and Setup
```bash
git clone https://github.com/OmarHammami123/ias_hack_main.git
cd ias_hack_main

# Install uv (if not already installed)
pip install uv

# Sync dependencies (creates venv automatically!)
uv sync

# Activate the virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Or for Mac/Linux:
source .venv/bin/activate
```

> **Note:** `uv sync` automatically creates a virtual environment, installs all dependencies from `pyproject.toml`, and locks versions in `uv.lock`!

### 2. Generate Synthetic Data
```bash
# Generate 7 days of historical data
python data/generate_data.py
```

**Output:**
- `data/raw/pressure_sensor_data.csv` - ~1.6M pressure/humidity readings
- `data/raw/acoustic_sensor_data.csv` - ~160K acoustic frequency readings
- Anomaly rate: ~16% (realistic leak injection)

### 3. Train ML Models
```bash
# Model 01: Isolation Forest (Anomaly Detection)
python models/01_isolation_forest/train.py

# Model 02: Severity Classifier (Rule-Based)
python models/02_severity_classifier/train.py

# Model 03: Leak Size Estimator (Linear Regression)
python models/03_leak_size_estimator/train.py

# Model 04: Acoustic Classifier (CNN) - Optional
python models/04_acoustic_classifier/train.py

# Model 05: Predictive Forecast (Prophet) - Optional
python models/05_predictive_forecast/train.py
```

### 4. Run Dashboard
```bash
# Standard mode (uses CSV data)
uv run streamlit run dashboard/app.py

# Or with Python directly
streamlit run dashboard/app.py
```
🌐 **Open browser:** `http://localhost:8501`

### 5. Real-Time Data Streaming (Optional)
```bash
# Stream live data to stdout (JSONL format)
python data/stream_data.py

# Or pipe to Kafka/MQTT
python data/stream_data.py | kafka-console-producer --topic sensor-readings
```

## 🏗️ System Architecture

### ML Pipeline

```
Raw Sensor Data
       ↓
┌──────────────────────────────────────┐
│  Model 01: Isolation Forest          │
│  - Detects anomalies in pressure     │
│  - Output: is_anomaly flag           │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Model 02: Severity Classifier       │
│  - Calculates pressure drop vs median│
│  - Output: SMALL/MEDIUM/LARGE        │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Model 03: Leak Size Estimator       │
│  - Converts pressure drop to leak mm │
│  - Output: Annual cost in TND        │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Model 04: Acoustic Classifier (CNN) │
│  - Confirms leaks via audio signature│
│  - Output: leak/normal classification│
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Model 05: Predictive Forecast       │
│  - Forecasts future leak probability │
│  - Output: 30-day ahead predictions  │
└──────────────────────────────────────┘
       ↓
   Dashboard Visualization
```

### Data Flow

**Historical Analysis (CSV):**
```
generate_data.py → pressure_sensor_data.csv → ML Models → Dashboard
```

**Real-Time Streaming (JSONL):**
```
stream_data.py → stdout (JSONL) → Kafka/MQTT → Real-time Dashboard
```

## 📊 Data Schema

### Pressure Sensor Data
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | datetime | Reading timestamp | `2026-02-14T10:30:00Z` |
| `sensor_id` | string | Sensor identifier | `P_A_001` |
| `zone` | string | Factory zone | `Zone_A` |
| `pressure_psi` | float | Pressure reading (PSI) | `125.3` |
| `humidity_percent` | float | Humidity reading (%) | `45.2` |
| `temperature_c` | float | Temperature (Celsius) | `22.5` |
| `is_anomaly` | boolean | Ground truth label | `true` |

### Classified Leak Output
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sensor_id` | string | Sensor identifier | `P_A_001` |
| `zone` | string | Factory zone | `Zone_A` |
| `severity` | string | Leak severity | `MEDIUM` |
| `priority_score` | int | Urgency (0-100) | `60` |
| `pressure_drop` | float | PSI deviation from baseline | `8.5` |
| `humidity_change` | float | % deviation from baseline | `6.2` |
| `estimated_annual_cost` | float | Cost in TND/year | `12,450.00` |

### Streaming Data Format (JSONL)
Each line is a complete JSON object:
```json
{"timestamp": "2026-02-15T14:22:05", "sensor_id": "P_A_001", "zone": "Zone_A", "pressure_psi": 118.7, "humidity_percent": 42.3, "temperature_c": 21.8, "is_anomaly": true}
```

## ⚙️ Configuration

### Cost Calculation
- **Electricity Rate:** 0.37 TND/kWh
- **Compressor Efficiency:** 75%
- **Operating Hours:** 8,760 hours/year (24/7)
- **CFM to kW Conversion:** 0.25 kW per CFM at 125 PSI

### Severity Thresholds
| Severity | Pressure Drop | Humidity Change |
|----------|---------------|-----------------|
| **LARGE** | > 15 PSI | > 10% |
| **MEDIUM** | 5-15 PSI | 5-10% |
| **SMALL** | < 5 PSI | < 5% |

### Factory Configuration
- **Zones:** 4 (Zone_A, Zone_B, Zone_C, Zone_D)
- **Sensors per Zone:** 5 pressure sensors, 2 acoustic sensors
- **Total Sensors:** 20 pressure + 8 acoustic = 28 sensors
- **Sampling Rate:** 1 Hz (1 reading/second)
- **Normal Pressure:** 125 PSI baseline

## 📈 Model Performance

| Model | Type | Accuracy | Output |
|-------|------|----------|--------|
| **01: Isolation Forest** | Unsupervised | ~90% | `is_anomaly` boolean |
| **02: Severity Classifier** | Rule-based | 100%* | `SMALL/MEDIUM/LARGE` |
| **03: Leak Size Estimator** | Linear Regression | R²=0.85 | Annual cost (TND) |
| **04: Acoustic Classifier** | CNN | ~88% | `leak/normal` |
| **05: Predictive Forecast** | Prophet | MAPE<15% | 30-day forecast |

_*Rule-based classifier has deterministic accuracy given correct inputs_

## 🎨 Dashboard Features

### Main View
- **Hero Metrics:** Active leaks, total cost, average leak cost, cost per sensor
- **Factory Floor Map:** Interactive 2D map with:
  - Serial sensor placement along pipeline routes
  - Zone boundaries and labels
  - Color-coded leak severity markers
  - Directional pipeline flow arrows
  - Hover details for each sensor
- **Recent Trends:** 6-hour rolling pressure/humidity charts
- **Detailed Analytics:** Filterable table with all leak data

### Visualizations
- 📍 **Sensor Floor Map** - 2D factory layout with pipeline routing
- 📊 **Trend Charts** - Pressure and humidity over time
- 📈 **Zone Analytics** - Breakdown by factory zone
- 🔥 **Hotspot Table** - Top problematic sensors
- 💡 **Key Insights** - Automated actionable recommendations

### Styling
- **Dark theme** with consistent color palette
- **High contrast text** for accessibility
- **Responsive layout** adapts to screen size
- **Custom CSS** using design tokens

## 🛠️ Tech Stack

**Machine Learning:**
- `scikit-learn` - Isolation Forest, Linear Regression
- `tensorflow` - CNN for acoustic classification
- `prophet` - Time-series forecasting

**Data Processing:**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations

**Visualization:**
- `streamlit` - Interactive dashboard framework
- `plotly` - Interactive charts and maps

**Development:**
- `uv` - Fast dependency management
- `black` - Code formatting
- `pytest` - Testing framework

## 📝 Usage Examples

### Cost Calculation
```python
from utils.helpers import calculate_leak_cost

# Calculate annual cost for a 3mm leak
annual_cost = calculate_leak_cost(leak_size_mm=3.0)
print(f"Annual cost: {annual_cost:,.2f} TND")
# Output: Annual cost: 12,450.00 TND
```

### Severity Classification
```python
from utils.helpers import classify_severity

severity = classify_severity(
    pressure_drop=8.5,  # PSI
    flow_deviation=75.0  # CFM
)
print(severity)  # Output: MEDIUM
```

### Real-Time Streaming
```python
from data.stream_data import StreamDataGenerator

generator = StreamDataGenerator()
generator.stream_forever(interval_seconds=5)
# Outputs JSONL to stdout every 5 seconds
```

## 🔧 Development

### Project Dependencies
All dependencies are managed via `pyproject.toml`:
- **Core:** pandas, numpy, scikit-learn, streamlit, plotly
- **ML:** tensorflow, prophet
- **Audio:** librosa, soundfile
- **Dev:** black, pytest, jupyter

### Adding New Dependencies
```bash
# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

## 🤝 Contributing

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add real-time streaming support"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Commit Message Convention
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style/formatting
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## 🎯 Key Highlights

### Why This Solution Stands Out

1. **💰 Financial Impact Focus**
   - Automatic cost calculation in local currency (TND)
   - ROI projections for maintenance decisions
   - Energy waste quantification

2. **🗺️ Intuitive Visualization**
   - Factory floor mapping with serial sensor placement
   - Pipeline routing visualization
   - Color-coded severity indicators

3. **🤖 Multi-Model ML Pipeline**
   - 5 specialized models working together
   - Anomaly detection → Severity → Cost → Confirmation → Prediction
   - Both supervised and unsupervised techniques

4. **⚡ Real-Time Ready**
   - JSONL streaming for Kafka/MQTT integration
   - Live data generation with realistic leak simulation
   - Scalable architecture for production deployment

5. **🎨 Production-Quality UI**
   - Dark theme with accessibility considerations
   - Interactive charts and maps
   - Actionable insights and recommendations

## 📚 Documentation

- **[Dashboard README](dashboard/README.md)** - Dashboard setup and features
- **[Model 01: Isolation Forest](models/01_isolation_forest/README.md)** - Anomaly detection
- **[Model 02: Severity Classifier](models/02_severity_classifier/README.md)** - Severity scoring
- **[Model 03: Leak Size Estimator](models/03_leak_size_estimator/README.md)** - Cost estimation
- **[Model 04: Acoustic Classifier](models/04_acoustic_classifier/README.md)** - Audio-based detection
- **[Model 05: Predictive Forecast](models/05_predictive_forecast/README.md)** - Time-series prediction

## 📄 License

This project is created for the IAS Hackathon 2026.

## 👥 Team

Built with ❤️ by the Silent Sabotage team

---

**⭐ Star this repo if you find it useful!**
