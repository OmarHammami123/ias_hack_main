"""
Model 04: Acoustic Leak Classifier (CNN on Spectrograms)

PRIORITY: 💡 Nice to Have (Differentiator)
ESTIMATED TIME: 2-3 hours
TEAM MEMBER: _________

DESCRIPTION:
CNN model that classifies audio frequency patterns as 'leak' or 'normal'.
Uses frequency band features as a proxy for spectrograms.

INPUTS:
- Frequency band energies (10 bands: 0-1kHz, 1-2kHz, ..., 9-10kHz)
- Amplitude (dB)

OUTPUTS:
- Binary classification: leak (1) or normal (0)
- Confidence score (0-1)

SUCCESS CRITERIA:
- Accuracy > 85%
- Low false positive rate (< 15%)
- Complements pressure-based detection
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.config import MODEL_CONFIG, RAW_DATA_DIR, MODELS_DIR


class AcousticLeakClassifier:
    """CNN-based classifier for acoustic leak detection."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'freq_band_0_1k', 'freq_band_1_2k', 'freq_band_2_3k',
            'freq_band_3_4k', 'freq_band_4_5k', 'freq_band_5_6k',
            'freq_band_6_7k', 'freq_band_7_8k', 'freq_band_8_9k',
            'freq_band_9_10k', 'amplitude_db'
        ]
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load acoustic sensor data."""
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"   Loaded {len(df):,} rows")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and labels."""
        
        X = df[self.feature_columns].values
        
        # Convert label to binary
        if 'label' in df.columns:
            y = (df['label'] == 'leak').astype(int).values
            print(f"📊 Feature shape: {X.shape}")
            print(f"   Leak samples: {y.sum():,} ({y.mean()*100:.2f}%)")
        else:
            y = None
        
        return X, y
    
    def build_model(self, input_dim: int):
        """Build CNN model for frequency pattern classification."""
        
        # Note: This is a 1D CNN suitable for frequency band features
        # For actual spectrograms, you'd use 2D CNN
        
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=(input_dim,)),
            
            # Reshape for 1D convolution
            layers.Reshape((input_dim, 1)),
            
            # Convolutional layers
            layers.Conv1D(32, kernel_size=3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            
            layers.Conv1D(64, kernel_size=3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            # Output layer
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        return model
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the CNN model."""
        print("\n🎯 Training Acoustic Classifier...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Training set: {len(X_train):,} samples")
        print(f"   Test set: {len(X_test):,} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build model
        self.model = self.build_model(input_dim=X_train.shape[1])
        
        print("\n📐 Model Architecture:")
        self.model.summary()
        
        # Callbacks
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        # Train
        print("\n🚀 Training...")
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_test_scaled, y_test),
            epochs=MODEL_CONFIG["acoustic_classifier"]["epochs"],
            batch_size=MODEL_CONFIG["acoustic_classifier"]["batch_size"],
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Evaluate
        print("\n📈 Evaluating...")
        test_loss, test_acc, test_auc = self.model.evaluate(X_test_scaled, y_test, verbose=0)
        
        print(f"\n   Test Accuracy: {test_acc:.4f}")
        print(f"   Test AUC: {test_auc:.4f}")
        
        # Detailed classification report
        y_pred_proba = self.model.predict(X_test_scaled, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Leak']))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        print("\n✅ Training complete!")
        
        return {
            'history': history,
            'test_accuracy': test_acc,
            'test_auc': test_auc,
        }
    
    def predict(self, X: np.ndarray) -> tuple:
        """Predict leak probability."""
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict(X_scaled, verbose=0).flatten()
        predictions = (probabilities > 0.5).astype(int)
        
        return predictions, probabilities
    
    def save_model(self, output_dir: str):
        """Save trained model."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save Keras model
        self.model.save(output_path / "acoustic_model.h5")
        
        # Save scaler
        joblib.dump(self.scaler, output_path / "scaler.pkl")
        
        print(f"\n💾 Model saved to {output_dir}/")
    
    def load_model(self, model_dir: str):
        """Load pre-trained model."""
        model_path = Path(model_dir)
        
        self.model = keras.models.load_model(model_path / "acoustic_model.h5")
        self.scaler = joblib.load(model_path / "scaler.pkl")
        
        print(f"✅ Model loaded from {model_dir}/")


def main():
    """Main training pipeline."""
    
    print("=" * 60)
    print("MODEL 04: ACOUSTIC LEAK CLASSIFIER")
    print("=" * 60)
    
    # Initialize classifier
    classifier = AcousticLeakClassifier()
    
    # Load data
    data_file = RAW_DATA_DIR / "acoustic_sensor_data.csv"
    
    if not data_file.exists():
        print(f"\n⚠️  {data_file} not found!")
        print("Run data generation first: python data/generate_data.py")
        return
    
    df = classifier.load_data(data_file)
    
    # Prepare features
    X, y = classifier.prepare_features(df)
    
    # Train model
    results = classifier.train(X, y)
    
    # Save model
    model_output_dir = MODELS_DIR / "04_acoustic_classifier" / "trained_model"
    classifier.save_model(model_output_dir)
    
    print("\n" + "=" * 60)
    print("✅ MODEL 04 COMPLETE!")
    print("=" * 60)
    print("\nThis model provides a second modality for leak detection.")
    print("Combine with pressure-based detection for higher confidence!")


if __name__ == "__main__":
    main()
