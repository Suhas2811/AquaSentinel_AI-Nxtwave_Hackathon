
from pathlib import Path

import joblib
import pandas as pd


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Saved model location
MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "hybrid_ridge_models.pkl"
)

def load_forecasting_models():
    """
    Load the seven trained Hybrid Ridge models.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Forecasting model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_sensor_consumption(data, sensor_id, models=None):
    """
    Predict recorded consumption for a sensor.

    Parameters:
        data: DataFrame containing forecasting features.
        sensor_id: Sensor identifier, e.g. S0102.
        models: Previously loaded forecasting models.

    Returns:
        DataFrame containing actual and predicted values.
    """

    if models is None:
        models = load_forecasting_models()

    if sensor_id not in models:
        raise ValueError(
            f"No trained forecasting model for {sensor_id}"
        )

    model_info = models[sensor_id]

    model = model_info["model"]
    start_date = model_info["start_date"]
    features = model_info["features"]

    required_columns = [
        "sensor_id",
        "date",
        "daily_consumption",
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_mean_7",
        "rolling_mean_14",
        "day_of_week",
        "month",
        "is_weekend"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    result = data[
        data["sensor_id"] == sensor_id
    ].copy()

    if result.empty:
        raise ValueError(
            f"No records found for {sensor_id}"
        )

    result["date"] = pd.to_datetime(result["date"])

    result["day_index"] = (
        result["date"] - start_date
    ).dt.days

    if result[features].isna().any().any():
        raise ValueError(
            "Input contains missing forecasting features."
        )

    result["predicted_consumption"] = model.predict(
        result[features]
    )

    return result
