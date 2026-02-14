# Model 05: Predictive Leak Forecasting - Prophet/LSTM

**Team Member:** ___________  
**Priority:** 💡 Nice to Have (MAJOR DIFFERENTIATOR!)  
**Estimated Time:** 2-3 hours  
**Status:** 🔴 Not Started

## 📋 Your Task

Build a **time series forecasting model** to predict where leaks will occur in the next 30 days.

## 🎯 What It Does

This is your **secret weapon** for the hackathon pitch:
> *"Everyone else detects leaks. We **predict** them before they happen."*

- Analyzes historical leak patterns
- Incorporates pipe age, material, and environmental factors
- Forecasts probability of leak occurrence per zone
- Enables **proactive maintenance** instead of reactive repairs

## 💰 Business Impact

**Reactive Approach:**
```
Leak happens → Detect → Fix → $18K wasted energy
```

**Predictive Approach:**
```
Model predicts leak → Schedule inspection → Prevent → $18K SAVED
```

This model **sells the business case**!

## 📥 Inputs

### Time Series Data:
- Daily leak counts per zone
- Pressure trend patterns
- Flow rate variations over time

### Metadata (Optional but Powerful):
- `pipe_age_years` - Older pipes fail more often
- `pipe_material` - Steel vs. copper vs. PVC failure rates
- `joint_type` - Threaded joints more prone to leaks
- `temperature_cycling` - Thermal expansion/contraction stress
- `maintenance_history` - When was last inspection?

## 📤 Outputs

- **30-Day Forecast:** Probability of leak per zone (0-100%)
- **Expected Severity:** If a leak occurs, how bad will it be?
- **Recommended Actions:** Which zones to inspect first?
- **Confidence Intervals:** Upper/lower bounds on predictions

## ✅ Success Criteria

- **Precision:** > 0.70 (avoid false alarms that waste inspection time)
- **Recall:** > 0.60 (catch at least 60% of actual failures)
- **Actionable:** Outputs should directly inform maintenance schedule
- **Interpretable:** Business stakeholders should trust the model

## 🛠️ Approach: Prophet vs. LSTM

### **Option 1: Prophet (Recommended for Hackathon)**
✅ Pros:
- Fast to implement (~1-2 hours)
- Handles seasonality automatically
- Provides confidence intervals
- Works well with limited data

❌ Cons:
- Less flexible for multiple features

### **Option 2: LSTM (If You Have Time)**
✅ Pros:
- Can incorporate many features
- Learns complex patterns
- Impressive to judges

❌ Cons:
- 2-3 hours minimum
- Requires more data
- Harder to interpret

**For this hackathon: Start with Prophet. If you finish early, try LSTM.**

## 🚀 Quick Start

### 1. Generate Data
```bash
cd ../..
python data/generate_data.py
```

### 2. Train Prophet Model
```bash
python train.py
```

### 3. Expected Output
```
🎯 Training model for Zone_A...
   Initial training: 7 days, 12 total leaks
   
🎯 Training model for Zone_B...
   Initial training: 7 days, 8 total leaks

📊 30-Day Forecast Summary:
   Zone_A: 68% leak probability (HIGH RISK)
   Zone_B: 42% leak probability (MEDIUM RISK)
   Zone_C: 23% leak probability (LOW RISK)
   Zone_D: 71% leak probability (HIGH RISK)

✅ Models saved to: models/05_predictive_forecast/
📈 Forecast chart saved to: forecast_visualization.png
```

## 📊 Prophet Implementation

### Basic Setup:
```python
from prophet import Prophet

# Prepare data
df_prophet = df[['timestamp', 'is_anomaly']].copy()
df_prophet.columns = ['ds', 'y']  # Prophet requires these names
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

# Aggregate to daily leak counts
daily_leaks = df_prophet.groupby(df_prophet['ds'].dt.date)['y'].sum().reset_index()

# Initialize and train
model = Prophet(
    yearly_seasonality=False,
    weekly_seasonality=True,
    daily_seasonality=False,
    interval_width=0.95
)
model.fit(daily_leaks)

# Forecast 30 days
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
```

### Adding Regressors (Pipe Age, Material, etc.):
```python
# Add metadata as additional features
model = Prophet()
model.add_regressor('pipe_age_years')
model.add_regressor('temperature_cycling')

# Prepare training data with regressors
df_with_regressors = df.merge(metadata, on='sensor_id')
model.fit(df_with_regressors[['ds', 'y', 'pipe_age_years', 'temperature_cycling']])
```

## 📊 Visualizations to Create

### 1. **Forecast Chart (Per Zone)**
```python
import matplotlib.pyplot as plt

fig = model.plot(forecast)
plt.title(f'Zone {zone} - 30-Day Leak Forecast')
plt.xlabel('Date')
plt.ylabel('Expected Daily Leaks')
plt.axvline(x=pd.to_datetime('today'), color='r', linestyle='--', label='Today')
plt.legend()
plt.savefig(f'forecast_{zone}.png')
```

### 2. **Component Analysis**
```python
# Show trend, weekly patterns, etc.
fig = model.plot_components(forecast)
plt.savefig('forecast_components.png')
```

### 3. **Risk Heatmap**
```python
import seaborn as sns

risk_matrix = pd.DataFrame({
    'Zone': zones,
    'Leak Probability (%)': [68, 42, 23, 71],
    'Expected Severity': ['HIGH', 'MEDIUM', 'LOW', 'CRITICAL']
})

plt.figure(figsize=(8, 6))
sns.heatmap(risk_matrix[['Leak Probability (%)']].T, 
            annot=True, cmap='RdYlGn_r', cbar=True)
plt.title('30-Day Leak Risk by Zone')
plt.savefig('risk_heatmap.png')
```

