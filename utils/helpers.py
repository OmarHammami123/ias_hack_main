"""
Helper functions shared across the project.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


def calculate_leak_cost(leak_size_mm: float, hours_per_year: int = 8760) -> float:
    """
    Calculate annual cost of a leak based on its size.
    
    Args:
        leak_size_mm: Leak diameter in millimeters
        hours_per_year: Operating hours per year (default: 24/7)
    
    Returns:
        Annual cost in Tunisian Dinars (TND)
    """
    from utils.config import COST_CONFIG
    
    # Estimate CFM loss based on leak size (approximation)
    # Using orifice flow equation: Q ∝ d²
    cfm_loss = (leak_size_mm ** 2) * 0.63  # Empirical constant
    
    # Energy to compress air: ~0.25 kW per CFM at 125 PSI
    kw_wasted = cfm_loss * 0.25
    
    # Annual energy cost
    kwh_per_year = kw_wasted * hours_per_year
    annual_cost = kwh_per_year * COST_CONFIG["electricity_rate_per_kwh"]
    
    return round(annual_cost, 2)


def classify_severity(pressure_drop: float, flow_deviation: float) -> str:
    """
    Classify leak severity based on pressure drop and flow deviation.
    
    Args:
        pressure_drop: Pressure drop in PSI
        flow_deviation: Flow deviation in CFM
    
    Returns:
        Severity level: 'CRITICAL', 'HIGH', 'MEDIUM', or 'LOW'
    """
    if pressure_drop > 20 or flow_deviation > 200:
        return "CRITICAL"
    elif pressure_drop > 10 or flow_deviation > 100:
        return "HIGH"
    elif pressure_drop > 5 or flow_deviation > 50:
        return "MEDIUM"
    else:
        return "LOW"


def generate_sensor_id(zone: str, sensor_type: str, index: int) -> str:
    """
    Generate standardized sensor ID.
    
    Args:
        zone: Zone identifier (e.g., 'Zone_A')
        sensor_type: 'P' for pressure, 'A' for acoustic
        index: Sensor index within zone
    
    Returns:
        Sensor ID (e.g., 'P_A_001')
    """
    return f"{sensor_type}_{zone[-1]}_{index:03d}"


def add_noise(value: float, noise_level: float = 0.02) -> float:
    """
    Add Gaussian noise to a sensor reading.
    
    Args:
        value: Original sensor value
        noise_level: Standard deviation as fraction of value (default: 2%)
    
    Returns:
        Value with added noise
    """
    noise = np.random.normal(0, abs(value) * noise_level)
    return value + noise


def create_time_range(start_date: str, num_days: int, freq: str = '1S') -> pd.DatetimeIndex:
    """
    Create a datetime range for data generation.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        num_days: Number of days to generate
        freq: Frequency ('1S' for 1 second, '1T' for 1 minute)
    
    Returns:
        Pandas DatetimeIndex
    """
    start = pd.to_datetime(start_date)
    end = start + timedelta(days=num_days)
    return pd.date_range(start=start, end=end, freq=freq)


def calculate_pressure_gradient(sensor_readings: List[Dict]) -> List[Tuple[str, str, float]]:
    """
    Calculate pressure gradients between adjacent sensors.
    
    Args:
        sensor_readings: List of sensor readings with 'sensor_id' and 'pressure_psi'
    
    Returns:
        List of tuples: (sensor_1, sensor_2, pressure_drop)
    """
    gradients = []
    sorted_readings = sorted(sensor_readings, key=lambda x: x['sensor_id'])
    
    for i in range(len(sorted_readings) - 1):
        sensor_1 = sorted_readings[i]['sensor_id']
        sensor_2 = sorted_readings[i + 1]['sensor_id']
        pressure_1 = sorted_readings[i]['pressure_psi']
        pressure_2 = sorted_readings[i + 1]['pressure_psi']
        
        pressure_drop = abs(pressure_1 - pressure_2)
        gradients.append((sensor_1, sensor_2, pressure_drop))
    
    return gradients


def format_alert_message(zone: str, severity: str, estimated_cost: float, sensor_ids: List[str]) -> str:
    """
    Format an alert message for the dashboard.
    
    Args:
        zone: Zone identifier
        severity: Severity level
        estimated_cost: Estimated annual cost
        sensor_ids: List of affected sensor IDs
    
    Returns:
        Formatted alert message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensors_str = ", ".join(sensor_ids[:3])  # Show first 3 sensors
    
    message = f"""
    🚨 LEAK DETECTED - {severity}
    Zone: {zone}
    Time: {timestamp}
    Affected Sensors: {sensors_str}
    Estimated Annual Cost: ${estimated_cost:,.2f}
    """
    return message.strip()


def export_to_json(data: pd.DataFrame, filepath: str) -> None:
    """
    Export DataFrame to JSON file.
    
    Args:
        data: Pandas DataFrame
        filepath: Output file path
    """
    data.to_json(filepath, orient='records', date_format='iso', indent=2)
    print(f"✅ Data exported to {filepath}")


def load_from_json(filepath: str) -> pd.DataFrame:
    """
    Load DataFrame from JSON file.
    
    Args:
        filepath: Input file path
    
    Returns:
        Pandas DataFrame
    """
    return pd.read_json(filepath)


def get_zone_statistics(data: pd.DataFrame, zone: str) -> Dict:
    """
    Calculate statistics for a specific zone.
    
    Args:
        data: Sensor data DataFrame
        zone: Zone identifier
    
    Returns:
        Dictionary with zone statistics
    """
    zone_data = data[data['zone'] == zone]
    
    stats = {
        "zone": zone,
        "num_sensors": zone_data['sensor_id'].nunique(),
        "avg_pressure": zone_data['pressure_psi'].mean(),
        "std_pressure": zone_data['pressure_psi'].std(),
        "avg_flow": zone_data['flow_rate_cfm'].mean(),
        "std_flow": zone_data['flow_rate_cfm'].std(),
        "anomaly_rate": (zone_data['is_anomaly'].mean() if 'is_anomaly' in zone_data.columns else 0),
    }
    
    return stats
