"""
Model 01: Isolation Forest for Anomaly Detection

PRIORITY: ✅ Must Have
ESTIMATED TIME: 1-2 hours
TEAM MEMBER: _________

DESCRIPTION:
Uses Isolation Forest algorithm to detect anomalous sensor readings that may indicate leaks.
Works by identifying data points that are "isolated" from the normal distribution.

INPUTS:
- Pressure sensor readings (pressure_psi, humidity_percent, temperature_c)

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
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
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
        # Note: feature_columns will be expanded by prepare_features()
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load pressure sensor data."""
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"   Loaded {len(df):,} rows")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for training with engineering."""
        
        print("🔧 Engineering features...")
        
        # Sort by sensor_id and timestamp for rolling calculations
        df = df.sort_values(['sensor_id', 'timestamp']).copy()
        
        # Basic features
        features_df = df[['pressure_psi', 'humidity_percent', 'temperature_c']].copy()
        
        # Feature Engineering - Rolling Statistics (per sensor)
        for col in ['pressure_psi', 'humidity_percent', 'temperature_c']:
            # Rolling mean (last 60 seconds)
            features_df[f'{col}_rolling_mean_60s'] = df.groupby('sensor_id')[col].transform(
                lambda x: x.rolling(window=60, min_periods=1).mean()
            )
            # Rolling std (last 60 seconds)
            features_df[f'{col}_rolling_std_60s'] = df.groupby('sensor_id')[col].transform(
                lambda x: x.rolling(window=60, min_periods=1).std().fillna(0)
            )
        
        # Rate of Change (derivatives)
        for col in ['pressure_psi', 'humidity_percent', 'temperature_c']:
            features_df[f'{col}_diff'] = df.groupby('sensor_id')[col].transform(
                lambda x: x.diff().fillna(0)
            )
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        features_df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        features_df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        features_df['is_work_hours'] = ((df['hour'] >= 7) & (df['hour'] <= 19)).astype(int)
        
        # Deviation from rolling mean
        features_df['pressure_deviation'] = (
            features_df['pressure_psi'] - features_df['pressure_psi_rolling_mean_60s']
        )
        features_df['humidity_deviation'] = (
            features_df['humidity_percent'] - features_df['humidity_percent_rolling_mean_60s']
        )
        
        X = features_df
        y = df['is_anomaly'].values if 'is_anomaly' in df.columns else None
        
        print(f"📊 Feature shape: {X.shape} ({X.shape[1]} features)")
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
    
    def evaluate(self, X: pd.DataFrame, y: np.ndarray, dataset_name: str = "Test"):
        """Evaluate model performance."""
        print(f"\n📈 Evaluating model on {dataset_name} set...")
        
        predictions, scores = self.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, predictions)
        precision = precision_score(y, predictions)
        recall = recall_score(y, predictions)
        f1 = f1_score(y, predictions)
        auc = roc_auc_score(y, scores)
        
        # Print summary metrics
        print(f"\n{'='*50}")
        print(f"{dataset_name.upper()} SET METRICS:")
        print(f"{'='*50}")
        print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"Precision: {precision:.4f} (of predicted leaks, {precision*100:.2f}% are real)")
        print(f"Recall:    {recall:.4f} (found {recall*100:.2f}% of actual leaks)")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC AUC:   {auc:.4f}")
        
        # Classification metrics
        print("\nDetailed Classification Report:")
        print(classification_report(y, predictions, target_names=['Normal', 'Anomaly']))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y, predictions)
        print(cm)
        print(f"\nTrue Negatives:  {cm[0][0]:,} (correctly identified normal)")
        print(f"False Positives: {cm[0][1]:,} (false alarms)")
        print(f"False Negatives: {cm[1][0]:,} (missed leaks)")
        print(f"True Positives:  {cm[1][1]:,} (correctly detected leaks)")
        
        # Calculate false positive rate
        fpr = cm[0][1] / (cm[0][0] + cm[0][1]) if (cm[0][0] + cm[0][1]) > 0 else 0
        print(f"\n⚠️  False Positive Rate: {fpr:.4f} ({fpr*100:.2f}%)")
        
        return {
            'predictions': predictions,
            'scores': scores,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc,
            'confusion_matrix': cm,
            'false_positive_rate': fpr,
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
    """Main training pipeline with train-test split."""
    
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
    
    # Train-Test Split (80-20)
    print("\n📊 Splitting data: 80% train, 20% test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training set: {len(X_train):,} samples")
    print(f"   Test set:     {len(X_test):,} samples")
    
    # Train model on training set only
    detector.train(X_train)
    
    # Evaluate on training set
    train_results = detector.evaluate(X_train, y_train, dataset_name="Training")
    
    # Evaluate on test set
    test_results = detector.evaluate(X_test, y_test, dataset_name="Test")
    
    # Compare train vs test performance
    print("\n" + "=" * 60)
    print("TRAIN vs TEST COMPARISON:")
    print("=" * 60)
    print(f"{'Metric':<20} {'Train':<15} {'Test':<15} {'Status'}")
    print("-" * 60)
    
    metrics_to_compare = [
        ('Accuracy', train_results['accuracy'], test_results['accuracy']),
        ('Precision', train_results['precision'], test_results['precision']),
        ('Recall', train_results['recall'], test_results['recall']),
        ('F1-Score', train_results['f1'], test_results['f1']),
        ('ROC AUC', train_results['auc'], test_results['auc']),
        ('FP Rate', train_results['false_positive_rate'], test_results['false_positive_rate']),
    ]
    
    for metric_name, train_val, test_val in metrics_to_compare:
        diff = abs(train_val - test_val)
        status = "✅ Good" if diff < 0.05 else "⚠️  Check"
        print(f"{metric_name:<20} {train_val:<15.4f} {test_val:<15.4f} {status}")
    
    # Save model
    model_output_dir = MODELS_DIR / "01_isolation_forest" / "trained_model"
    detector.save_model(model_output_dir)
    
    print("\n" + "=" * 60)
    print("✅ MODEL 01 COMPLETE!")
    print("=" * 60)
    
    # Success criteria check
    print("\n🎯 SUCCESS CRITERIA CHECK:")
    success = True
    
    if test_results['accuracy'] > 0.90:
        print("✅ Accuracy > 90%: PASS")
    else:
        print(f"❌ Accuracy > 90%: FAIL (got {test_results['accuracy']*100:.2f}%)")
        success = False
    
    if test_results['false_positive_rate'] < 0.10:
        print("✅ False Positive Rate < 10%: PASS")
    else:
        print(f"❌ False Positive Rate < 10%: FAIL (got {test_results['false_positive_rate']*100:.2f}%)")
        success = False
    
    if success:
        print("\n🎉 All success criteria met!")
    else:
        print("\n⚠️  Some criteria not met. Consider:")
        print("   - Tuning contamination parameter")
        print("   - Adding feature engineering (rolling means, derivatives)")
        print("   - Increasing n_estimators")
    
    print("\n📝 Next steps:")
    print("1. Review metrics above")
    print("2. If needed, tune hyperparameters in utils/config.py")
    print("3. Add feature engineering in prepare_features()")
    print("4. Test on new data: detector.predict(new_data)")


if __name__ == "__main__":
    main()