### 4. **Maintenance Schedule**
```python
# Automatically generate inspection priorities
inspection_schedule = []
for zone, prob in zip(zones, leak_probabilities):
    if prob > 0.60:
        priority = "URGENT - Inspect within 3 days"
    elif prob > 0.40:
        priority = "MEDIUM - Inspect within 2 weeks"
    else:
        priority = "LOW - Routine inspection"
    
    inspection_schedule.append({
        'zone': zone,
        'probability': prob,
        'priority': priority
    })
```

## 💡 Advanced Features

### 1. **Pipe Age Impact**
```python
# Older pipes = higher failure probability
# This adds huge value to the model!

metadata['failure_multiplier'] = 1 + (metadata['pipe_age_years'] / 10) * 0.5
# 10-year-old pipe = 1.5x more likely to fail than new pipe
```

### 2. **Material-Specific Models**
```python
# Different materials age differently
material_models = {}

for material in ['steel', 'copper', 'pvc']:
    material_data = df[df['pipe_material'] == material]
    material_models[material] = Prophet()
    material_models[material].fit(material_data)
```

### 3. **Temperature Cycling Stress**
```python
# Calculate thermal stress factor
df['temp_range_daily'] = df.groupby(df['timestamp'].dt.date)['temperature_c'].transform(
    lambda x: x.max() - x.min()
)

# Large daily temperature swings → more stress on joints
model.add_regressor('temp_range_daily')
```

## 🔍 Model Validation

### Backtesting:
```python
# Train on first 5 days, test on last 2 days
train_df = df[df['timestamp'] < '2026-02-12']
test_df = df[df['timestamp'] >= '2026-02-12']

model.fit(train_df)
predictions = model.predict(test_df)

# Compare predicted vs actual leak counts
from sklearn.metrics import mean_absolute_error

mae = mean_absolute_error(test_df['y'], predictions['yhat'])
print(f"Mean Absolute Error: {mae:.2f} leaks/day")
```

## 🎯 Integration with Dashboard

Your forecast will power the dashboard's **Predictive Maintenance** tab:

```python
# Export forecast for dashboard
forecast_summary = {
    "generated_at": datetime.now().isoformat(),
    "forecast_period_days": 30,
    "zones": [
        {
            "zone": "Zone_A",
            "leak_probability": 0.68,
            "expected_leaks": 8,
            "confidence_interval": [5, 12],
            "recommended_action": "Schedule inspection within 3 days",
            "estimated_prevention_savings": "$45,000"
        },
        # ... more zones
    ]
}

with open('forecast_summary.json', 'w') as f:
    json.dump(forecast_summary, f, indent=2)
```

## 📊 Sample Output

```json
{
  "zone": "Zone_A",
  "forecast_date": "2026-03-15",
  "leak_probability": 0.68,
  "expected_severity": "HIGH",
  "confidence_interval_lower": 0.52,
  "confidence_interval_upper": 0.84,
  "contributing_factors": {
    "pipe_age_years": 15,
    "recent_leak_trend": "increasing",
    "temperature_cycling": "high",
    "material": "steel"
  },
  "recommended_actions": [
    "Inspect Zone A sensors S007-S009 within 3 days",
    "Check threaded joints near high-temperature equipment",
    "Prepare replacement parts for 3-5mm leak repair"
  ],
  "estimated_prevention_savings": "$18,500"
}
```

## 🐛 Troubleshooting

**Prophet won't install:**
```bash
# Try this instead
pip install prophet --no-cache-dir

# Or use conda
conda install -c conda-forge prophet
```

**"Insufficient data" error:**
- You need at least 2-3 days of data
- Run `generate_data.py` with `num_days=7`

**Flat predictions (no variation):**
- Add seasonality: `weekly_seasonality=True`
- Add regressors (pipe age, material)
- Check if you have actual variation in the data

**Unrealistic probabilities (> 1.0 or < 0.0):**
```python
# Clip to valid range
forecast['leak_probability'] = forecast['yhat'].clip(0, 1)
```

## 📝 Deliverables

- [ ] Trained Prophet models (one per zone)
- [ ] 30-day forecast data (CSV or JSON)
- [ ] Forecast visualization charts
- [ ] Risk heatmap by zone
- [ ] Maintenance schedule recommendation
- [ ] Model validation metrics (MAE, precision, recall)
- [ ] Brief write-up of which features were most predictive

## 🚀 Bonus Challenges

### 1. **Anomaly Detection in Forecast**
```python
# Flag when predicted leak rate suddenly spikes
forecast['is_spike'] = forecast['yhat'] > forecast['yhat'].rolling(7).mean() * 2
```

### 2. **Cost-Benefit Analysis**
```python
# Show ROI of predictive maintenance
inspection_cost = 500  # per zone
average_leak_cost = 18000
expected_savings = leak_probability * average_leak_cost - inspection_cost
```

### 3. **LSTM Alternative**
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

model = Sequential([
    LSTM(64, input_shape=(lookback_days, num_features)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])
```

## 🎤 Pitch Deck Slide

**Title:** "We Don't Just Find Leaks. We Predict Them."

**Visual:** Risk heatmap + 30-day forecast chart

**Key Message:**
- "Our AI forecasts leak probability 30 days in advance"
- "Enables proactive maintenance vs. reactive repairs"
- "Average savings: $18K per prevented leak"
- "Zone A has 68% leak probability - inspect within 3 days"

---

**Questions?** This model wins hackathons. Make it shine! 🏆
