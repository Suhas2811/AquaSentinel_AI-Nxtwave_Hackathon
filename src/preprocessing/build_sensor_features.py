
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/processed/HSB_Sensor_Daily_Features.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.normalize()

# Aggregate by sensor and day
daily = df.groupby(
    ["sensor_id", "date"]
).agg(
    daily_consumption=("value", "sum"),
    event_count=("value", "size"),
    mean_event_value=("value", "mean"),
    maximum_event_value=("value", "max"),
    active_timestamps=("timestamp", "nunique")
).reset_index()

daily = daily.sort_values(["sensor_id", "date"])

# Previous observed day for each sensor
daily["previous_consumption"] = (
    daily.groupby("sensor_id")["daily_consumption"].shift(1)
)

daily["previous_event_count"] = (
    daily.groupby("sensor_id")["event_count"].shift(1)
)

# Changes between consecutive observed records
daily["consumption_change"] = (
    daily["daily_consumption"] - daily["previous_consumption"]
)

daily["event_count_change"] = (
    daily["event_count"] - daily["previous_event_count"]
)

# Rolling statistics using past observations only
daily["rolling_mean_consumption"] = (
    daily.groupby("sensor_id")["daily_consumption"]
    .transform(lambda s: s.shift(1).rolling(7, min_periods=3).mean())
)

daily["rolling_mean_events"] = (
    daily.groupby("sensor_id")["event_count"]
    .transform(lambda s: s.shift(1).rolling(7, min_periods=3).mean())
)

# Save
daily.to_csv(OUTPUT_FILE, index=False)

print("SENSOR DAILY FEATURES CREATED")
print("------------------------------")
print("Total sensor-day records:", len(daily))
print("Unique sensors:", daily["sensor_id"].nunique())
print("Features:", daily.columns.tolist())

print("\nMissing values:")
print(daily.isnull().sum())

print("\nPriority sensor examples:")
print(
    daily[daily["sensor_id"].isin(["S0208", "S0101", "S0212"])]
    .groupby("sensor_id")
    .size()
)

print("\nSaved to:", OUTPUT_FILE)
