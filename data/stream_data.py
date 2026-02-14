"""
Real-time Data Stream Generator for Leak Detection System

Generates continuous pressure sensor data in JSON format (JSONL - one JSON per line).
Output to stdout - pipe to Kafka or other streaming tools.

Usage:
    python data/stream_data.py
    python data/stream_data.py | kafka-console-producer --topic sensor-readings
"""

import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import SENSOR_CONFIG
from utils.helpers import generate_sensor_id, add_noise


class StreamDataGenerator:
    """Generate real-time sensor data stream."""
    
    def __init__(self):
        self.zones = SENSOR_CONFIG["zones"]
        self.sensors_per_zone = SENSOR_CONFIG["pressure_sensors_per_zone"]
        self.base_pressure = SENSOR_CONFIG["normal_pressure_psi"]
        self.base_humidity = SENSOR_CONFIG["normal_humidity_percent"]
        
        # Track which sensors have active leaks
        self.active_leaks = {}
        
    def _should_trigger_leak(self, sensor_id: str) -> bool:
        """Randomly decide if a new leak should start (low probability)."""
        if sensor_id not in self.active_leaks:
            # 5% chance of new leak starting per reading
            return np.random.random() < 0.05
        return False
    
    def _get_leak_params(self, sensor_id: str):
        """Get or create leak parameters for a sensor."""
        if sensor_id not in self.active_leaks:
            # Initialize new leak
            severity = np.random.choice(['small', 'medium', 'large'], p=[0.6, 0.3, 0.1])
            
            if severity == 'small':
                pressure_drop = np.random.uniform(2, 5)
                humidity_change = np.random.uniform(-5, -2)
            elif severity == 'medium':
                pressure_drop = np.random.uniform(5, 15)
                humidity_change = np.random.uniform(-10, -5)
            else:  # large
                pressure_drop = np.random.uniform(15, 30)
                humidity_change = np.random.uniform(-15, -10)
            
            self.active_leaks[sensor_id] = {
                'severity': severity,
                'pressure_drop': pressure_drop,
                'humidity_change': humidity_change,
                'start_time': datetime.now().isoformat()
            }
        
        return self.active_leaks[sensor_id]
    
    def _maybe_heal_leak(self, sensor_id: str):
        """Randomly heal a leak (simulating repair)."""
        if sensor_id in self.active_leaks:
            # 0.1% chance of leak being repaired per reading
            if np.random.random() < 0.001:
                del self.active_leaks[sensor_id]
    
    def generate_reading(self, zone: str, sensor_idx: int) -> dict:
        """Generate a single sensor reading."""
        sensor_id = generate_sensor_id(zone, 'P', sensor_idx)
        timestamp = datetime.now()
        
        # Seasonal variation based on hour
        hour = timestamp.hour
        seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        base_pressure = self.base_pressure * seasonal_factor
        base_humidity = self.base_humidity * (1.0 - 0.05 * np.sin(2 * np.pi * (hour - 6) / 24))
        
        # Check for leak trigger
        if self._should_trigger_leak(sensor_id):
            leak_params = self._get_leak_params(sensor_id)
        
        # Apply leak effect if active
        if sensor_id in self.active_leaks:
            leak = self.active_leaks[sensor_id]
            pressure = base_pressure - leak['pressure_drop']
            humidity = max(0, min(100, base_humidity + leak['humidity_change']))
            is_anomaly = True
            
            # Maybe heal this leak
            self._maybe_heal_leak(sensor_id)
        else:
            pressure = base_pressure
            humidity = base_humidity
            is_anomaly = False
        
        # Add noise
        pressure = add_noise(pressure, noise_level=0.02)
        humidity = add_noise(humidity, noise_level=0.02)
        humidity = max(0, min(100, humidity))
        
        # Temperature (ambient variations)
        temperature = 20 + 5 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
        
        return {
            'timestamp': timestamp.isoformat(),
            'sensor_id': sensor_id,
            'zone': zone,
            'pressure_psi': round(pressure, 2),
            'humidity_percent': round(humidity, 2),
            'temperature_c': round(temperature, 2),
            'is_anomaly': is_anomaly,
            'airflow_rate': round(np.random.uniform(10, 50), 2),
            'power_kw': round(np.random.uniform(5, 15), 2)
        }
    
    def stream_forever(self, interval_seconds: float = 5.0):
        """Generate and print sensor readings indefinitely."""
        print(f"🔄 Starting real-time data stream (interval: {interval_seconds}s)", file=sys.stderr)
        print(f"📡 Monitoring {len(self.zones)} zones, {self.sensors_per_zone} sensors per zone", file=sys.stderr)
        print(f"💡 Outputting JSONL format to stdout. Press Ctrl+C to stop.\n", file=sys.stderr)
        
        reading_count = 0
        
        try:
            while True:
                # Generate readings for all sensors
                for zone in self.zones:
                    for sensor_idx in range(1, self.sensors_per_zone + 1):
                        reading = self.generate_reading(zone, sensor_idx)
                        
                        # Output as single-line JSON
                        print(json.dumps(reading), flush=True)
                        reading_count += 1
                
                # Status update to stderr (won't interfere with stdout stream)
                if reading_count % 100 == 0:
                    active_leak_count = len(self.active_leaks)
                    print(f"✅ Generated {reading_count} readings | Active leaks: {active_leak_count}", file=sys.stderr)
                
                # Wait before next batch
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stream stopped. Total readings: {reading_count}", file=sys.stderr)
            if self.active_leaks:
                print(f"📊 Active leaks at shutdown: {len(self.active_leaks)}", file=sys.stderr)
                for sensor_id, leak in self.active_leaks.items():
                    print(f"   • {sensor_id}: {leak['severity']} severity", file=sys.stderr)


if __name__ == "__main__":
    # Parse interval from command line if provided
    interval = 5.0
    if len(sys.argv) > 1:
        try:
            interval = float(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid interval: {sys.argv[1]}. Using default: 5.0s", file=sys.stderr)
    
    generator = StreamDataGenerator()
    generator.stream_forever(interval_seconds=interval)
