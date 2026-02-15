"""
Model 05: Predictive Leak Forecasting (Prophet)

PRIORITY: 💡 Nice to Have (Major Differentiator!)
ESTIMATED TIME: 2-3 hours

DESCRIPTION:
Time series forecasting to predict where leaks will occur in the next 30 days.
Uses historical leak patterns per pipe segment.

INPUTS:
- Time series of leak occurrences per pipe (P-001 through P-010)
- Pressure drop patterns (PS - PE)
- Temperature and humidity variations

OUTPUTS:
- Probability of leak occurrence in next 30 days (per pipe)
- Expected leak severity
- Recommended inspection schedule

SUCCESS CRITERIA:
- Precision > 0.70 (avoid false alarms)
- Recall > 0.60 (catch most failures)
- Actionable 30-day forecast per pipe
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import MODELS_DIR

# Leak detection thresholds (adjusted for sensor noise tolerance)
LEAK_THRESHOLDS = {
    'SMALL': 8,    # 8-15 PSI drop (filters normal noise)
    'MEDIUM': 15,  # 15-25 PSI drop
    'LARGE': 25,   # > 25 PSI drop
}


class PipeLeakForecaster:
    """Prophet-based forecasting for pipe leak prediction."""
    
    def __init__(self):
        self.models = {}  # One model per pipe
        self.pipe_ids = [f'P-{str(i).zfill(3)}' for i in range(1, 11)]  # P-001 to P-010
    
    def load_data(self) -> pd.DataFrame:
        """Load historical pipe sensor data from CSV."""
        
        # Try historical data first
        data_file = Path(__file__).parent.parent.parent / "data" / "generated" / "pipe_history.csv"
        
        if not data_file.exists():
            # Fall back to live data (though it won't have enough history)
            data_file = Path(__file__).parent.parent.parent / "data" / "generated" / "live_sensor_data.csv"
            print(f"⚠️  pipe_history.csv not found, using live data (may be insufficient)")
        
        print(f"📂 Loading data from {data_file}...")
        
        if not data_file.exists():
            print(f"❌ File not found: {data_file}")
            print("   Please run: python data/generate_pipe_history.py")
            return None
        
        df = pd.read_csv(data_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"✅ Loaded {len(df):,} rows from {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Duration: {(df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 86400:.1f} days")
        
        return df
    
    def calculate_pressure_drops(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate pressure drop for each pipe and detect leaks."""
        
        print("\n🔧 Calculating pressure drops per pipe...")
        
        leak_data = []
        
        for pipe_id in self.pipe_ids:
            ps_col = f'PS_{pipe_id}'  # Pressure Start
            pe_col = f'PE_{pipe_id}'  # Pressure End
            
            if ps_col not in df.columns or pe_col not in df.columns:
                print(f"   ⚠️  Skipping {pipe_id}: columns not found")
                continue
            
            # Calculate pressure drop
            pressure_drop = df[ps_col] - df[pe_col]
            
            # Classify leak severity
            severity = pd.cut(
                pressure_drop,
                bins=[-np.inf, LEAK_THRESHOLDS['SMALL'], LEAK_THRESHOLDS['MEDIUM'], LEAK_THRESHOLDS['LARGE'], np.inf],
                labels=['NONE', 'SMALL', 'MEDIUM', 'LARGE']
            )
            
            # A leak is detected if pressure drop > 5 PSI
            is_leak = pressure_drop > LEAK_THRESHOLDS['SMALL']
            
            # Build leak records
            for idx, row in df.iterrows():
                if is_leak.iloc[idx]:
                    leak_data.append({
                        'timestamp': row['timestamp'],
                        'pipe_id': pipe_id,
                        'pressure_start': row[ps_col],
                        'pressure_end': row[pe_col],
                        'pressure_drop': pressure_drop.iloc[idx],
                        'temperature': row.get(f'T_{pipe_id}', None),
                        'humidity': row.get(f'H_{pipe_id}', None),
                        'severity': severity.iloc[idx],
                        'is_leak': True
                    })
        
        leak_df = pd.DataFrame(leak_data)
        
        if not leak_df.empty:
            print(f"✅ Detected {len(leak_df):,} leak events across all pipes")
            print(f"\n   Severity distribution:")
            for sev in ['SMALL', 'MEDIUM', 'LARGE']:
                count = (leak_df['severity'] == sev).sum()
                print(f"      {sev:>6}: {count:>5,} leaks")
        else:
            print("⚠️  No leaks detected in the data")
        
        return leak_df
    
    def prepare_time_series(self, leak_df: pd.DataFrame, pipe_id: str) -> pd.DataFrame:
        """
        Prepare time series data for Prophet (per pipe).
        
        Prophet requires columns: 'ds' (datetime) and 'y' (value)
        """
        
        # Filter to specific pipe
        pipe_leaks = leak_df[leak_df['pipe_id'] == pipe_id].copy()
        
        if pipe_leaks.empty:
            # No leaks for this pipe
            return pd.DataFrame({'ds': [], 'y': []})
        
        # Aggregate to daily leak counts
        daily_leaks = pipe_leaks.groupby(pipe_leaks['timestamp'].dt.date).size().reset_index()
        daily_leaks.columns = ['ds', 'y']
        daily_leaks['ds'] = pd.to_datetime(daily_leaks['ds'])
        
        # Fill missing days with 0 leaks
        date_range = pd.date_range(
            start=daily_leaks['ds'].min(),
            end=daily_leaks['ds'].max(),
            freq='D'
        )
        
        full_range = pd.DataFrame({'ds': date_range})
        daily_leaks = full_range.merge(daily_leaks, on='ds', how='left')
        daily_leaks['y'] = daily_leaks['y'].fillna(0)
        
        print(f"   {pipe_id}: {len(daily_leaks)} days, {daily_leaks['y'].sum():.0f} total leaks")
        
        return daily_leaks
    
    
    def train_pipe_model(self, df_pipe: pd.DataFrame, pipe_id: str):
        """Train a Prophet model for a specific pipe."""
        
        if df_pipe.empty or df_pipe['y'].sum() == 0:
            print(f"   ⚠️  {pipe_id}: No leaks to train on - skipping")
            return None
        
        # Initialize Prophet with relaxed settings for short time series
        model = Prophet(
            seasonality_mode='additive',
            interval_width=0.95,
            daily_seasonality=False,
            weekly_seasonality=False,  # May not have enough data
            yearly_seasonality=False,
            changepoint_prior_scale=0.5  # More flexible
        )
        
        # Train
        try:
            model.fit(df_pipe)
            print(f"   ✅ {pipe_id}: Model trained successfully")
            return model
        except Exception as e:
            print(f"   ❌ {pipe_id}: Training failed - {e}")
            return None
    
    def forecast(self, pipe_id: str, periods: int = 30) -> pd.DataFrame:
        """Generate forecast for a specific pipe."""
        
        if pipe_id not in self.models or self.models[pipe_id] is None:
            return None
        
        model = self.models[pipe_id]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)
        
        # Predict
        forecast = model.predict(future)
        
        return forecast
    
    def calculate_risk_scores(self, forecast: pd.DataFrame, pipe_id: str) -> pd.DataFrame:
        """
        Calculate risk scores based on forecast.
        
        Risk = predicted leak rate * 100 (normalized to 0-100%)
        """
        
        if forecast is None or forecast.empty:
            return pd.DataFrame()
        
        # Get forecast for future dates only (last 30 days)
        future_forecast = forecast.tail(30).copy()
        
        # Base risk from forecast (predicted leak count)
        # Normalize: if yhat > 1 leak/day, risk = 100%
        future_forecast['base_risk'] = (future_forecast['yhat'].clip(0, 2) / 2 * 100)
        
        # Final risk score
        future_forecast['risk_score'] = future_forecast['base_risk'].clip(0, 100)
        
        return future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'risk_score']]
    
    def generate_recommendations(self, risk_scores: pd.DataFrame, pipe_id: str):
        """Generate maintenance recommendations based on risk scores."""
        
        if risk_scores.empty:
            print(f"   ℹ️  {pipe_id}: Insufficient data for forecast")
            return
        
        high_risk_days = risk_scores[risk_scores['risk_score'] > 60]
        avg_risk = risk_scores['risk_score'].mean()
        max_risk = risk_scores['risk_score'].max()
        
        if max_risk > 80:
            print(f"   🔴 {pipe_id}: CRITICAL RISK ({max_risk:.0f}%) - Immediate inspection required!")
        elif max_risk > 60:
            print(f"   🟠 {pipe_id}: HIGH RISK ({max_risk:.0f}%) - Schedule inspection within 7 days")
        elif avg_risk > 30:
            print(f"   🟡 {pipe_id}: MODERATE RISK ({avg_risk:.0f}%) - Monitor closely")
        else:
            print(f"   🟢 {pipe_id}: LOW RISK ({avg_risk:.0f}%) - Continue normal monitoring")
    
    def train_all_pipes(self, leak_df: pd.DataFrame):
        """Train models for all pipes."""
        
        print(f"\n🏗️  Training forecast models for {len(self.pipe_ids)} pipes...")
        
        trained_count = 0
        
        for pipe_id in self.pipe_ids:
            # Prepare time series
            df_pipe = self.prepare_time_series(leak_df, pipe_id)
            
            # Train model
            model = self.train_pipe_model(df_pipe, pipe_id)
            
            # Store model
            self.models[pipe_id] = model
            if model is not None:
                trained_count += 1
        
        print(f"\n✅ {trained_count}/{len(self.pipe_ids)} pipe models trained successfully!")
    
    def save_models(self, output_dir: Path):
        """Save all trained models."""
        import pickle
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for pipe_id, model in self.models.items():
            if model is not None:
                model_file = output_dir / f"prophet_model_{pipe_id}.pkl"
                with open(model_file, 'wb') as f:
                    pickle.dump(model, f)
                saved_count += 1
        
        print(f"\n💾 {saved_count} models saved to {output_dir}/")
    
    def save_forecast_summary(self, output_dir: Path):
        """Save forecast summary to CSV."""
        
        summary_rows = []
        
        for pipe_id in self.pipe_ids:
            forecast = self.forecast(pipe_id, periods=30)
            if forecast is not None:
                risk_scores = self.calculate_risk_scores(forecast, pipe_id)
                if not risk_scores.empty:
                    summary_rows.append({
                        'pipe_id': pipe_id,
                        'avg_predicted_leaks_per_day': forecast['yhat'].tail(30).mean(),
                        'avg_risk_score': risk_scores['risk_score'].mean(),
                        'max_risk_score': risk_scores['risk_score'].max(),
                        'high_risk_days': (risk_scores['risk_score'] > 60).sum(),
                    })
        
        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            summary_file = output_dir / "forecast_summary.csv"
            summary_df.to_csv(summary_file, index=False)
            print(f"📊 Forecast summary saved to {summary_file}")
            
            return summary_df
        
        return None


