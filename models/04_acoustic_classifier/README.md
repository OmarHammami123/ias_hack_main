# Model 04: Acoustic Classifier - CNN for Leak Detection

**Team Member:** ___________  
**Priority:** 💡 Nice to Have (Differentiator!)  
**Estimated Time:** 2-3 hours  
**Status:** 🔴 Not Started

## 📋 Your Task

Build a **CNN (Convolutional Neural Network)** to classify acoustic frequency patterns as 'leak' or 'normal'.

## 🎯 What It Does

- Analyzes sound frequency patterns from acoustic sensors
- Detects ultrasonic "hiss" characteristic of compressed air leaks
- Provides **secondary confirmation** for pressure-based detection
- Reduces false positives when combined with Model 01

## 🎵 Why Acoustics?

Compressed air leaks create distinctive high-frequency sounds (ultrasonic range):
- **Normal operation:** Low, steady hum from equipment
- **Leak:** Sharp, high-pitched hiss (especially in 1-5 kHz range)

Even small leaks (1-2mm) produce detectable acoustic signatures!

## 📥 Inputs

- **Frequency Bands:** Energy in 10 frequency ranges (0-1kHz, 1-2kHz, ..., 9-10kHz)
- **Amplitude:** Overall sound level in dB
- Each reading represents a ~1 second audio snapshot

### Example Input:
```python
{
  'freq_band_0_1k': 25.3,   # Low rumble
  'freq_band_1_2k': 42.1,   # HIGH = leak signature
  'freq_band_2_3k': 38.7,   # HIGH = leak signature
  'freq_band_3_4k': 28.2,
  'freq_band_4_5k': 35.8,   # Ultrasonic leak energy
  'freq_band_5_6k': 22.1,
  ...
  'amplitude_db': 68.5
}
```

## 📤 Outputs

- **Binary Classification:** leak (1) or normal (0)
- **Confidence Score:** 0.0 to 1.0 (how certain the model is)
- **Predicted Class Probabilities:** [P(normal), P(leak)]

## ✅ Success Criteria

- **Accuracy:** > 85%
- **False Positive Rate:** < 15%
- **Complements Pressure Detection:** When both models agree → high confidence
- **Fast Inference:** < 50ms per sample

## 🏗️ Model Architecture

The starter code uses a **1D CNN** suitable for frequency band features:

```
Input (11 features)
    ↓
Reshape → (11, 1)
    ↓
Conv1D(32 filters) + ReLU + BatchNorm
    ↓
MaxPooling1D
    ↓
Conv1D(64 filters) + ReLU + BatchNorm
    ↓
MaxPooling1D
    ↓
Flatten
    ↓
Dense(64) + ReLU + Dropout
    ↓
Dense(1) + Sigmoid
    ↓
Output: [0 or 1]
```

## 🚀 Quick Start

### 1. Generate Acoustic Data
```bash
cd ../..
python data/generate_data.py
```

### 2. Train the CNN
```bash
python train.py
```

### 3. Expected Output
```
Epoch 1/50
████████████████████ 245/245 - loss: 0.4123 - accuracy: 0.8234
Epoch 50/50
████████████████████ 245/245 - loss: 0.1245 - accuracy: 0.9567

✅ Model saved to: acoustic_classifier_model.h5
📊 Test Accuracy: 88.3%
📉 False Positive Rate: 11.2%
```

## 💡 Improvement Ideas

### 1. **Add More Convolutional Layers**
```python
layers.Conv1D(128, kernel_size=3, activation='relu', padding='same'),
layers.BatchNormalization(),
layers.MaxPooling1D(pool_size=2),
```

### 2. **Class Weighting** (if data is imbalanced)
```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

model.fit(X_train, y_train, class_weight=class_weight_dict)
```

### 3. **Data Augmentation**
```python
# Add noise to training samples
def add_noise(X, noise_level=0.05):
    noise = np.random.normal(0, noise_level, X.shape)
    return X + noise

X_train_augmented = np.vstack([X_train, add_noise(X_train)])
```

### 4. **Attention Mechanism**
```python
# Focus on important frequency bands
from tensorflow.keras.layers import Attention

# Add after Conv layers
attention_output = Attention()([conv_output, conv_output])
```

