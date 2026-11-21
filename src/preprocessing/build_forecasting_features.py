
import pandas as pd

INPUT_FILE = "data/processed/HSB_Forecasting_Continuous.csv"
OUTPUT_FILE = "data/processed/HSB_Forecasting_Features.csv"

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])

# Sort each sensor's time series
df = df.sort_values(["sensor_id", "date"]).copy()

# Calendar features
df["day_of_week"] = df["date"].dt.dayofweek
df["day_of_month"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

# Lag and rolling features calculated separately per sensor
grouped = df.groupby("sensor_id")["daily_consumption"]

df["lag_1"] = grouped.shift(1)
df["lag_7"] = grouped.shift(7)
df["lag_14"] = grouped.shift(14)

df["rolling_mean_7"] = grouped.transform(
    lambda x: x.shift(1).rolling(7).mean()
)

df["rolling_mean_14"] = grouped.transform(
    lambda x: x.shift(1).rolling(14).mean()
)

# Remove rows without sufficient historical observations
features = df.dropna().copy()

features.to_csv(OUTPUT_FILE, index=False)

print("FORECASTING FEATURES CREATED")
print("----------------------------")
print("Original rows:", len(df))
print("Feature rows:", len(features))
print("Sensors:", features["sensor_id"].nunique())
print("Features:", features.columns.tolist())

print("\nMissing values:")
print(features.isna().sum())

print("\nRows per sensor:")
print(features.groupby("sensor_id").size())

print("\nSaved to:", OUTPUT_FILE)
