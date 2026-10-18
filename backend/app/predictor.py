# backend/app/predictor.py
# ML prediction module for battery sufficiency and demand forecasting

import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import os

# Path to ML models (relative to this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTERY_MODEL_PATH = os.path.join(BASE_DIR, "ml", "battery_model.pkl")
DEMAND_MODEL_PATH = os.path.join(BASE_DIR, "ml", "demand_model.pkl")

# Ensure ml directory exists
os.makedirs(os.path.join(BASE_DIR, "ml"), exist_ok=True)

class MLPredictor:
    """Machine learning predictor for EV charging optimization"""
    
    def __init__(self):
        """Load pre-trained ML models"""
        try:
            self.battery_model = joblib.load(BATTERY_MODEL_PATH)
            self.demand_model = joblib.load(DEMAND_MODEL_PATH)
        except FileNotFoundError as e:
            print(f"Warning: ML models not found. {e}")
            print("Please run the training scripts in ml/ directory.")
            self.battery_model = None
            self.demand_model = None
    
    def predict_needs_charge(
        self,
        battery_pct: float,
        distance_remaining_km: float,
        speed_kmh: float,
        temp_celsius: float,
        ac_on: int
    ) -> int:
        """
        Predict whether charging is needed for the trip
        Returns: 1 (needs charge) or 0 (safe to continue)
        """
        if self.battery_model is None:
            # Fallback: simple rule-based prediction
            # From SRS: needs_charge = 1 when battery_pct / distance_remaining_km < 0.45
            if distance_remaining_km > 0:
                ratio = battery_pct / distance_remaining_km
                return 1 if ratio < 0.45 else 0
            return 0
        
        features = np.array([battery_pct, distance_remaining_km, speed_kmh, temp_celsius, ac_on]).reshape(1, -1)
        prediction = self.battery_model.predict(features)[0]
        return int(prediction)
    
    def predict_wait_time(
        self,
        hour_of_day: int,
        day_of_week: int,
        total_connectors: int,
        charger_rating_kw: float,
        is_weekend: int
    ) -> float:
        """
        Predict station wait time
        Returns: estimated wait time in minutes
        """
        if self.demand_model is None:
            # Fallback: simple estimation based on time of day
            base_wait = 5
            if 8 <= hour_of_day <= 10 or 17 <= hour_of_day <= 19:
                base_wait += 10
            if is_weekend:
                base_wait -= 3
            return float(base_wait)
        
        features = np.array([hour_of_day, day_of_week, total_connectors, charger_rating_kw, is_weekend]).reshape(1, -1)
        prediction = self.demand_model.predict(features)[0]
        return float(max(0, prediction))
    
    def estimate_charge_time_and_cost(
        self,
        battery_pct: float,
        charger_rating_kw: float
    ) -> Tuple[float, float]:
        """
        Estimate charge time and cost
        Returns: (charge_time_min, cost_inr)
        """
        # Fixed assumptions from SRS
        battery_capacity_kwh = 40.0
        tariff_per_kwh = 8.5
        
        # Energy needed (kWh)
        energy_needed = (100 - battery_pct) / 100 * battery_capacity_kwh
        
        # Charge time (min) = energy_needed / charger_kW * 60
        if charger_rating_kw > 0:
            charge_time_min = energy_needed / charger_rating_kw * 60
        else:
            charge_time_min = 0
        
        # Cost (₹) = energy_needed * tariff
        cost = energy_needed * tariff_per_kwh
        
        return round(charge_time_min, 1), round(cost, 2)

# Global predictor instance
predictor = MLPredictor()
