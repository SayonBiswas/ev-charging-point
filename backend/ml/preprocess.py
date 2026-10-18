# backend/ml/preprocess.py
# Data preprocessing for ML model training

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_STATIONS_PATH = os.path.join(BASE_DIR, "data", "bhubaneswar_stations.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_data.csv")

def preprocess_stations():
    """
    Load and preprocess station data
    Removes rows with missing coordinates, non-Bhubaneswar locations, and non-operational stations
    """
    # Load raw station data
    df = pd.read_csv(RAW_STATIONS_PATH)
    
    # Remove rows with missing latitude or longitude
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Keep only operational stations
    if 'is_operational' in df.columns:
        df = df[df['is_operational'] == True]
    
    # Keep only Bhubaneswar stations (simple coordinate check)
    # Bhubaneswar approximate bounds: 20.2 to 20.4 N, 85.7 to 85.9 E
    df = df[
        (df['latitude'] >= 20.2) & (df['latitude'] <= 20.4) &
        (df['longitude'] >= 85.7) & (df['longitude'] <= 85.9)
    ]
    
    # Save cleaned data
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"Preprocessed {len(df)} stations")
    print(f"Saved to: {CLEANED_DATA_PATH}")
    
    return df

def generate_battery_training_data(output_path: str, num_samples: int = 1000):
    """
    Generate synthetic battery training data
    Creates a CSV file with simulated charging session data
    """
    np.random.seed(42)
    
    data = []
    
    for _ in range(num_samples):
        battery_pct = np.random.uniform(5, 95)
        distance_remaining_km = np.random.uniform(5, 200)
        speed_kmh = np.random.uniform(30, 100)
        temp_celsius = np.random.uniform(15, 45)
        ac_on = np.random.choice([0, 1])
        
        # Label: needs_charge = 1 when battery_pct / distance_remaining_km < 0.45
        ratio = battery_pct / distance_remaining_km
        needs_charge = 1 if ratio < 0.45 else 0
        
        data.append({
            'battery_pct': battery_pct,
            'distance_remaining_km': distance_remaining_km,
            'speed_kmh': speed_kmh,
            'temp_celsius': temp_celsius,
            'ac_on': ac_on,
            'needs_charge': needs_charge
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} battery training samples: {output_path}")

def generate_demand_training_data(output_path: str, num_samples: int = 1000):
    """
    Generate synthetic demand training data
    Creates a CSV file with simulated demand patterns
    """
    np.random.seed(42)
    
    data = []
    
    for _ in range(num_samples):
        hour_of_day = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        total_connectors = np.random.choice([2, 4, 6, 8])
        charger_rating_kw = np.random.choice([7.4, 22, 50])
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Simulate wait time based on factors
        base_wait = 5
        if 8 <= hour_of_day <= 10 or 17 <= hour_of_day <= 19:
            base_wait += 15
        if is_weekend:
            base_wait -= 5
        if charger_rating_kw > 30:
            base_wait += 5
        
        wait_minutes = max(0, base_wait + np.random.normal(0, 3))
        
        data.append({
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'total_connectors': total_connectors,
            'charger_rating_kw': charger_rating_kw,
            'is_weekend': is_weekend,
            'wait_minutes': wait_minutes
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} demand training samples: {output_path}")

if __name__ == "__main__":
    # Preprocess station data
    preprocess_stations()
    
    # Generate training data
    battery_data_path = os.path.join(BASE_DIR, "data", "raw_charging_sessions.csv")
    demand_data_path = os.path.join(BASE_DIR, "data", "demand_data.csv")
    
    generate_battery_training_data(battery_data_path)
    generate_demand_training_data(demand_data_path)
