"""
Model 02: Severity Classifier (Rule-Based)

PRIORITY: ✅ Must Have
ESTIMATED TIME: 30 minutes

DESCRIPTION:
Rule-based classifier that categorizes detected leaks by severity level.
Uses pressure drop and humidity change thresholds.

INPUTS:
- Pressure drop (PSI)
- Humidity change (%)

OUTPUTS:
- Severity level: LARGE, MEDIUM, SMALL
- Priority score (0-100)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import RAW_DATA_DIR, MODELS_DIR
from utils.helpers import classify_severity, calculate_leak_cost


class SeverityClassifier:
    """Rule-based severity classifier for detected leaks."""
    
    def __init__(self):
        # Severity thresholds
        self.pressure_thresholds = {
            'LARGE': 15,    # > 15 PSI drop
            'MEDIUM': 5,    # 5-15 PSI drop
            'SMALL': 0,     # < 5 PSI drop
        }
        
        self.humidity_thresholds = {
            'LARGE': 10,    # > 10% humidity change
            'MEDIUM': 5,    # 5-10% change
            'SMALL': 0,     # < 5% change
        }
        
        self.priority_scores = {
            'LARGE': 100,
            'MEDIUM': 60,
            'SMALL': 30,
        }
        
    def calculate_baseline(self, df: pd.DataFrame) -> dict:
        """Calculate baseline values per zone."""
        print("📊 Calculating baseline values per zone...")
        
        normal_data = df[df['is_anomaly'] == False]
        
        baselines = {}
        for zone in df['zone'].unique():
            zone_data = normal_data[normal_data['zone'] == zone]
            
            baselines[zone] = {
                'pressure_baseline': zone_data['pressure_psi'].median(),
                'humidity_baseline': zone_data['humidity_percent'].median(),
            }
            
            print(f"   {zone}: Pressure={baselines[zone]['pressure_baseline']:.1f} PSI, "
                  f"Humidity={baselines[zone]['humidity_baseline']:.1f}%")
        
        return baselines
    
    def calculate_deviations(self, df: pd.DataFrame, baselines: dict) -> pd.DataFrame:
        """Calculate deviations from baseline."""
        
        df = df.copy()
        df['pressure_drop'] = 0.0
        df['humidity_change'] = 0.0
        
        for zone in df['zone'].unique():
            zone_mask = df['zone'] == zone
            baseline = baselines[zone]
            
            df.loc[zone_mask, 'pressure_drop'] = (
                baseline['pressure_baseline'] - df.loc[zone_mask, 'pressure_psi']
            ).clip(lower=0)
            
            df.loc[zone_mask, 'humidity_change'] = abs(
                df.loc[zone_mask, 'humidity_percent'] - baseline['humidity_baseline']
            )
        
        return df
    
    def classify(self, pressure_drop: float, humidity_change: float) -> tuple:
        """Classify severity based on pressure drop and humidity change."""
        
        if pressure_drop > self.pressure_thresholds['LARGE'] or \
           humidity_change > self.humidity_thresholds['LARGE']:
            severity = 'LARGE'
        elif pressure_drop > self.pressure_thresholds['MEDIUM'] or \
             humidity_change > self.humidity_thresholds['MEDIUM']:
            severity = 'MEDIUM'
        else:
            severity = 'SMALL'
        
        priority_score = self.priority_scores[severity]
        
        return severity, priority_score
    
    def classify_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify severity for a batch of readings."""
        
        df = df.copy()
        
        severity_levels = []
        priority_scores = []
        estimated_costs = []
        
        for _, row in df.iterrows():
            severity, priority = self.classify(
                row['pressure_drop'],
                row['humidity_change']
            )
            
            leak_size_mm = row['pressure_drop'] / 5
            annual_cost = calculate_leak_cost(leak_size_mm)
            
            severity_levels.append(severity)
            priority_scores.append(priority)
            estimated_costs.append(annual_cost)
        
        df['severity'] = severity_levels
        df['priority_score'] = priority_scores
        df['estimated_annual_cost'] = estimated_costs
        
        return df
    
    def generate_report(self, df: pd.DataFrame):
        """Generate summary report of classified leaks."""
        
        print("\n" + "=" * 60)
        print("SEVERITY CLASSIFICATION REPORT")
        print("=" * 60)
        
        total_anomalies = df['is_anomaly'].sum()
        print(f"\nTotal anomalies detected: {total_anomalies:,}")
        
        print("\nSeverity Distribution:")
        anomaly_df = df[df['is_anomaly']]
        severity_counts = anomaly_df['severity'].value_counts()
        for severity in ['LARGE', 'MEDIUM', 'SMALL']:
            count = severity_counts.get(severity, 0)
            pct = (count / total_anomalies * 100) if total_anomalies > 0 else 0
            avg_cost = anomaly_df[anomaly_df['severity'] == severity]['estimated_annual_cost'].mean()
            cost_str = f"{avg_cost:,.0f} TND" if not np.isnan(avg_cost) else "0 TND"
            print(f"  {severity:>6}: {count:>6,} ({pct:>5.1f}%) - Avg cost: {cost_str:>15}/year")
        
        total_cost = anomaly_df['estimated_annual_cost'].sum()
        print(f"\nEstimated Total Annual Cost: {total_cost:,.2f} TND")
        
        print("\n🔴 Top 5 Most Costly Leaks:")
        top_leaks = anomaly_df.nlargest(5, 'estimated_annual_cost')
        for idx, row in top_leaks.iterrows():
            print(f"  {row['sensor_id']} ({row['zone']}): "
                  f"{row['severity']:>6} - Pressure drop: {row['pressure_drop']:.1f} PSI - "
                  f"{row['estimated_annual_cost']:,.0f} TND/year")
        
        print("\nBy Zone:")
        for zone in sorted(df['zone'].unique()):
            zone_anomalies = anomaly_df[anomaly_df['zone'] == zone]
            zone_cost = zone_anomalies['estimated_annual_cost'].sum()
            zone_count = len(zone_anomalies)
            if zone_count > 0:
                print(f"  {zone}: {zone_count:>3} leaks, {zone_cost:>10,.0f} TND/year")


def main():
    """Main classification pipeline."""
    
    print("=" * 60)
    print("MODEL 02: SEVERITY CLASSIFIER")
    print("=" * 60)
    
    classifier = SeverityClassifier()
    
    data_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
    print(f"\n📂 Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"   Loaded {len(df):,} rows")
    
    baselines = classifier.calculate_baseline(df)
    df = classifier.calculate_deviations(df, baselines)
    
    print("\n🎯 Classifying leak severity...")
    df = classifier.classify_batch(df)
    
    classifier.generate_report(df)
    
    output_dir = MODELS_DIR / "02_severity_classifier"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "classified_leaks.csv"
    
    df[df['is_anomaly']].to_csv(output_file, index=False)
    print(f"\n💾 Classified leaks saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("✅ MODEL 02 COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
