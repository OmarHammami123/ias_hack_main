"""
Model 01: Isolation Forest for Anomaly Detection

PRIORITY: ✅ Must Have
ESTIMATED TIME: 1-2 hours
TEAM MEMBER: _________

DESCRIPTION:
Uses Isolation Forest algorithm to detect anomalous sensor readings that may indicate leaks.
Works by identifying data points that are "isolated" from the normal distribution.

INPUTS:
- Pressure sensor readings (pressure_psi, flow_rate_cfm, temperature_c)

OUTPUTS:
- Binary classification: anomaly (1) or normal (0)
- Anomaly score (higher = more anomalous)

SUCCESS CRITERIA:
- Accuracy > 90%
- Low false positive rate (< 10%)
- Fast inference time (< 100ms per batch)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import MODEL_CONFIG, RAW_DATA_DIR, MODELS_DIR
from utils.helpers import get_zone_statistics


class LeakAnomalyDetector:
    """Isolation Forest model for detecting leak anomalies."""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=MODEL_CONFIG["isolation_forest"]["contamination"],
            n_estimators=MODEL_CONFIG["isolation_forest"]["n_estimators"],
            random_state=MODEL_CONFIG["isolation_forest"]["random_state"],
        )
        self.scaler = StandardScaler()
        self.feature_columns = ['pressure_psi', 'flow_rate_cfm', 'temperature_c']
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load pressure sensor data."""
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"   Loaded {len(df):,} rows")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for training."""
        
        # TODO: Add feature engineering here
        # Ideas:
        # - Rolling statistics (mean, std over last N samples)
        # - Rate of change (derivative of pressure/flow)
        # - Time-based features (hour of day, day of week)
        # - Zone-specific baseline deviations
        
        X = df[self.feature_columns].copy()
        y = df['is_anomaly'].values if 'is_anomaly' in df.columns else None
        
        print(f"📊 Feature shape: {X.shape}")
        if y is not None:
            print(f"   Anomaly rate: {y.mean()*100:.2f}%")
        
        return X, y
    
    def train(self, X: pd.DataFrame):
        """Train the Isolation Forest model."""
        print("\n🎯 Training Isolation Forest...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        
        print("✅ Training complete!")
        
    def predict(self, X: pd.DataFrame) -> tuple:
        """Predict anomalies."""
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(X_scaled)
        
        # Convert to binary (1 for anomaly, 0 for normal)
        predictions_binary = (predictions == -1).astype(int)
        
        # Get anomaly scores (lower = more anomalous)
        scores = self.model.score_samples(X_scaled)
        # Invert so higher = more anomalous
        anomaly_scores = -scores
        
        return predictions_binary, anomaly_scores
    
    def evaluate(self, X: pd.DataFrame, y: np.ndarray):
        """Evaluate model performance."""
        print("\n📈 Evaluating model...")
        
        predictions, scores = self.predict(X)
        
        # Classification metrics
        print("\nClassification Report:")
        print(classification_report(y, predictions, target_names=['Normal', 'Anomaly']))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y, predictions))
        
        # ROC AUC
        auc = roc_auc_score(y, scores)
        print(f"\nROC AUC Score: {auc:.4f}")
        
        return {
            'predictions': predictions,
            'scores': scores,
            'auc': auc,
        }
    
    def save_model(self, output_dir: str):
        """Save trained model and scaler."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        model_file = output_path / "isolation_forest.pkl"
        scaler_file = output_path / "scaler.pkl"
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        
        print(f"\n💾 Model saved to {output_dir}/")
        
    def load_model(self, model_dir: str):
        """Load pre-trained model and scaler."""
        model_path = Path(model_dir)
        
        self.model = joblib.load(model_path / "isolation_forest.pkl")
        self.scaler = joblib.load(model_path / "scaler.pkl")
        
        print(f"✅ Model loaded from {model_dir}/")


def main():
    """Main training pipeline."""
    
    print("=" * 60)
    print("MODEL 01: ISOLATION FOREST ANOMALY DETECTION")
    print("=" * 60)
    
    # Initialize detector
    detector = LeakAnomalyDetector()
    
    # Load data
    data_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
    df = detector.load_data(data_file)
    
    # Prepare features
    X, y = detector.prepare_features(df)
    
    # Train model
    detector.train(X)
    
    # Evaluate
    results = detector.evaluate(X, y)
    
    # Save model
    model_output_dir = MODELS_DIR / "01_isolation_forest" / "trained_model"
    detector.save_model(model_output_dir)
    
    print("\n" + "=" * 60)
    print("✅ MODEL 01 COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review evaluation metrics above")
    print("2. Tune hyperparameters if needed (contamination, n_estimators)")
    print("3. Add feature engineering for better performance")
    print("4. Test on new data: detector.predict(new_data)")


if __name__ == "__main__":
    main()
