# 👥 Team Collaboration Guide

**Project:** Silent Sabotage - Industrial Leak Detection System  
**Hackathon:** IAS Hackathon (Theme 03)  
**Date:** February 14, 2026

---

## 🎯 Quick Start for Team Members

> **⚡ Pro Tip:** We're using [uv](https://github.com/astral-sh/uv) for package management - it's 10-100x faster than pip!

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ias_hack_main
```

### 2. Set Up Your Environment
```bash
# Install uv if you don't have it
pip install uv

# Sync dependencies (creates venv + installs everything!)
uv sync

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

> **What just happened?** `uv sync` created a `.venv` folder, installed all packages from `pyproject.toml`, and created a lockfile (`uv.lock`) for reproducible builds.

### 3. Generate Data (EVERYONE DO THIS FIRST!)
```bash
python data/generate_data.py
```

This creates:
- `data/raw/pressure_sensor_data.csv` (~1.6M rows)
- `data/raw/acoustic_sensor_data.csv` (~160K rows)
- `data/raw/sensor_metadata.csv` (28 sensors)

### 4. Choose Your Model
See task assignments below ⬇️

---

## 👥 Task Assignments

| Team Member | Model | Priority | Time | Status |
|-------------|-------|----------|------|--------|
| **Member 1** | [01 - Isolation Forest](models/01_isolation_forest/README.md) | ✅ Must Have | 1-2h | 🔴 Not Started |
| **Member 2** | [02 - Severity Classifier](models/02_severity_classifier/README.md) | ✅ Must Have | 30min | 🔴 Not Started |
| **Member 3** | [03 - Leak Size Estimator](models/03_leak_size_estimator/README.md) | ⚠️ Should Have | 1h | 🔴 Not Started |
| **Member 4** | [04 - Acoustic Classifier](models/04_acoustic_classifier/README.md) | 💡 Nice to Have | 2-3h | 🔴 Not Started |
| **Member 5** | [05 - Predictive Forecast](models/05_predictive_forecast/README.md) | 💡 Differentiator | 2-3h | 🔴 Not Started |
| **ALL** | [Dashboard](dashboard/README.md) | ✅ Must Have | 3-4h | 🔴 Not Started |

### How to Update Your Status:
```bash
# Edit this file and push
git add TEAM_GUIDE.md
git commit -m "Update: Started working on Model 01"
git push
```

---

## 🔄 Git Workflow

### Branch Naming Convention:
```
model-01-isolation-forest
model-02-severity
model-03-leak-size
model-04-acoustic
model-05-forecast
dashboard
```

### Workflow:
```bash
# 1. Create your branch
git checkout -b model-01-isolation-forest

# 2. Work on your model
cd models/01_isolation_forest
python train.py

# 3. Save your trained model
# Models are .gitignored, so save to shared drive or cloud

# 4. Commit your code (NOT the model file)
git add train.py
git commit -m "Feat: Isolation Forest with rolling features"

# 5. Push to GitHub
git push origin model-01-isolation-forest

# 6. Create Pull Request
# Go to GitHub and create PR to main
```

### What to Commit:
✅ **DO commit:**
- Code files (`.py`)
- README updates
- Configuration changes
- Notebooks (`.ipynb`)
- Small sample outputs (< 1MB)

❌ **DON'T commit:**
- Large data files (`.csv`, `.json`) - already in `.gitignore`
- Model artifacts (`.pkl`, `.h5`, `.pt`) - already in `.gitignore`
- Virtual environment (`venv/`) - already in `.gitignore`

---

## 📋 Daily Standup Checklist

### Morning (9:00 AM)
- [ ] Pull latest changes: `git pull origin main`
- [ ] Review your model's README
- [ ] Check if data is generated: `ls data/raw/`
- [ ] Set up your branch
- [ ] Post in team chat: "Working on Model X today"

### Midday (1:00 PM)
- [ ] Commit progress: `git add . && git commit -m "WIP: Model training"`
- [ ] Update status in this file
- [ ] Help others if you're ahead of schedule

### Evening (6:00 PM)
- [ ] Finalize your model
- [ ] Create Pull Request
- [ ] Document any issues or improvements
- [ ] Help with dashboard integration

---

## 🆘 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'utils'"
**Solution:**
```python
# Add this at the top of your train.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
```

### Issue 2: "FileNotFoundError: data/raw/pressure_sensor_data.csv"
**Solution:**
```bash
# Generate data first!
cd ../..  # Go to project root
python data/generate_data.py
```

### Issue 3: "Package not found" or import errors
**Solution:**
```bash
# Make sure environment is synced
uv sync

# Verify you're in the right environment
which python  # Mac/Linux
where python  # Windows
# Should show .venv/bin/python or .venv\Scripts\python.exe
```

### Issue 4: Prophet installation fails
**Solution:**
```bash
# Add prophet with uv
uv add prophet==1.1.4

# Or use conda instead
conda install -c conda-forge prophet
```

### Issue 5: TensorFlow/Keras issues (Model 04)
**Solution:**
```bash
# Add specific versions with uv
uv add tensorflow==2.13.0
uv add keras==2.13.1
```

