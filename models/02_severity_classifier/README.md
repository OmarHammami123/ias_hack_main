# Model 02: Severity Classifier - Rule-Based System

**Team Member:** ___________  
**Priority:** ✅ Must Have  
**Estimated Time:** 30 minutes  
**Status:** 🔴 Not Started

## 📋 Your Task

Build a **rule-based classifier** to categorize detected leaks by severity level.

## 🎯 What It Does

- Takes an anomaly detected by Model 01
- Calculates how severe the leak is based on pressure drop and flow deviation
- Assigns a priority level: CRITICAL, HIGH, MEDIUM, or LOW
- Helps maintenance teams prioritize which leaks to fix first

## 📥 Inputs

- `pressure_drop` - Difference from baseline pressure (PSI)
- `flow_deviation` - Difference from baseline flow (CFM)
- `zone` - Which zone the leak is in
- Optional: leak duration, time of day

## 📤 Outputs

- **Severity Level:** CRITICAL, HIGH, MEDIUM, or LOW
- **Priority Score:** 0-100 (higher = more urgent)
- **Estimated Annual Cost:** Dollar amount lost per year

## ✅ Success Criteria

- **Clear Rules:** Anyone should be able to understand why a leak is classified as CRITICAL
- **Fast Inference:** < 1ms per classification
- **Business Alignment:** Cost estimates should be realistic

## 🎨 Severity Rules (Current Thresholds)

| Severity | Pressure Drop | Flow Deviation | Priority Score |
|----------|---------------|----------------|----------------|
| CRITICAL | > 20 PSI | > 200 CFM | 100 |
| HIGH | 10-20 PSI | 100-200 CFM | 75 |
| MEDIUM | 5-10 PSI | 50-100 CFM | 50 |
| LOW | < 5 PSI | < 50 CFM | 25 |

**Note:** If *either* condition is met, the higher severity applies.

## 🚀 Quick Start

### 1. Generate Data First
```bash
cd ../..  # Go to project root
python data/generate_data.py
```

### 2. Run the Classifier
```bash
python train.py
```

### 3. Expected Output
```
📊 Severity Distribution:
   CRITICAL: 15 leaks ($183,450/year)
   HIGH: 42 leaks ($312,800/year)
   MEDIUM: 89 leaks ($145,200/year)
   LOW: 124 leaks ($28,500/year)

✅ Classification report saved to: severity_report.json
```

## 💡 Enhancement Ideas

This is a simple rule-based system, but you can make it smarter:

### 1. **Zone-Specific Rules**
```python
# Critical zones (near expensive equipment) get higher priority
if zone in ["Zone_A", "Zone_C"]:
    priority_score *= 1.5
```

### 2. **Time-Based Adjustments**
```python
# Night shift leaks = pure waste (no production happening)
if is_night_shift:
    priority_score += 20  # Bump priority
```

### 3. **Duration Factor**
```python
# Leaks that have been going on for days are worse
if leak_duration_hours > 48:
    severity = upgrade_severity(severity)
```

### 4. **Cascade Effect**
```python
# Multiple leaks in same zone = infrastructure problem
if zone_leak_count > 3:
    priority_score += 25
```

## 📊 Cost Calculation

The classifier estimates annual cost using this formula:

```python
# Simplified version:
cfm_loss = estimate from pressure drop and flow deviation
kw_wasted = cfm_loss * 0.25  # Energy to compress air
kwh_per_year = kw_wasted * 8760  # 24/7 operation
annual_cost = kwh_per_year * $0.12  # Electricity rate
```

**Your task:** Verify this makes sense and adjust if needed.

## 🔍 How to Test

1. **Edge Cases**
   - What happens with pressure_drop = 0?
   - What if flow_deviation is negative? (shouldn't happen, but...)
   
2. **Boundary Conditions**
   - Test right at thresholds (e.g., 5.0 PSI, 5.1 PSI)
   
3. **Business Logic**
   - Does a 1mm leak really cost $X per year?
   - Ask: Would a factory manager agree with your priorities?

## 📝 Deliverables

- [ ] Working severity classification function
- [ ] Cost estimation function
- [ ] Sample output JSON with severity distribution
- [ ] Brief documentation of any rule changes you made

## 🎯 Integration with Other Models

Your output will be used by:
- **Dashboard** - To color-code alerts (red = CRITICAL, yellow = MEDIUM, etc.)
- **Model 05 (Forecasting)** - To prioritize which zones to forecast

## Example Output Format

```json
{
  "leak_id": "LEAK_2026_02_14_001",
  "zone": "Zone_A",
  "severity": "HIGH",
  "priority_score": 75,
  "pressure_drop": 12.5,
  "flow_deviation": 125.3,
  "estimated_leak_size_mm": 3.2,
  "annual_cost_usd": 18500,
  "detected_at": "2026-02-14T10:30:00Z"
}
```

---

**Questions?** This is the simplest model—you should finish fast and help others!
