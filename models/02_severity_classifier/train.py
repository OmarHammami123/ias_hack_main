"""
Model 02: Severity Classifier (Rule-Based)

PRIORITY: ✅ Must Have
ESTIMATED TIME: 30 minutes
TEAM MEMBER: _________

DESCRIPTION:
Rule-based classifier that categorizes detected leaks by severity level.
Uses pressure drop and flow deviation thresholds.

INPUTS:
- Pressure drop (PSI)
- Flow rate deviation (CFM)
- Optional: Leak duration, zone, time of day

OUTPUTS:
- Severity level: CRITICAL, HIGH, MEDIUM, LOW
- Priority score (0-100)

SUCCESS CRITERIA:
- Clear, interpretable rules
- Fast inference (< 1ms)
- Aligns with business impact
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
            'CRITICAL': 20,  # > 20 PSI drop
            'HIGH': 10,      # 10-20 PSI drop
            'MEDIUM': 5,     # 5-10 PSI drop
            'LOW': 0,        # < 5 PSI drop
        }
        
        self.flow_thresholds = {
            'CRITICAL': 200,  # > 200 CFM deviation
            'HIGH': 100,      # 100-200 CFM
            'MEDIUM': 50,     # 50-100 CFM
            'LOW': 0,         # < 50 CFM
        }
        
        # Priority scores
        self.priority_scores = {
            'CRITICAL': 100,
            'HIGH': 75,
            'MEDIUM': 50,
            'LOW': 25,
        }
        
    def calculate_baseline(self, df: pd.DataFrame) -> dict:
        """Calculate baseline values per zone."""
        print("📊 Calculating baseline values per zone...")
        
        # Filter to normal periods only (non-anomalous)
        normal_data = df[df['is_anomaly'] == False]
        
        baselines = {}
        for zone in df['zone'].unique():
            zone_data = normal_data[normal_data['zone'] == zone]
            
            baselines[zone] = {
                'pressure_baseline': zone_data['pressure_psi'].median(),
                'flow_baseline': zone_data['flow_rate_cfm'].median(),
            }
            
            print(f"   {zone}: Pressure={baselines[zone]['pressure_baseline']:.1f} PSI, "
                  f"Flow={baselines[zone]['flow_baseline']:.1f} CFM")
        
        return baselines
    
    def calculate_deviations(self, df: pd.DataFrame, baselines: dict) -> pd.DataFrame:
        """Calculate deviations from baseline."""
        
        df = df.copy()
        df['pressure_drop'] = 0.0
        df['flow_deviation'] = 0.0
        
        for zone in df['zone'].unique():
            zone_mask = df['zone'] == zone
            baseline = baselines[zone]
            
            # Pressure drop (baseline - current)
            df.loc[zone_mask, 'pressure_drop'] = (
                baseline['pressure_baseline'] - df.loc[zone_mask, 'pressure_psi']
            )
            
            # Flow deviation (current - baseline, absolute)
            df.loc[zone_mask, 'flow_deviation'] = abs(
                df.loc[zone_mask, 'flow_rate_cfm'] - baseline['flow_baseline']
            )
        
        return df
    
    def classify(self, pressure_drop: float, flow_deviation: float) -> tuple:
        """
        Classify severity based on pressure drop and flow deviation.
        
        Returns:
            (severity_level, priority_score)
        """
        
        # Determine severity based on BOTH pressure and flow
        # Use the worse of the two indicators
        
        if pressure_drop > self.pressure_thresholds['CRITICAL'] or \
           flow_deviation > self.flow_thresholds['CRITICAL']:
            severity = 'CRITICAL'
        elif pressure_drop > self.pressure_thresholds['HIGH'] or \
             flow_deviation > self.flow_thresholds['HIGH']:
            severity = 'HIGH'
        elif pressure_drop > self.pressure_thresholds['MEDIUM'] or \
             flow_deviation > self.flow_thresholds['MEDIUM']:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        # TODO: Add additional factors:
        # - Night shift multiplier (higher priority if leak during idle time)
        # - Zone criticality (production zones > storage zones)
        # - Leak duration (longer duration = higher priority)
        # - Trend (worsening vs stable)
        
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
                row['flow_deviation']
            )
            
            # Estimate leak size from pressure drop (rough approximation)
            leak_size_mm = row['pressure_drop'] / 5  # ~5 PSI per mm
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
        
        # Overall stats
        total_anomalies = df['is_anomaly'].sum()
        print(f"\nTotal anomalies detected: {total_anomalies:,}")
        
        # Breakdown by severity
        print("\nSeverity Distribution:")
        severity_counts = df[df['is_anomaly']]['severity'].value_counts()
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            pct = (count / total_anomalies * 100) if total_anomalies > 0 else 0
            print(f"  {severity:>8}: {count:>6} ({pct:>5.1f}%)")
        
        # Financial impact
        total_cost = df[df['is_anomaly']]['estimated_annual_cost'].sum()
        print(f"\nEstimated Total Annual Cost: ${total_cost:,.2f}")
        
        # Top 5 most costly leaks
        print("\n🔴 Top 5 Most Costly Leaks:")
        top_leaks = df[df['is_anomaly']].nlargest(5, 'estimated_annual_cost')
        for idx, row in top_leaks.iterrows():
            print(f"  {row['sensor_id']} ({row['zone']}): "
                  f"{row['severity']} - ${row['estimated_annual_cost']:,.0f}/year")
        
        # Zone breakdown
        print("\nBy Zone:")
        for zone in df['zone'].unique():
            zone_anomalies = df[(df['zone'] == zone) & (df['is_anomaly'])]
            zone_cost = zone_anomalies['estimated_annual_cost'].sum()
            print(f"  {zone}: {len(zone_anomalies)} leaks, ${zone_cost:,.0f}/year")


def main():
    """Main classification pipeline."""
    
    print("=" * 60)
    print("MODEL 02: SEVERITY CLASSIFIER")
    print("=" * 60)
    
    # Initialize classifier
    classifier = SeverityClassifier()
    
    # Load data
    data_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
    print(f"\n📂 Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate baselines
    baselines = classifier.calculate_baseline(df)
    
    # Calculate deviations
    df = classifier.calculate_deviations(df, baselines)
    
    # Classify severity
    print("\n🎯 Classifying leak severity...")
    df = classifier.classify_batch(df)
    
    # Generate report
    classifier.generate_report(df)
    
    # Save classified data
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
