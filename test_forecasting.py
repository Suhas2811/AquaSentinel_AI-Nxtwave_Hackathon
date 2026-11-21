
import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.models.forecasting import (
    load_forecasting_models,
    predict_sensor_consumption
)

# Load test dataset
test = pd.read_csv("data/processed/forecast_test.csv")

# Load trained models
models = load_forecasting_models()

results = []

for sensor in sorted(models.keys()):

    predictions = predict_sensor_consumption(
        test,
        sensor,
        models
    )

    actual = predictions["daily_consumption"]
    predicted = predictions["predicted_consumption"]
    persistence = predictions["lag_1"]

    results.append({
        "sensor_id": sensor,
        "Hybrid_MAE": mean_absolute_error(actual, predicted),
        "Hybrid_RMSE": np.sqrt(
            mean_squared_error(actual, predicted)
        ),
        "Persistence_MAE": mean_absolute_error(
            actual, persistence
        )
    })

results_df = pd.DataFrame(results)

print("\nFINAL FORECASTING TEST — ALL SENSORS")
print(results_df.round(6).to_string(index=False))

print("\nOVERALL METRICS")

print(
    "MAE:",
    round(results_df["Hybrid_MAE"].mean(), 6)
)

print(
    "RMSE:",
    round(np.sqrt(
        np.mean(results_df["Hybrid_RMSE"] ** 2)
    ), 6)
)
