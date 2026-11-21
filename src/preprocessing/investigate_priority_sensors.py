
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/metadata/priority_sensor_analysis.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

priority_sensors = ["S0208", "S0101", "S0212"]

# Filter priority sensors
sensor_data = df[
    df["sensor_id"].isin(priority_sensors)
].copy()

# Daily consumption for each sensor
sensor_data["date"] = sensor_data["timestamp"].dt.date

daily = sensor_data.groupby(
    ["sensor_id", "date"]
).agg(
    daily_consumption=("value", "sum"),
    event_count=("value", "size"),
    maximum_event=("value", "max")
).reset_index()

# Sensor-level summary
summary = sensor_data.groupby("sensor_id").agg(
    total_records=("value", "size"),
    total_consumption=("value", "sum"),
    mean_value=("value", "mean"),
    median_value=("value", "median"),
    maximum_value=("value", "max"),
    unique_dates=("date", "nunique"),
    fixture=("attached_to", "first"),
    water_type=("type", "first"),
    apartment=("apartment", "first"),
    cluster=("cluster_name", "first")
)

print("PRIORITY SENSOR INVESTIGATION")
print("-----------------------------")

print("\nSensor summary:")
print(summary.round(5).to_string())

for sensor in priority_sensors:
    print(f"\nTop 10 consumption days for {sensor}:")

    sensor_daily = daily[
        daily["sensor_id"] == sensor
    ].sort_values(
        "daily_consumption", ascending=False
    )

    print(
        sensor_daily.head(10).to_string(index=False)
    )

# Save detailed daily results
daily.to_csv(OUTPUT_FILE, index=False)

print("\nSaved to:", OUTPUT_FILE)
