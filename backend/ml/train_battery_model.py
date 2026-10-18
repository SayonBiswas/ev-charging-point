# backend/ml/train_battery_model.py
# Train RandomForest model for battery sufficiency prediction

import sys
import os
# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.preprocess import generate_battery_training_data
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTERY_DATA_PATH = os.path.join(BASE_DIR, "data", "raw_charging_sessions.csv")
BATTERY_MODEL_PATH = os.path.join(BASE_DIR, "ml", "battery_model.pkl")

def train_battery_model(data_path: str, model_output_path: str):
    """
    Train RandomForest model to predict if charging is needed
    Args:
        data_path: Path to training data CSV
        model_output_path: Path to save trained model
    """
    print("Loading battery training data...")
    
    # Generate data if not exists
    if not os.path.exists(data_path):
        print("Generating synthetic training data...")
        generate_battery_training_data(data_path)
    
    df = pd.read_csv(data_path)
    
    # Separate features and target
    feature_columns = ['battery_pct', 'distance_remaining_km', 'speed_kmh', 'temp_celsius', 'ac_on']
    X = df[feature_columns].values
    y = df['needs_charge'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train RandomForest model
    print("Training RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, model_output_path)
    print(f"\nModel saved to: {model_output_path}")
    
    return accuracy

if __name__ == "__main__":
    train_battery_model(BATTERY_DATA_PATH, BATTERY_MODEL_PATH)
