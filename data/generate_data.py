"""
Synthetic Data Generator for Leak Detection System

Generates realistic pressure, flow, and acoustic sensor data with injected leak anomalies.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import (
    SENSOR_CONFIG,
    LEAK_CONFIG,
    DATA_GENERATION_CONFIG,
    RAW_DATA_DIR,
)
from utils.helpers import generate_sensor_id, add_noise


class SyntheticDataGenerator:
    """Generate synthetic sensor data for the leak detection system."""
    
    def __init__(self, start_date: str = "2026-02-01", num_days: int = 7):
        self.start_date = start_date
        self.num_days = num_days
        self.zones = SENSOR_CONFIG["zones"]
        self.sensors_per_zone = SENSOR_CONFIG["pressure_sensors_per_zone"]
        
    def generate_pressure_data(self) -> pd.DataFrame:
        """Generate pressure sensor data with leak anomalies."""
        
        # Time range (1 sample per second)
        timestamps = pd.date_range(
            start=self.start_date,
            periods=self.num_days * 24 * 60 * 60,  # seconds in num_days
            freq='1S'
        )
        
        data = []
        
        for zone in self.zones:
            for sensor_idx in range(1, self.sensors_per_zone + 1):
                sensor_id = generate_sensor_id(zone, 'P', sensor_idx)
                
                # Decide if this sensor will detect a leak (random)
                has_leak = np.random.random() < DATA_GENERATION_CONFIG["leak_injection_probability"]
                
                # When does the leak start? (random time in the period)
                if has_leak:
                    leak_start_idx = np.random.randint(len(timestamps) // 4, 3 * len(timestamps) // 4)
                else:
                    leak_start_idx = len(timestamps)  # Never starts
                
                for idx, ts in enumerate(timestamps):
                    # Base values with daily seasonality
                    hour = ts.hour
                    # Higher pressure during work hours (7am-7pm)
                    seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * (hour - 6) / 24)
                    
                    base_pressure = SENSOR_CONFIG["normal_pressure_psi"] * seasonal_factor
                    base_flow = SENSOR_CONFIG["normal_flow_cfm"] * seasonal_factor
                    
                    # Add leak effect
                    if idx >= leak_start_idx:
                        # Leak causes pressure drop and increased flow
                        leak_severity = np.random.choice(['small', 'medium', 'large'], p=[0.6, 0.3, 0.1])
                        
                        if leak_severity == 'small':
                            pressure_drop = np.random.uniform(2, 5)
                            flow_increase = np.random.uniform(20, 50)
                        elif leak_severity == 'medium':
                            pressure_drop = np.random.uniform(5, 15)
                            flow_increase = np.random.uniform(50, 150)
                        else:  # large
                            pressure_drop = np.random.uniform(15, 30)
                            flow_increase = np.random.uniform(150, 300)
                        
                        pressure = base_pressure - pressure_drop
                        flow = base_flow + flow_increase
                        is_anomaly = True
                    else:
                        pressure = base_pressure
                        flow = base_flow
                        is_anomaly = False
                    
                    # Add noise
                    pressure = add_noise(pressure, noise_level=0.02)
                    flow = add_noise(flow, noise_level=0.02)
                    
                    # Temperature (ambient variations)
                    temperature = 20 + 5 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
                    
                    data.append({
                        'timestamp': ts,
                        'sensor_id': sensor_id,
                        'zone': zone,
                        'pressure_psi': round(pressure, 2),
                        'flow_rate_cfm': round(flow, 2),
                        'temperature_c': round(temperature, 2),
                        'is_anomaly': is_anomaly,
                    })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df):,} pressure sensor readings")
        print(f"   Anomalies: {df['is_anomaly'].sum():,} ({df['is_anomaly'].mean()*100:.2f}%)")
        
        return df
    
    def generate_acoustic_data(self, pressure_data: pd.DataFrame) -> pd.DataFrame:
        """Generate acoustic sensor data correlated with pressure anomalies."""
        
        # Get unique timestamps and zones from pressure data
        timestamps = pressure_data['timestamp'].unique()
        
        data = []
        
        for zone in self.zones:
            for sensor_idx in range(1, SENSOR_CONFIG["acoustic_sensors_per_zone"] + 1):
                sensor_id = generate_sensor_id(zone, 'A', sensor_idx)
                
                # Sample every 10 seconds (acoustic sampling is less frequent)
                for ts in timestamps[::10]:
                    # Check if there's a leak in this zone at this time
                    zone_pressure_data = pressure_data[
                        (pressure_data['zone'] == zone) & 
                        (pressure_data['timestamp'] == ts)
                    ]
                    has_leak = zone_pressure_data['is_anomaly'].any()
                    
                    if has_leak:
                        # Leak signature: high energy in specific frequency bands
                        # Frequency bands: 0-1kHz, 1-2kHz, ..., 9-10kHz
                        freq_bands = [
                            np.random.uniform(30, 40),   # 0-1kHz (high if leak)
                            np.random.uniform(40, 50),   # 1-2kHz (high if leak)
                            np.random.uniform(35, 45),   # 2-3kHz
                            np.random.uniform(25, 35),   # 3-4kHz
                            np.random.uniform(30, 40),   # 4-5kHz (ultrasonic leak signature)
                            np.random.uniform(20, 30),   # 5-6kHz
                            np.random.uniform(15, 25),   # 6-7kHz
                            np.random.uniform(10, 20),   # 7-8kHz
                            np.random.uniform(5, 15),    # 8-9kHz
                            np.random.uniform(5, 10),    # 9-10kHz
                        ]
                        amplitude = np.random.uniform(60, 80)  # dB
                        label = 'leak'
                    else:
                        # Normal operation: lower, more uniform frequency distribution
                        freq_bands = [
                            np.random.uniform(15, 25),
                            np.random.uniform(15, 25),
                            np.random.uniform(10, 20),
                            np.random.uniform(10, 20),
                            np.random.uniform(8, 15),
                            np.random.uniform(5, 12),
                            np.random.uniform(5, 10),
                            np.random.uniform(3, 8),
                            np.random.uniform(2, 5),
                            np.random.uniform(1, 3),
                        ]
                        amplitude = np.random.uniform(35, 55)  # dB
                        label = 'normal'
                    
                    data.append({
                        'timestamp': ts,
                        'sensor_id': sensor_id,
                        'zone': zone,
                        'freq_band_0_1k': freq_bands[0],
                        'freq_band_1_2k': freq_bands[1],
                        'freq_band_2_3k': freq_bands[2],
                        'freq_band_3_4k': freq_bands[3],
                        'freq_band_4_5k': freq_bands[4],
                        'freq_band_5_6k': freq_bands[5],
                        'freq_band_6_7k': freq_bands[6],
                        'freq_band_7_8k': freq_bands[7],
                        'freq_band_8_9k': freq_bands[8],
                        'freq_band_9_10k': freq_bands[9],
                        'amplitude_db': round(amplitude, 2),
                        'label': label,
                    })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df):,} acoustic sensor readings")
        print(f"   Leak signatures: {(df['label'] == 'leak').sum():,} ({(df['label'] == 'leak').mean()*100:.2f}%)")
        
        return df
    
    def generate_metadata(self) -> pd.DataFrame:
        """Generate sensor metadata (location, type, installation date, etc.)."""
        
        metadata = []
        
        # Pressure sensors
        for zone in self.zones:
            for sensor_idx in range(1, self.sensors_per_zone + 1):
                sensor_id = generate_sensor_id(zone, 'P', sensor_idx)
                
                metadata.append({
                    'sensor_id': sensor_id,
                    'sensor_type': 'pressure',
                    'zone': zone,
                    'location_x': np.random.uniform(0, 100),  # meters
                    'location_y': np.random.uniform(0, 100),
                    'installation_date': datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365)),
                    'pipe_material': np.random.choice(['steel', 'copper', 'pvc']),
                    'pipe_age_years': np.random.randint(1, 20),
                    'joint_type': np.random.choice(['welded', 'threaded', 'flanged']),
                })
        
        # Acoustic sensors
        for zone in self.zones:
            for sensor_idx in range(1, SENSOR_CONFIG["acoustic_sensors_per_zone"] + 1):
                sensor_id = generate_sensor_id(zone, 'A', sensor_idx)
                
                metadata.append({
                    'sensor_id': sensor_id,
                    'sensor_type': 'acoustic',
                    'zone': zone,
                    'location_x': np.random.uniform(0, 100),
                    'location_y': np.random.uniform(0, 100),
                    'installation_date': datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365)),
                    'pipe_material': None,
                    'pipe_age_years': None,
                    'joint_type': None,
                })
        
        df = pd.DataFrame(metadata)
        print(f"✅ Generated metadata for {len(df)} sensors")
        
        return df
    
    def save_data(self, pressure_df: pd.DataFrame, acoustic_df: pd.DataFrame, metadata_df: pd.DataFrame):
        """Save generated data to CSV files."""
        
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        pressure_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
        acoustic_file = RAW_DATA_DIR / "acoustic_sensor_data.csv"
        metadata_file = RAW_DATA_DIR / "sensor_metadata.csv"
        
        pressure_df.to_csv(pressure_file, index=False)
        acoustic_df.to_csv(acoustic_file, index=False)
        metadata_df.to_csv(metadata_file, index=False)
        
        print(f"\n📁 Data saved to:")
        print(f"   {pressure_file}")
        print(f"   {acoustic_file}")
        print(f"   {metadata_file}")
    
    def generate_all(self):
        """Generate all synthetic data."""
        print(f"🏭 Generating synthetic sensor data for {self.num_days} days...\n")
        
        # Generate data
        pressure_df = self.generate_pressure_data()
        acoustic_df = self.generate_acoustic_data(pressure_df)
        metadata_df = self.generate_metadata()
        
        # Save to files
        self.save_data(pressure_df, acoustic_df, metadata_df)
        
        print("\n✅ Data generation complete!")
        print(f"\nNext steps:")
        print(f"1. Explore the data: data/raw/*.csv")
        print(f"2. Train models: python models/01_isolation_forest/train.py")
        print(f"3. Run dashboard: streamlit run dashboard/app.py")


if __name__ == "__main__":
    generator = SyntheticDataGenerator(
        start_date="2026-02-01",
        num_days=DATA_GENERATION_CONFIG["num_days"]
    )
    generator.generate_all()
