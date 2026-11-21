
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "hybrid_ridge_models.pkl"
)

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Forecasting_Continuous.csv"
)

# Seven trained sensors
SENSORS = [
    "S0102",
    "S0103",
    "S0104",
    "S0105",
    "S0106",
    "S0107",
    "S0109"
]


def load_resources():
    """Load trained models and historical consumption data."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Historical dataset not found: {DATA_PATH}"
        )

    models = joblib.load(MODEL_PATH)

    history = pd.read_csv(DATA_PATH)
    history["date"] = pd.to_datetime(history["date"])

    return models, history


def forecast_future(horizon=7):
    """
    Generate recursive consumption forecasts
    for all seven trained sensors.

    Future lag and rolling features use previous
    predictions rather than actual future values.
    """

    if not isinstance(horizon, int) or isinstance(horizon, bool):
        raise ValueError("Horizon must be a positive integer.")

    if horizon < 1:
        raise ValueError("Horizon must be at least 1 day.")

    models, history = load_resources()

    forecast_results = []

    for sensor in SENSORS:

        if sensor not in models:
            raise ValueError(
                f"Trained model missing for {sensor}"
            )

        sensor_history = (
            history[history["sensor_id"] == sensor]
            .sort_values("date")
            .copy()
        )

        if len(sensor_history) < 14:
            raise ValueError(
                f"Insufficient history for {sensor}"
            )

        if sensor_history["date"].duplicated().any():
            raise ValueError(
                f"Duplicate dates found for {sensor}"
            )

        if sensor_history["daily_consumption"].isna().any():
            raise ValueError(
                f"Missing consumption values for {sensor}"
            )

        model_info = models[sensor]

        model = model_info["model"]
        model_start_date = pd.Timestamp(
            model_info["start_date"]
        )

        # Historical consumption values
        consumption = (
            sensor_history["daily_consumption"]
            .astype(float)
            .tolist()
        )

        last_date = sensor_history["date"].max()

        for day in range(1, horizon + 1):

            forecast_date = (
                last_date + pd.Timedelta(days=day)
            )

            # Historical and previously predicted values
            lag_1 = consumption[-1]
            lag_7 = consumption[-7]
            lag_14 = consumption[-14]

            rolling_mean_7 = np.mean(consumption[-7:])
            rolling_mean_14 = np.mean(consumption[-14:])

            # Calendar features
            day_of_week = forecast_date.day_of_week
            month = forecast_date.month
            is_weekend = int(day_of_week >= 5)

            # Trend feature
            day_index = (
                forecast_date - model_start_date
            ).days

            # Build model input in training feature order
            features = pd.DataFrame([{
                "lag_1": lag_1,
                "lag_7": lag_7,
                "lag_14": lag_14,
                "rolling_mean_7": rolling_mean_7,
                "rolling_mean_14": rolling_mean_14,
                "day_of_week": day_of_week,
                "month": month,
                "is_weekend": is_weekend,
                "day_index": day_index
            }])

            # Predict consumption
            raw_prediction = float(
                model.predict(features)[0]
            )

            # Consumption cannot be negative
            prediction = max(0.0, raw_prediction)

            forecast_results.append({
                "sensor_id": sensor,
                "date": forecast_date,
                "predicted_consumption": prediction
            })

            # Append prediction for recursive forecasting
            consumption.append(prediction)

    return pd.DataFrame(forecast_results)


if __name__ == "__main__":

    forecasts = forecast_future(horizon=7)

    print("\n7-DAY WATER CONSUMPTION FORECAST")
    print(forecasts.to_string(index=False))

    print("\nFORECAST SUMMARY")
    print(
        forecasts.groupby("sensor_id")[
            "predicted_consumption"
        ].mean().round(6)
    )

    # Save forecast results
    output_path = (
        PROJECT_ROOT
        / "evaluation"
        / "seven_day_forecast.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    forecasts.to_csv(output_path, index=False)

    print(f"\nForecast saved to: {output_path}")
    print(f"Total predictions: {len(forecasts)}")
