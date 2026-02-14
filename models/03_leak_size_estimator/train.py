"""
Model 03: Leak Size Estimator (Linear Regression)

PRIORITY: ⚠️ Should Have
ESTIMATED TIME: 1 hour
TEAM MEMBER: _________

DESCRIPTION:
Linear regression model to estimate physical leak size (diameter in mm)
from pressure drop and flow rate measurements.

INPUTS:
- Pressure drop (PSI)
- Humidity change (%)
- Temperature (°C)

OUTPUTS:
- Estimated leak diameter (mm)
- Confidence interval
- Annual cost estimate

SUCCESS CRITERIA:
- R² > 0.80
- RMSE < 1mm for small leaks
- Realistic cost estimates
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import MODEL_CONFIG, RAW_DATA_DIR, MODELS_DIR
from utils.helpers import calculate_leak_cost


class LeakSizeEstimator:
    """Regression model to estimate leak size from sensor readings."""
    
    def __init__(self, model_type='linear'):
        if model_type == 'linear':
            self.model = LinearRegression()
        else:
            self.model = Ridge(alpha=1.0)
        
        self.scaler = StandardScaler()
        self.feature_columns = ['pressure_drop', 'humidity_change', 'temperature_c']
        
    def create_training_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create synthetic training data with known leak sizes.
        
        In real-world scenario, this would come from historical repairs.
        For hackathon, we generate it based on physics-based relationships.
        """
        
        # Filter to anomalies only
        leaks = df[df['is_anomaly']].copy()
        
        # Estimate leak size based on pressure drop and humidity change
        # Physics: larger leak → more pressure drop + higher humidity change
        # Rough approximation based on orifice flow equations:
        # Q = Cd * A * sqrt(2 * ΔP / ρ)
        # Combined with humidity as indicator of leak severity
        
        # Pressure contribution (primary indicator)
        pressure_component = leaks['pressure_drop'] / 5.0
        
        # Humidity contribution (secondary indicator, scaled down)
        humidity_component = leaks['humidity_change'] / 3.0
        
        # Combined estimate with noise
        leaks['leak_size_mm'] = (pressure_component + humidity_component) / 2 + np.random.normal(0, 0.3, len(leaks))
        leaks['leak_size_mm'] = leaks['leak_size_mm'].clip(0.5, 10)  # Physical limits
        
        return leaks
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load and prepare data."""
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"   Loaded {len(df):,} rows")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and target."""
        
        X = df[self.feature_columns].copy()
        y = df['leak_size_mm'].values if 'leak_size_mm' in df.columns else None
        
        print(f"📊 Feature shape: {X.shape}")
        if y is not None:
            print(f"   Target range: {y.min():.2f} - {y.max():.2f} mm")
            print(f"   Mean leak size: {y.mean():.2f} mm")
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: np.ndarray):
        """Train the regression model."""
        print("\n🎯 Training Leak Size Estimator...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=MODEL_CONFIG["leak_size_estimator"]["train_test_split"],
            random_state=MODEL_CONFIG["leak_size_estimator"]["random_state"]
        )
        
        print(f"   Training set: {len(X_train):,} samples")
        print(f"   Test set: {len(X_test):,} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"\n   R² Score (train): {train_score:.4f}")
        print(f"   R² Score (test):  {test_score:.4f}")
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        
        # Detailed metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"   RMSE: {rmse:.4f} mm")
        print(f"   MAE:  {mae:.4f} mm")
        
        # Feature importance (for linear models)
        if hasattr(self.model, 'coef_'):
            print("\n   Feature Importance:")
            for feature, coef in zip(self.feature_columns, self.model.coef_):
                print(f"     {feature:>20}: {coef:>8.4f}")
        
        print("✅ Training complete!")
        
        return {
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': y_pred,
            'r2': test_score,
            'rmse': rmse,
            'mae': mae,
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict leak sizes."""
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        # Ensure physical constraints
        predictions = np.clip(predictions, 0.1, 20)  # 0.1mm to 20mm
        return predictions
    
    def predict_with_cost(self, X: pd.DataFrame) -> pd.DataFrame:
        """Predict leak sizes and estimate costs."""
        
        leak_sizes = self.predict(X)
        annual_costs = [calculate_leak_cost(size) for size in leak_sizes]
        
        results = pd.DataFrame({
            'leak_size_mm': leak_sizes,
            'annual_cost_tnd': annual_costs,
        })
        
        return results
    
    def save_model(self, output_dir: str):
        """Save trained model."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, output_path / "leak_size_model.pkl")
        joblib.dump(self.scaler, output_path / "scaler.pkl")
        
        print(f"\n💾 Model saved to {output_dir}/")
    
    def load_model(self, model_dir: str):
        """Load pre-trained model."""
        model_path = Path(model_dir)
        
        self.model = joblib.load(model_path / "leak_size_model.pkl")
        self.scaler = joblib.load(model_path / "scaler.pkl")
        
        print(f"✅ Model loaded from {model_dir}/")


def main():
    """Main training pipeline."""
    
    print("=" * 60)
    print("MODEL 03: LEAK SIZE ESTIMATOR")
    print("=" * 60)
    
    # Initialize estimator
    estimator = LeakSizeEstimator(model_type='linear')
    
    # Load data (from previous models)
    classified_file = MODELS_DIR / "02_severity_classifier" / "classified_leaks.csv"
    
    if not classified_file.exists():
        print(f"\n⚠️  {classified_file} not found!")
        print("Run Model 02 first: python models/02_severity_classifier/train.py")
        return
    
    df = estimator.load_data(classified_file)
    
    # Create training data with synthetic leak sizes
    print("\n🔧 Creating training data...")
    training_data = estimator.create_training_data(df)
    
    # Prepare features
    X, y = estimator.prepare_features(training_data)
    
    # Train model
    results = estimator.train(X, y)
    
    # Save model
    model_output_dir = MODELS_DIR / "03_leak_size_estimator" / "trained_model"
    estimator.save_model(model_output_dir)
    
    # Example predictions
    print("\n" + "=" * 60)
    print("EXAMPLE PREDICTIONS")
    print("=" * 60)
    
    sample_data = pd.DataFrame({
        'pressure_drop': [3, 8, 15, 25],
        'humidity_change': [2, 6, 12, 18],
        'temperature_c': [22, 23, 22, 24],
    })
    
    predictions = estimator.predict_with_cost(sample_data)
    
    for i, row in predictions.iterrows():
        print(f"\nLeak {i+1}:")
        print(f"  Estimated size: {row['leak_size_mm']:.2f} mm")
        print(f"  Annual cost: {row['annual_cost_tnd']:,.2f} TND")
    
    print("\n" + "=" * 60)
    print("✅ MODEL 03 COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
