"""
Real-time sensor data generator for pipe network monitoring.
Generates data every second for all 10 pipes with automatic anomaly injection.
"""

import csv
import time
import random
from datetime import datetime
from pathlib import Path

# Pipe network configuration
PIPE_IDS = [
    'P-001', 'P-002', 'P-003', 'P-004', 'P-005',
    'P-006', 'P-007', 'P-008', 'P-009', 'P-010'
]

# Output configuration
OUTPUT_DIR = Path(__file__).parent / 'generated'
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / 'live_sensor_data.csv'

# Anomaly injection parameters
ANOMALIES_PER_MINUTE = 1
ANOMALY_DURATION_SEC = 30  # Each anomaly lasts 30 seconds


class PipeNetwork:
    """Manages sensor data generation for the entire pipe network."""
    
    def __init__(self):
        self.pipes = PIPE_IDS
        self.active_anomalies = {}   # {pipe_id: start_time}
        self.next_anomaly_time = time.time() + random.uniform(5, 60)
    
    def update_anomalies(self):
        """Inject 1 anomaly per minute, each lasting exactly 30 seconds."""
        now = time.time()
        
        # Clear anomalies that have lasted >= 30 seconds
        to_remove = [pid for pid, t0 in self.active_anomalies.items() if now - t0 >= ANOMALY_DURATION_SEC]
        for pid in to_remove:
            del self.active_anomalies[pid]
            print(f"  [x] ANOMALY CLEARED: {pid}  (after {ANOMALY_DURATION_SEC}s)")
        
        # Inject a new anomaly if it's time
        if now >= self.next_anomaly_time:
            # Pick a random pipe that isn't already anomalous
            candidates = [p for p in self.pipes if p not in self.active_anomalies]
            if candidates:
                pipe_id = random.choice(candidates)
                self.active_anomalies[pipe_id] = now
                print(f"  [!] ANOMALY STARTED: {pipe_id}")
            # Schedule next anomaly in ~60 seconds
            self.next_anomaly_time = now + random.uniform(50, 70)
    
    def generate_reading(self, pipe_id, pipe_index):
        """Generate sensor readings for a single pipe.
        
        Normal baselines aligned to training data distribution:
          pressure_psi   ~ 114.9  (std ~4.9)
          temperature_c  ~ 22.7   (std ~2.0)
          humidity_%     ~ 45.7   (std ~2.8)
        """
        is_anomaly = pipe_id in self.active_anomalies
        
        # Base pressure decreases slightly along the network
        base_pressure = 114.9 - pipe_index * 0.3
        base_temp     = 22.7
        base_humidity = 45.7
        
        if is_anomaly:
            # Anomaly: significant pressure drop, temp rise, humidity change
            pressure_drop = random.uniform(15, 25)
            ps = base_pressure + random.gauss(0, 2.0)
            pe = base_pressure - pressure_drop + random.gauss(0, 3.0)
            temp = random.gauss(base_temp + 5, 2.5)
            humidity = random.gauss(base_humidity - 12, 4.0)
        else:
            # Normal: stable readings matching training distribution
            ps = base_pressure + random.gauss(0, 1.5)
            pe = base_pressure - 1.0 + random.gauss(0, 1.2)
            temp = random.gauss(base_temp, 1.0)
            humidity = random.gauss(base_humidity, 1.5)
        
        return {
            f'PS_{pipe_id}': round(ps, 2),
            f'PE_{pipe_id}': round(pe, 2),
            f'T_{pipe_id}':  round(temp, 2),
            f'H_{pipe_id}':  round(humidity, 2)
        }
    
    def generate_tick(self):
        """Generate a complete sensor reading for all pipes."""
        self.update_anomalies()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = {'timestamp': timestamp}
        
        for idx, pipe_id in enumerate(self.pipes):
            row.update(self.generate_reading(pipe_id, idx))
        
        return row


def initialize_csv(filename):
    """Create CSV file with headers."""
    headers = ['timestamp']
    for pipe_id in PIPE_IDS:
        headers.extend([
            f'PS_{pipe_id}',
            f'PE_{pipe_id}',
            f'T_{pipe_id}',
            f'H_{pipe_id}'
        ])
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
    
    print(f"[*] Initialized: {filename}")


def run_generator(duration_sec=None):
    """
    Run the data generator continuously.
    
    Args:
        duration_sec: Optional duration in seconds. If None, runs indefinitely.
    """
    network = PipeNetwork()
    initialize_csv(OUTPUT_FILE)
    
    print("\n[*] Starting data generator...")
    print(f"[*] Pipes: {len(PIPE_IDS)} ({', '.join(PIPE_IDS)})")
    print(f"[*] Tick rate: 1 Hz (every 1 second)")
    print(f"[!] Anomalies: {ANOMALIES_PER_MINUTE} per minute (~{ANOMALY_DURATION_SEC}s duration)")
    print(f"[*] Output: {OUTPUT_FILE}")
    print("\n[Ctrl+C to stop]\n")
    
    tick_count = 0
    start_time = time.time()
    
    try:
        while True:
            tick_start = time.time()
            
            # Generate data
            row = network.generate_tick()
            
            # Write to CSV
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writerow(row)
            
            tick_count += 1
            anomaly_str = f" [{len(network.active_anomalies)} active]" if network.active_anomalies else ""
            print(f"[tick] {tick_count:4d} | {row['timestamp']}{anomaly_str}")
            
            # Check duration limit
            if duration_sec and (time.time() - start_time) >= duration_sec:
                break
            
            # Sleep to maintain 1 Hz rate
            elapsed = time.time() - tick_start
            sleep_time = max(0, 1.0 - elapsed)
            time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\n\n[STOP] Generator stopped by user")
    
    print(f"\n[*] Total ticks generated: {tick_count}")
    print(f"[*] Runtime: {time.time() - start_time:.1f} seconds")
    print(f"[*] Data saved to: {OUTPUT_FILE}\n")


if __name__ == '__main__':
    # Run indefinitely (use Ctrl+C to stop)
    run_generator()
    
    # Or run for a specific duration (e.g., 5 minutes):
    # run_generator(duration_sec=300)