---

## 🎯 Model Integration Points

### Model 01 → Model 02
```python
# Model 01 detects anomalies
anomalies = isolation_forest.predict(data)

# Model 02 classifies severity
for anomaly in anomalies:
    severity = severity_classifier.classify(anomaly)
```

### Model 02 → Model 03
```python
# Model 02 provides severity
severity, pressure_drop, flow_dev = model_02_output

# Model 03 estimates leak size
leak_size = leak_estimator.predict(pressure_drop, flow_dev)
```

### Model 01 + Model 04 (Multi-Modal)
```python
# Combine pressure and acoustic
pressure_anomaly = model_01.predict(pressure_data)
acoustic_leak = model_04.predict(acoustic_data)

# High confidence when both agree
if pressure_anomaly and acoustic_leak > 0.8:
    confidence = "CONFIRMED"
```

### Model 05 → Dashboard
```python
# Forecast feeds into predictive tab
forecast = model_05.predict_next_30_days()

# Dashboard displays risk heatmap
dashboard.show_risk_heatmap(forecast)
```

---

## 📊 Dashboard Integration

### Each Model Should Export:
```python
# Example output format
output = {
    "model_name": "isolation_forest",
    "version": "1.0",
    "predictions": [
        {
            "timestamp": "2026-02-14T10:30:00Z",
            "zone": "Zone_A",
            "is_anomaly": True,
            "anomaly_score": -0.15,
            "confidence": 0.92
        },
        # ... more predictions
    ],
    "metrics": {
        "accuracy": 0.923,
        "precision": 0.89,
        "recall": 0.87
    }
}

# Save to JSON
import json
with open('model_output.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### Dashboard Will Load:
```python
# dashboard/app.py
def load_model_outputs():
    outputs = {}
    for model_dir in Path('models').iterdir():
        output_file = model_dir / 'model_output.json'
        if output_file.exists():
            outputs[model_dir.name] = json.load(open(output_file))
    return outputs
```

---

## 💡 Tips for Success

### For Model Developers:
1. **Read your model's README first** - It has everything you need
2. **Start simple, iterate** - Get a baseline working, then improve
3. **Save checkpoints** - Commit code frequently
4. **Document your choices** - Brief comments explaining hyperparameters
5. **Test edge cases** - What if pressure_drop is 0? Negative?

### For Dashboard Developer:
1. **Start with static mockup** - Hardcode some values first
2. **Add interactivity** - Filters, date pickers, etc.
3. **Make it visual** - Colors, charts, animations
4. **Test with real data** - Load actual CSV outputs from models
5. **Prepare for demo** - Practice your walkthrough

### For Everyone:
1. **Communicate often** - Team chat is your friend
2. **Help each other** - Finished early? Help someone else
3. **Think about the pitch** - How does your work fit the story?
4. **Keep it simple** - Working > Perfect
5. **Have fun!** - This is a hackathon, enjoy the process

---

## 🏆 Success Metrics

### Minimum Viable Product (MVP):
- [ ] Models 01 and 02 working (detection + severity)
- [ ] Basic dashboard showing factory status
- [ ] Clear pitch deck explaining the solution
- [ ] Live demo ready

### Target (Competitive):
- [ ] Models 01, 02, 03 working (add leak size estimation)
- [ ] Dashboard with analytics and visualizations
- [ ] Model performance metrics displayed
- [ ] Professional pitch with business case

### Stretch Goal (Winning):
- [ ] All 5 models working
- [ ] Predictive forecasting integrated
- [ ] Multi-modal detection (pressure + acoustic)
- [ ] Polished dashboard with real-time updates
- [ ] Compelling pitch with ROI calculations

---

## 📞 Communication Channels

### Team Chat:
- Quick questions
- Status updates
- Blocker notifications

### GitHub Issues:
- Bug reports
- Feature requests
- Technical discussions

### Stand-ups:
- Morning: What are you working on?
- Evening: What did you accomplish?

---

## 🎤 Pitch Deck Outline

### Slide 1: The Problem
- "$X billion lost annually to compressed air leaks"
- "Most factories don't know where their energy is going"

### Slide 2: Our Solution
- "AI-powered leak detection system"
- "Detect, localize, and predict leaks before they happen"

### Slide 3: How It Works
- Multi-modal detection (pressure + acoustic)
- Machine learning models
- Real-time dashboard

### Slide 4: The Innovation
- **Predictive forecasting** - "We predict leaks 30 days in advance"
- **Multi-modal** - "Pressure + Acoustic = 95% accuracy"
- **Business intelligence** - "Track ROI and energy efficiency"

### Slide 5: Demo
- Live dashboard walkthrough
- Show a critical leak
- Show predictive forecast

### Slide 6: Impact
- "$85K annual savings for typical factory"
- "12% energy efficiency improvement"
- "ROI in 6 months"

### Slide 7: Team & Next Steps
- Meet the team
- Future roadmap
- Thank you

---

**Questions?** Ask in the team chat or check the main [README.md](README.md)

**Let's build something amazing! 🚀**
