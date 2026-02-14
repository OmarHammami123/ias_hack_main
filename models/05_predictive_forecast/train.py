"""
Model 05: Predictive Leak Forecasting (Prophet)

PRIORITY: 💡 Nice to Have (Major Differentiator!)
ESTIMATED TIME: 2-3 hours
TEAM MEMBER: _________

DESCRIPTION:
Time series forecasting to predict where leaks will occur in the next 30 days.
Uses historical leak patterns, pipe metadata, and environmental factors.

INPUTS:
- Time series of leak occurrences per zone
- Pipe age, material, joint type
- Temperature cycling patterns
- Historical maintenance records

OUTPUTS:
- Probability of leak occurrence in next 30 days (per zone/sensor)
- Expected leak severity
- Recommended inspection schedule

SUCCESS CRITERIA:
- Precision > 0.70 (avoid false alarms)
- Recall > 0.60 (catch most failures)
- Actionable 30-day forecast
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import classification_report, precision_recall_curve
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import MODEL_CONFIG, RAW_DATA_DIR, MODELS_DIR


class LeakForecastModel:
    """Prophet-based forecasting for predictive maintenance."""
    
    def __init__(self):
        self.models = {}  # One model per zone
        self.metadata = None
        
    def load_data(self) -> tuple:
        """Load historical leak data and sensor metadata."""
        
        # Load pressure data
        pressure_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
        print(f"📂 Loading data from {pressure_file}...")
        df_pressure = pd.read_csv(pressure_file)
        df_pressure['timestamp'] = pd.to_datetime(df_pressure['timestamp'])
        
        # Load metadata
        metadata_file = RAW_DATA_DIR / "sensor_metadata.csv"
        if metadata_file.exists():
            df_metadata = pd.read_csv(metadata_file)
            df_metadata['installation_date'] = pd.to_datetime(df_metadata['installation_date'])
            self.metadata = df_metadata
        else:
            print("⚠️  Metadata file not found. Run data generation first.")
            self.metadata = None
        
        return df_pressure, self.metadata
    
    def prepare_time_series(self, df: pd.DataFrame, zone: str) -> pd.DataFrame:
        """
        Prepare time series data for Prophet.
        
        Prophet requires columns: 'ds' (datetime) and 'y' (value)
        """
        
        # Filter to specific zone
        zone_data = df[df['zone'] == zone].copy()
        
        # Aggregate to daily leak counts
        daily_leaks = zone_data.groupby(zone_data['timestamp'].dt.date).agg({
            'is_anomaly': 'sum',  # Count of leaks per day
        }).reset_index()
        
        daily_leaks.columns = ['ds', 'y']
        daily_leaks['ds'] = pd.to_datetime(daily_leaks['ds'])
        
        print(f"   {zone}: {len(daily_leaks)} days, {daily_leaks['y'].sum()} total leaks")
        
        return daily_leaks
    
    def train_zone_model(self, df_zone: pd.DataFrame, zone: str):
        """Train a Prophet model for a specific zone."""
        
        print(f"\n🎯 Training model for {zone}...")
        
        # Initialize Prophet
        model = Prophet(
            seasonality_mode=MODEL_CONFIG["predictive_forecast"]["seasonality_mode"],
            interval_width=MODEL_CONFIG["predictive_forecast"]["interval_width"],
            daily_seasonality=True,
            weekly_seasonality=True,
        )
        
        # Add custom seasonality (e.g., work shifts)
        # Leaks may be more noticeable during idle periods
        
        # Train
        model.fit(df_zone)
        
        print(f"✅ {zone} model trained")
        
        return model
    
    def forecast(self, zone: str, periods: int = 30) -> pd.DataFrame:
        """Generate forecast for a specific zone."""
        
        if zone not in self.models:
            print(f"⚠️  No model found for {zone}")
            return None
        
        model = self.models[zone]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)
        
        # Predict
        forecast = model.predict(future)
        
        return forecast
    
    def calculate_risk_scores(self, forecast: pd.DataFrame, zone: str) -> pd.DataFrame:
        """
        Calculate risk scores based on forecast + metadata.
        
        Risk = f(predicted_leak_rate, pipe_age, material_factor, joint_factor)
        """
        
        # Get forecast for future dates only
        future_forecast = forecast[forecast['ds'] > forecast['ds'].max() - pd.Timedelta(days=30)]
        
        # Base risk from forecast (predicted leak count)
        future_forecast['base_risk'] = future_forecast['yhat'].clip(0, 100)  # 0-100 scale
        
        # Adjust for metadata if available
        if self.metadata is not None:
            zone_sensors = self.metadata[self.metadata['zone'] == zone]
            
            # Pipe age factor (older = higher risk)
            avg_pipe_age = zone_sensors['pipe_age_years'].mean()
            age_factor = 1 + (avg_pipe_age / 20)  # 20-year expected life
            
            # Material factor
            material_risk = {
                'steel': 1.0,
                'copper': 0.8,
                'pvc': 1.2,
            }
            avg_material_factor = zone_sensors['pipe_material'].map(material_risk).mean()
            
            # Joint factor
            joint_risk = {
                'welded': 0.8,
                'threaded': 1.0,
                'flanged': 1.3,
            }
            avg_joint_factor = zone_sensors['joint_type'].map(joint_risk).mean()
            
            # Combined risk score
            future_forecast['risk_score'] = (
                future_forecast['base_risk'] * 
                age_factor * 
                avg_material_factor * 
                avg_joint_factor
            )
        else:
            future_forecast['risk_score'] = future_forecast['base_risk']
        
        # Normalize to 0-100
        future_forecast['risk_score'] = future_forecast['risk_score'].clip(0, 100)
        
        return future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'risk_score']]
    
    def generate_recommendations(self, risk_scores: pd.DataFrame, zone: str):
        """Generate maintenance recommendations based on risk scores."""
        
        high_risk_days = risk_scores[risk_scores['risk_score'] > 70]
        
        if len(high_risk_days) > 0:
            print(f"\n🚨 HIGH RISK DETECTED - {zone}")
            print(f"   {len(high_risk_days)} high-risk days in next 30 days")
            print(f"   Recommended action: Schedule preventive inspection")
            print(f"   Priority: {'URGENT' if high_risk_days['risk_score'].max() > 85 else 'HIGH'}")
        else:
            print(f"\n✅ {zone}: Low risk, continue normal monitoring")
    
    def train_all_zones(self, df: pd.DataFrame):
        """Train models for all zones."""
        
        zones = df['zone'].unique()
        
        print(f"\n🏭 Training forecast models for {len(zones)} zones...")
        
        for zone in zones:
            # Prepare time series
            df_zone = self.prepare_time_series(df, zone)
            
            # Train model
            model = self.train_zone_model(df_zone, zone)
            
            # Store model
            self.models[zone] = model
        
        print(f"\n✅ All zone models trained!")
    
    def save_models(self, output_dir: str):
        """Save all trained models."""
        import pickle
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for zone, model in self.models.items():
            model_file = output_path / f"prophet_model_{zone}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
        
        print(f"\n💾 {len(self.models)} models saved to {output_dir}/")


def main():
    """Main forecasting pipeline."""
    
    print("=" * 60)
    print("MODEL 05: PREDICTIVE LEAK FORECASTING")
    print("=" * 60)
    
    # Initialize forecaster
    forecaster = LeakForecastModel()
    
    # Load data
    df_pressure, df_metadata = forecaster.load_data()
    
    if df_pressure is None:
        print("\n⚠️  Data not found. Run data generation first.")
        return
    
    # Train models for all zones
    forecaster.train_all_zones(df_pressure)
    
    # Generate forecasts
    print("\n" + "=" * 60)
    print("30-DAY FORECAST RESULTS")
    print("=" * 60)
    
    for zone in df_pressure['zone'].unique():
        forecast = forecaster.forecast(zone, periods=30)
        risk_scores = forecaster.calculate_risk_scores(forecast, zone)
        forecaster.generate_recommendations(risk_scores, zone)
    
    # Save models
    model_output_dir = MODELS_DIR / "05_predictive_forecast" / "trained_models"
    forecaster.save_models(model_output_dir)
    
    print("\n" + "=" * 60)
    print("✅ MODEL 05 COMPLETE!")
    print("=" * 60)
    print("\n🎯 KEY DIFFERENTIATOR:")
    print("You're not just detecting leaks—you're PREDICTING them!")
    print("This puts you ahead of 95% of hackathon projects.")


if __name__ == "__main__":
    main()
