# backend/ml/train_demand_model.py
# Train XGBoost model for demand forecasting

import sys
import os
# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.preprocess import generate_demand_training_data
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMAND_DATA_PATH = os.path.join(BASE_DIR, "data", "demand_data.csv")
DEMAND_MODEL_PATH = os.path.join(BASE_DIR, "ml", "demand_model.pkl")

def train_demand_model(data_path: str, model_output_path: str):
    """
    Train XGBoost model to predict station wait time
    Args:
        data_path: Path to training data CSV
        model_output_path: Path to save trained model
    """
    print("Loading demand training data...")
    
    # Generate data if not exists
    if not os.path.exists(data_path):
        print("Generating synthetic training data...")
        generate_demand_training_data(data_path)
    
    df = pd.read_csv(data_path)
    
    # Separate features and target
    feature_columns = ['hour_of_day', 'day_of_week', 'total_connectors', 'charger_rating_kw', 'is_weekend']
    X = df[feature_columns].values
    y = df['wait_minutes'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train XGBoost model
    print("Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  Mean Absolute Error: {mae:.4f} minutes")
    print(f"  Mean Squared Error: {mse:.4f}")
    print(f"  R² Score: {r2:.4f}")
    
    # Save model
    joblib.dump(model, model_output_path)
    print(f"\nModel saved to: {model_output_path}")
    
    return mae

if __name__ == "__main__":
    train_demand_model(DEMAND_DATA_PATH, DEMAND_MODEL_PATH)