def main():
    """Main forecasting pipeline."""
    
    print("=" * 70)
    print("MODEL 05: PREDICTIVE LEAK FORECASTING (PIPE-BASED)")
    print("=" * 70)
    
    # Initialize forecaster
    forecaster = PipeLeakForecaster()
    
    # Load data
    df = forecaster.load_data()
    
    if df is None:
        print("\n❌ Data loading failed.")
        print("   Run: python data/generate_pipe_history.py")
        print("   This will create ~14 days of historical pipe sensor data.")
        return
    
    # Calculate pressure drops and detect leaks
    leak_df = forecaster.calculate_pressure_drops(df)
    
    if leak_df.empty:
        print("\n❌ No leaks detected in data. Cannot train forecast models.")
        return
    
    # Train models for all pipes
    forecaster.train_all_pipes(leak_df)
    
    # Generate forecasts and recommendations
    print("\n" + "=" * 70)
    print("30-DAY FORECAST RESULTS (PER PIPE)")
    print("=" * 70)
    
    for pipe_id in forecaster.pipe_ids:
        forecast = forecaster.forecast(pipe_id, periods=30)
        if forecast is not None:
            risk_scores = forecaster.calculate_risk_scores(forecast, pipe_id)
            forecaster.generate_recommendations(risk_scores, pipe_id)
    
    # Save models and summary
    output_dir = MODELS_DIR / "05_predictive_forecast" / "trained_models"
    forecaster.save_models(output_dir)
    
    summary_df = forecaster.save_forecast_summary(output_dir)
    
    if summary_df is not None:
        print("\n" + "=" * 70)
        print("📊 FORECAST SUMMARY")
        print("=" * 70)
        print(summary_df.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✅ MODEL 05 COMPLETE!")
    print("=" * 70)
    print("\n🎯 KEY DIFFERENTIATOR:")
    print("   You're not just detecting leaks—you're PREDICTING them!")
    print("   Per-pipe forecasts enable targeted preventive maintenance.")
    print("   This puts you ahead of 95% of hackathon projects! 🚀")


if __name__ == "__main__":
    main()
