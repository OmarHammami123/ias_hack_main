# Model 01: Isolation Forest - Anomaly Detection

**Team Member:** ___________  
**Priority:** ✅ Must Have  
**Estimated Time:** 1-2 hours  
**Status:** 🔴 Not Started

## 📋 Your Task

Build an **Isolation Forest** model to detect anomalous sensor readings that may indicate leaks.

## 🎯 What It Does

- Analyzes pressure, flow, and temperature sensor readings
- Identifies abnormal patterns that deviate from "normal" operation
- Flags potential leaks for further investigation
- First line of defense in the detection pipeline

## 📥 Inputs

- `pressure_psi` - Pressure reading in PSI
- `humidity_percent` - Humidity reading in percentage (0-100%)
- `temperature_c` - Temperature in Celsius
- Optional: Derived features (rolling averages, rate of change, etc.)

## 📤 Outputs

- Binary classification: `anomaly` (1) or `normal` (0)
- Anomaly score: Continuous value indicating how anomalous the reading is
- Higher score = more likely to be a leak

## ✅ Success Criteria

- **Accuracy:** > 90%
- **False Positive Rate:** < 10% (we don't want too many false alarms)
- **Inference Time:** < 100ms per batch
- Model should generalize to unseen zones and time periods

## 🚀 Quick Start

### 1. Generate Data First
```bash
cd ../..  # Go to project root
python data/generate_data.py
```

### 2. Train the Model
```bash
python train.py
```

### 3. Expected Output
```
✅ Model saved to: models/01_isolation_forest/isolation_forest_model.pkl
📊 Accuracy: 92.3%
⚠️  False Positive Rate: 8.1%
```

## 💡 Feature Engineering Ideas

The current implementation uses basic features. **Bonus points** if you add:

1. **Rolling Statistics**
   ```python
   df['pressure_rolling_mean'] = df['pressure_psi'].rolling(window=60).mean()
   df['pressure_rolling_std'] = df['pressure_psi'].rolling(window=60).std()
   ```

2. **Rate of Change**
   ```python
   df['pressure_derivative'] = df['pressure_psi'].diff()
   df['humidity_derivative'] = df['humidity_percent'].diff()
   ```

3. **Time-Based Features**
   ```python
   df['hour_of_day'] = df['timestamp'].dt.hour
   df['is_night_shift'] = (df['hour_of_day'] >= 22) | (df['hour_of_day'] < 6)
   ```

4. **Zone-Specific Baselines**
   ```python
   # Calculate mean pressure per zone, then find deviation
   zone_baselines = df.groupby('zone')['pressure_psi'].mean()
   df['pressure_deviation'] = df.apply(...)
   ```

## 🔍 How to Test Your Model

1. **Check confusion matrix** - Make sure True Positives >> False Positives
2. **Test on different zones** - Does it work across all zones?
3. **Simulate real-time** - Pick a random time window and predict

## 📚 Resources

- [Isolation Forest Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Understanding Isolation Forest](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)

## 🐛 Troubleshooting

**Model predicts everything as anomaly:**
- Your `contamination` parameter is too high
- Try lowering it to 0.05 or 0.01

**Too many false positives:**
- Add more features (rolling stats, derivatives)
- Increase training data quality
- Tune `n_estimators` parameter

**Model is too slow:**
- Reduce `n_estimators` from 100 to 50
- Sample your data if it's huge

## 📝 Deliverables

- [ ] Trained model saved as `isolation_forest_model.pkl`
- [ ] Scaler saved as `scaler.pkl`
- [ ] Training metrics report (accuracy, precision, recall)
- [ ] Feature importance or visualization (optional)
- [ ] Brief comment in your code explaining any improvements you made

---

**Questions?** Ask your team or check the main README.md
