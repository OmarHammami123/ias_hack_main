# Model 03: Leak Size Estimator - Linear Regression

**Team Member:** ___________  
**Priority:** ⚠️ Should Have  
**Estimated Time:** 1 hour  
**Status:** 🔴 Not Started

## 📋 Your Task

Build a **Linear Regression** model to estimate the physical leak size (diameter in mm) from sensor readings.

## 🎯 What It Does

- Takes pressure drop and flow deviation measurements
- Estimates the actual hole size causing the leak
- Enables accurate cost calculations and repair planning
- Validates physics-based assumptions

## 📥 Inputs

- `pressure_drop` - PSI difference from baseline
- `flow_deviation` - CFM difference from baseline
- `temperature_c` - Ambient temperature
- Optional: pipe diameter, material, age

## 📤 Outputs

- **Leak Diameter:** Estimated size in millimeters (e.g., 3.5mm)
- **Confidence Interval:** Range of likely values (e.g., 2.8-4.2mm)
- **Annual Cost:** Calculated from estimated leak size

## ✅ Success Criteria

- **R² Score:** > 0.80 (model explains 80%+ of variance)
- **RMSE:** < 1mm for small leaks (< 5mm)
- **Realistic Estimates:** No negative values, reasonable size range (0.5-10mm)

## 🧪 The Physics Behind It

The model is based on orifice flow equations:

```
Q = Cd × A × √(2 × ΔP / ρ)

where:
  Q = volumetric flow rate (CFM)
  Cd = discharge coefficient (~0.6 for sharp orifice)
  A = cross-sectional area of leak (π × r²)
  ΔP = pressure drop (PSI converted to Pa)
  ρ = air density (~1.2 kg/m³)
```

**Your regression model learns this relationship from data.**

## 🚀 Quick Start

### 1. Generate Data
```bash
cd ../..
python data/generate_data.py
```

### 2. Train the Model
```bash
python train.py
```

### 3. Expected Output
```
📊 Model Performance:
   R² Score: 0.87
   RMSE: 0.64mm
   MAE: 0.51mm

✅ Model saved to: leak_size_model.pkl
📈 Scatter plot saved to: predictions_vs_actual.png
```

## 💡 Feature Engineering Ideas

### 1. **Polynomial Features**
The relationship might not be perfectly linear:
```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
```

### 2. **Derived Features**
```python
# Pressure-flow ratio
df['pressure_flow_ratio'] = df['pressure_drop'] / (df['flow_deviation'] + 1)

# Flow per PSI drop
df['flow_per_psi'] = df['flow_deviation'] / (df['pressure_drop'] + 1)
```

### 3. **Physics-Based Features**
```python
# Theoretical leak area (from orifice equation)
df['theoretical_area'] = df['flow_deviation'] / np.sqrt(df['pressure_drop'])
```

## 📊 Visualizations to Create

### 1. **Predictions vs Actual**
```python
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([0, 10], [0, 10], 'r--')  # Perfect prediction line
plt.xlabel('Actual Leak Size (mm)')
plt.ylabel('Predicted Leak Size (mm)')
plt.title('Leak Size Predictions')
plt.savefig('predictions_vs_actual.png')
```

### 2. **Residuals Plot**
```python
residuals = y_test - y_pred
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Leak Size (mm)')
plt.ylabel('Residuals (mm)')
plt.title('Residual Analysis')
plt.savefig('residuals.png')
```

### 3. **Feature Importance**
```python
# For linear regression, coefficients = feature importance
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'coefficient': model.coef_
}).sort_values('coefficient', ascending=False)
```

## 🔍 Model Validation

### Test These Cases:

**1. Small Leaks (< 2mm)**
```python
test_small = df[df['leak_size_mm'] < 2]
# Should have low error here
```

**2. Large Leaks (> 5mm)**
```python
test_large = df[df['leak_size_mm'] > 5]
# Check if estimates are still reasonable
```

**3. Different Zones**
```python
for zone in zones:
    zone_data = df[df['zone'] == zone]
    # Model should work across all zones
```

## 🎯 Integration Points

Your model will be used by:
- **Model 02 (Severity Classifier)** - More accurate cost estimation
- **Dashboard** - Display leak size visually
- **Maintenance Reports** - Specify exact parts needed for repair

## 📊 Sample Output

```json
{
  "leak_id": "LEAK_001",
  "estimated_size_mm": 3.2,
  "confidence_interval_lower": 2.7,
  "confidence_interval_upper": 3.8,
  "pressure_drop": 12.5,
  "flow_deviation": 125.3,
  "annual_cost_usd": 18500,
  "repair_difficulty": "minor",
  "recommended_action": "Schedule during next maintenance window"
}
```

## 🐛 Troubleshooting

**Negative predictions:**
```python
# Clip predictions to physical limits
predictions = np.clip(predictions, 0.5, 10)
```

**High RMSE:**
- Try polynomial features
- Add more derived features
- Check for outliers in training data
- Consider Ridge/Lasso regression for regularization

**Model doesn't generalize:**
- Check if you're overfitting
- Increase training data
- Remove highly correlated features

## 📝 Deliverables

- [ ] Trained regression model (`leak_size_model.pkl`)
- [ ] Feature scaler (`scaler.pkl`)
- [ ] Model performance metrics (R², RMSE, MAE)
- [ ] Predictions vs Actual scatter plot
- [ ] Residuals analysis plot
- [ ] Brief write-up of any improvements you made

## 🚀 Bonus Challenge

Can you add **confidence intervals** to your predictions?

```python
from sklearn.linear_model import BayesianRidge

# This gives you uncertainty estimates!
model = BayesianRidge()
predictions, std_dev = model.predict(X, return_std=True)
```

---

**Questions?** Check the physics formulas in `utils/helpers.py` or ask your team.