## 📊 Visualizations to Create

### 1. **Training History**
```python
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Validation')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Validation')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.savefig('training_history.png')
```

### 2. **Confusion Matrix**
```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_test, predictions)
disp = ConfusionMatrixDisplay(cm, display_labels=['Normal', 'Leak'])
disp.plot()
plt.savefig('confusion_matrix.png')
```

### 3. **Frequency Signature Comparison**
```python
# Average frequency profile for leaks vs normal
leak_avg = df[df['label'] == 'leak'][freq_columns].mean()
normal_avg = df[df['label'] == 'normal'][freq_columns].mean()

plt.bar(range(10), leak_avg, alpha=0.7, label='Leak Signature')
plt.bar(range(10), normal_avg, alpha=0.7, label='Normal Operation')
plt.xlabel('Frequency Band (kHz)')
plt.ylabel('Energy Level')
plt.legend()
plt.savefig('frequency_signatures.png')
```

## 🔍 Model Validation

### Test These Scenarios:

**1. Pure Leak Signals**
```python
# Should have high confidence
pure_leaks = df[df['label'] == 'leak']
predictions = model.predict(pure_leaks[feature_columns])
assert predictions.mean() > 0.85
```

**2. Pure Normal Signals**
```python
pure_normal = df[df['label'] == 'normal']
predictions = model.predict(pure_normal[feature_columns])
assert predictions.mean() < 0.15
```

**3. Noisy/Ambiguous Signals**
```python
# Create borderline cases
# What happens when energy levels are moderate?
```

## 🎯 Integration with Other Models

### Multi-Modal Detection Strategy:

```python
# Combine Model 01 (Isolation Forest) + Model 04 (Acoustic)
def combined_detection(pressure_anomaly_score, acoustic_confidence):
    if pressure_anomaly_score < 0 and acoustic_confidence > 0.8:
        return "CONFIRMED_LEAK"  # Both agree
    elif pressure_anomaly_score < 0 or acoustic_confidence > 0.8:
        return "PROBABLE_LEAK"  # One detected
    else:
        return "NORMAL"
```

## 📊 Sample Output

```json
{
  "timestamp": "2026-02-14T10:30:15Z",
  "sensor_id": "A_B_001",
  "zone": "Zone_B",
  "classification": "leak",
  "confidence": 0.94,
  "frequency_signature": {
    "peak_band": "1-2kHz",
    "peak_energy": 45.3,
    "ultrasonic_energy": 32.1
  },
  "correlation_with_pressure": true
}
```

## 🐛 Troubleshooting

**Model always predicts one class:**
- Check class balance in training data
- Use class weights
- Adjust decision threshold (default is 0.5)

**Overfitting (train acc >> test acc):**
```python
# Add dropout
layers.Dropout(0.5)

# Or reduce model complexity
# Fewer filters, fewer layers
```

**Underfitting (low accuracy overall):**
- Add more layers
- Increase model capacity
- Train for more epochs
- Check if features are normalized

**Slow training:**
```python
# Use smaller batch size
batch_size = 16  # instead of 32

# Or reduce epochs
epochs = 30  # instead of 50
```

## 📝 Deliverables

- [ ] Trained CNN model (`acoustic_classifier_model.h5`)
- [ ] Scaler for input features (`acoustic_scaler.pkl`)
- [ ] Training history plot
- [ ] Confusion matrix visualization
- [ ] Frequency signature comparison plot
- [ ] Model performance report (accuracy, precision, recall, F1)
- [ ] Brief explanation of hyperparameter choices

## 🚀 Bonus Challenges

### 1. **Real Spectrogram CNN (2D)**
If you have time, upgrade to actual spectrograms:
```python
# 2D CNN for spectrograms
layers.Conv2D(32, (3, 3), activation='relu')
layers.MaxPooling2D((2, 2))
```

### 2. **Transfer Learning**
Use a pre-trained audio classification model:
```python
from tensorflow.keras.applications import EfficientNetB0
base_model = EfficientNetB0(weights='imagenet', include_top=False)
```

### 3. **Real-Time Inference**
Optimize for edge deployment:
```python
import tensorflow as tf

# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
```

---

**Questions?** This is the most complex model. Don't hesitate to ask for help!
