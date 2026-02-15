"""
Generate historical pipe sensor data for Model 05 training.

Creates synthetic data matching the live_sensor_data.csv format:
- 10 pipes (P-001 to P-010)
- 4 sensors per pipe: PS (Pressure Start), PE (Pressure End), T (Temperature), H (Humidity)
- Simulates realistic leak patterns over 7-14 days
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_DAYS = 14  # Generate 14 days of historical data
SAMPLE_RATE_SECONDS = 60  # 1 sample per minute
OUTPUT_DIR = Path(__file__).parent / "generated"

# Pipe configuration (matches dashboard3)
PIPES = [f'P-{str(i).zfill(3)}' for i in range(1, 11)]  # P-001 to P-010

# Normal operating parameters
BASE_PRESSURE = 120.0  # PSI
NORMAL_PRESSURE_DROP = 1.5  # Normal drop from inlet to outlet
BASE_TEMPERATURE = 24.0  # Celsius
BASE_HUMIDITY = 42.0  # Percent

# Leak simulation parameters
LEAK_PROBABILITY = 0.005  # 0.5% - more realistic (1-2 leaks per pipe per month)
LEAK_DURATION_HOURS = (2, 12)  # Leak lasts 2-12 hours
LEAK_SEVERITY_DIST = [0.6, 0.3, 0.1]  # 60% small, 30% medium, 10% large


def add_noise(value, noise_level=0.02):
    """Add Gaussian noise to sensor reading."""
    noise = np.random.normal(0, abs(value) * noise_level)
    return value + noise


def generate_normal_reading(pipe_index, hour):
    """Generate normal sensor reading for a pipe."""
    
    # Add daily seasonality (higher pressure during work hours)
    seasonal_factor = 1.0 + 0.05 * np.sin(2 * np.pi * (hour - 6) / 24)
    
    # Base pressure decreases slightly along the network
    base_pressure = BASE_PRESSURE - pipe_index * 0.6
    
    pressure_start = add_noise(base_pressure * seasonal_factor, 0.015)
    pressure_end = add_noise(pressure_start - NORMAL_PRESSURE_DROP, 0.015)
    temperature = add_noise(BASE_TEMPERATURE + 0.5 * np.sin(2 * np.pi * (hour - 6) / 24), 0.03)
    humidity = add_noise(BASE_HUMIDITY - 0.8 * np.sin(2 * np.pi * (hour - 6) / 24), 0.03)
    
    return {
        'pressure_start': round(pressure_start, 2),
        'pressure_end': round(pressure_end, 2),
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2)
    }


def generate_leak_reading(pipe_index, hour, severity):
    """Generate sensor reading during a leak."""
    
    seasonal_factor = 1.0 + 0.05 * np.sin(2 * np.pi * (hour - 6) / 24)
    base_pressure = BASE_PRESSURE - pipe_index * 0.6
    
    # Leak causes significant pressure drop (aligned with Model 05 detection thresholds)
    if severity == 'small':
        pressure_drop = np.random.uniform(8, 15)  # 8 PSI minimum to avoid noise confusion
        temp_increase = np.random.uniform(2, 4)
        humidity_change = np.random.uniform(5, 10)
    elif severity == 'medium':
        pressure_drop = np.random.uniform(15, 25)
        temp_increase = np.random.uniform(4, 7)
        humidity_change = np.random.uniform(10, 15)
    else:  # large
        pressure_drop = np.random.uniform(25, 35)
        temp_increase = np.random.uniform(7, 10)
        humidity_change = np.random.uniform(15, 20)
    
    pressure_start = add_noise(base_pressure * seasonal_factor, 0.02)
    pressure_end = add_noise(pressure_start - pressure_drop, 0.03)
    temperature = add_noise(BASE_TEMPERATURE + temp_increase + 0.5 * np.sin(2 * np.pi * (hour - 6) / 24), 0.05)
    humidity = add_noise(BASE_HUMIDITY + humidity_change - 0.8 * np.sin(2 * np.pi * (hour - 6) / 24), 0.05)
    
    return {
        'pressure_start': round(pressure_start, 2),
        'pressure_end': round(pressure_end, 2),
        'temperature': round(temperature, 2),
        'humidity': round(max(0, min(100, humidity)), 2)  # Clamp 0-100
    }


def main():
    """Generate historical pipe sensor data."""
    
    print("=" * 70)
    print("PIPE SENSOR HISTORICAL DATA GENERATOR")
    print("=" * 70)
    
    # Calculate time range
    end_time = datetime.now().replace(second=0, microsecond=0)
    start_time = end_time - timedelta(days=NUM_DAYS)
    total_samples = int(NUM_DAYS * 24 * 60 * 60 / SAMPLE_RATE_SECONDS)
    
    print(f"\n📅 Time range: {start_time} to {end_time}")
    print(f"⏱️  Sample rate: {SAMPLE_RATE_SECONDS}s ({3600 / SAMPLE_RATE_SECONDS:.0f} samples/hour)")
    print(f"📊 Total samples: {total_samples:,}")
    print(f"🔧 Pipes: {len(PIPES)}")
    
    # Initialize leak schedule for each pipe
    leak_schedule = {}
    for pipe_id in PIPES:
        leak_schedule[pipe_id] = []
    
    # Randomly schedule leaks
    print(f"\n🎲 Scheduling random leaks (probability: {LEAK_PROBABILITY * 100:.1f}% per pipe per day)...")
    
    for pipe_id in PIPES:
        current_time = start_time
        while current_time < end_time:
            # Check if leak should start
            if np.random.random() < LEAK_PROBABILITY:
                # Choose severity
                severity = np.random.choice(['small', 'medium', 'large'], p=LEAK_SEVERITY_DIST)
                
                # Choose duration
                duration_hours = np.random.uniform(*LEAK_DURATION_HOURS)
                leak_end = current_time + timedelta(hours=duration_hours)
                
                leak_schedule[pipe_id].append({
                    'start': current_time,
                    'end': leak_end,
                    'severity': severity
                })
                
                # Skip ahead to avoid overlapping leaks
                current_time = leak_end + timedelta(hours=np.random.uniform(12, 48))
            else:
                current_time += timedelta(days=1)
    
    total_leaks = sum(len(leaks) for leaks in leak_schedule.values())
    print(f"   ✅ Scheduled {total_leaks} leak events across all pipes")
    
    # Generate time series data
    print(f"\n🔄 Generating {total_samples:,} sensor readings...")
    
    timestamps = []
    data_rows = []
    
    current_time = start_time
    sample_count = 0
    
    while current_time <= end_time:
        row = {'timestamp': current_time}
        
        for pipe_index, pipe_id in enumerate(PIPES):
            # Check if pipe is currently leaking
            is_leaking = False
            leak_severity = None
            
            for leak in leak_schedule[pipe_id]:
                if leak['start'] <= current_time <= leak['end']:
                    is_leaking = True
                    leak_severity = leak['severity']
                    break
            
            # Generate reading
            if is_leaking:
                reading = generate_leak_reading(pipe_index, current_time.hour, leak_severity)
            else:
                reading = generate_normal_reading(pipe_index, current_time.hour)
            
            # Add to row
            row[f'PS_{pipe_id}'] = reading['pressure_start']
            row[f'PE_{pipe_id}'] = reading['pressure_end']
            row[f'T_{pipe_id}'] = reading['temperature']
            row[f'H_{pipe_id}'] = reading['humidity']
        
        data_rows.append(row)
        current_time += timedelta(seconds=SAMPLE_RATE_SECONDS)
        sample_count += 1
        
        # Progress indicator
        if sample_count % 10000 == 0:
            progress = (sample_count / total_samples) * 100
            print(f"   Progress: {progress:.1f}% ({sample_count:,}/{total_samples:,})")
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    print(f"\n✅ Generated {len(df):,} rows")
    print(f"   Columns: {len(df.columns)} ({len(PIPES) * 4} sensors + timestamp)")
    
    # Save to CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "pipe_history.csv"
    
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Statistics
    print(f"\n📊 LEAK STATISTICS:")
    for pipe_id in PIPES:
        leak_count = len(leak_schedule[pipe_id])
        if leak_count > 0:
            severities = [leak['severity'] for leak in leak_schedule[pipe_id]]
            small = severities.count('small')
            medium = severities.count('medium')
            large = severities.count('large')
            print(f"   {pipe_id}: {leak_count} leaks (Small: {small}, Medium: {medium}, Large: {large})")
    
    print("\n" + "=" * 70)
    print("✅ HISTORICAL DATA GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\n🎯 Next step: Run Model 05 training:")
    print(f"   cd models/05_predictive_forecast")
    print(f"   python train.py")


if __name__ == "__main__":
    main()
