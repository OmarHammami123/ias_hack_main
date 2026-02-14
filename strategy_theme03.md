# 🎯 Theme 03 Strategy — The Silent Sabotage (Chosen Approach)

---

## Detection Approaches — Ranked

| Approach | Feasibility | Impressiveness | Hackathon Verdict |
|---|---|---|---|
| **Pressure & Flow Analysis** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ **#1 PICK — Do this** |
| **Acoustic / Ultrasonic Sensing** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **#2 PICK — Combine with #1** |
| **Vibration Analysis** | ⭐⭐⭐ | ⭐⭐⭐ | ⚠️ Possible but adds complexity |
| **Thermal Imaging** | ⭐⭐ | ⭐⭐⭐⭐ | ❌ Hard to simulate, needs real hardware |
| **Automated Soap Bubble Robot** | ⭐ | ⭐⭐⭐⭐⭐ | ❌ Cool idea but impossible in 24h |

### Why Pressure & Flow is #1
- **Easiest to simulate** — you just generate numbers (pressure values at different pipe points)
- **Most realistic** — this is what real factories actually deploy first
- **Clear logic** — "pressure drops between sensor A and sensor B = leak between them." Judges understand it instantly
- **No special hardware** — pressure sensors are the cheapest and most common industrial sensors
- **Night shift trick** — monitor flow when the factory is idle. Any flow = pure waste. Simple, smart insight

### Why Acoustic is #2 (Combine it)
- You can simulate it by generating audio spectrograms or frequency data
- CNN on spectrograms is a well-known ML pattern — lots of tutorials exist, fast to implement
- It gives you a **second modality** — judges love multi-sensor fusion
- The pitch sounds impressive: *"We listen for leaks the same way a doctor listens for heart murmurs"*

### What to Skip
- **Thermal imaging** — can't simulate it convincingly without real IR camera footage
- **Vibration** — adds a third sensor type without much extra value for the demo
- **Soap bubble robot** — fun to mention in your pitch as "future work" but don't try to build it

---

## Localization Strategies — Ranked

| Strategy | Feasibility | Impressiveness | Hackathon Verdict |
|---|---|---|---|
| **Zone-Based Isolation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ **#1 PICK — Simple and real** |
| **Pressure Gradient Mapping** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **#2 PICK — Great visual** |
| **Triangulation (TDoA)** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ Math is doable but risky under time pressure |
| **Digital Twin** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ Too ambitious for 24h |

### Why Zone-Based Isolation is #1
- Simplest to explain and implement
- Divide factory into zones on a map → each zone has sensors → the zone with anomalous readings contains the leak
- Dashboard shows a **factory floor map with colored zones** (green = OK, yellow = warning, red = leak detected)
- No complex math needed

### Why Pressure Gradient Mapping is #2
- Place sensors at intervals along a pipe → plot pressure values → the dip in the graph = leak location
- Produces a **beautiful visualization**: a line chart showing pressure along the pipe with a clear valley where the leak is
- Judges love visuals. This one tells the story instantly

### What to Skip
- **Triangulation** — the TDoA math is doable but debugging it under time pressure is risky. Mention it as a "Phase 2 enhancement"
- **Digital Twin** — sounds amazing in the pitch but building a real one in 24h is a trap. You'll spend all your time on the 3D model and have no ML to show

---

## The Winning Combination

```
DETECTION:     Pressure & Flow Analysis + Acoustic Classification
LOCALIZATION:  Zone-Based Isolation + Pressure Gradient Visualization
PRIORITIZATION: Cost-Based Ranking (leak size → annual $ waste)
```

### How It Flows Together

```
Pressure sensors detect anomaly in Zone 3
        ↓
Acoustic sensor in Zone 3 confirms: leak signature detected
        ↓
Pressure gradient along Zone 3 pipes → leak is between sensor S007 and S008
        ↓
Estimated leak size: 3mm → Annual waste: $18,000 → Priority: HIGH
        ↓
Dashboard alert + maintenance notification with exact location
```

---

## Innovation Angles — Ranked for Hackathon

| Idea | Build in 24h? | Judge Impact |
|---|---|---|
| **Factory-wide energy dashboard** | ✅ Yes (Streamlit) | ⭐⭐⭐⭐ |
| **Predictive leak forecasting** | ✅ Yes (simple LSTM/Prophet) | ⭐⭐⭐⭐⭐ |
| **Self-organizing sensor mesh** | ⚠️ Simulatable on Wokwi | ⭐⭐⭐ |
| **AR maintenance view** | ✅ As a UI mockup/Figma | ⭐⭐⭐⭐ |
| **Autonomous patrol robot** | ❌ No | ⭐⭐⭐⭐⭐ |
| **Closed-loop automated valves** | ⚠️ Simulatable | ⭐⭐⭐⭐ |
| **RL for valve optimization** | ❌ No | ⭐⭐⭐⭐⭐ |

### Top 2 Innovation Picks

**1. Predictive Leak Forecasting** — This is your differentiator. Everyone else will do detection. You go one step further: *"We don't just find leaks. We predict where the next one will happen."*
- Use pipe age, material, joint type, temperature cycling history as features
- Even a simple random forest that outputs "probability of leak in next 30 days per pipe segment" is enough
- One extra slide in your pitch. Massive impact

**2. Energy Dashboard with Efficiency Score** — This sells the business case
- Show: total energy input → useful work → detected leaks → unknown losses
- A single percentage: *"Your factory is running at 71% air efficiency. Industry best practice is 90%."*
- Gamification: track the score going up as leaks get fixed

---

## AI/ML Model — What to Actually Build

| Model | What It Does | Time to Build | Priority |
|---|---|---|---|
| **Isolation Forest** | Detects anomalous sensor readings | 1-2 hours | ✅ Must have |
| **Threshold + Rules** | Classifies severity (small/medium/large) | 30 min | ✅ Must have |
| **Linear Regression** | Estimates leak size from pressure drop | 1 hour | ✅ Should have |
| **CNN on Spectrograms** | Classifies audio as leak vs. no-leak | 2-3 hours | ⚠️ Nice to have |
| **Prophet/LSTM** | Predicts future leaks from trends | 2-3 hours | ⚠️ Nice to have (differentiator) |
|

### The Realistic ML Stack for 24 Hours

1. **Isolation Forest** for anomaly detection (scikit-learn, fast)
2. **Rule-based severity scoring** (if pressure_drop > X and flow_deviation > Y → severity = HIGH)
3. **Simple regression** for leak cost estimation (leak size → kWh wasted → dollars)
4. **If time permits**: Prophet time series forecast for predictive angle

---

## 24-Hour Sprint Plan

| Hours | What to Do |
|---|---|
| 0–2 | Architecture diagram, role assignment, GitHub setup |
| 2–5 | Generate synthetic data, build Isolation Forest + severity scoring |
| 5–8 | Build Streamlit dashboard with factory map + zone visualization |
| 8–11 | Add pressure gradient chart, priority table, energy KPIs |
| 11–14 | IoT simulation (Wokwi ESP32 sending JSON), connect to dashboard |
| 14–17 | Polish: add predictive forecast chart, refine UI, fix bugs |
| 17–20 | Build pitch deck, write 2-page PDF summary |
| 20–22 | Record 1-min video, rehearse 5-min pitch |
| 22–24 | Final polish, submit everything, prepare for Q&A |

---

## Bottom Line

Focus on **Pressure + Flow + Zones + Dashboard + Business Numbers**. That's the winning formula.
