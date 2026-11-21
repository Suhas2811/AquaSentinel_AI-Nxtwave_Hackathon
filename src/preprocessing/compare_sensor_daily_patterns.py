
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/metadata/priority_sensor_daily_patterns.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.normalize()

priority_sensors = ["S0208", "S0101", "S0212"]

data = df[df["sensor_id"].isin(priority_sensors)].copy()

# Daily behaviour of each sensor
daily = data.groupby(
    ["sensor_id", "date"]
).agg(
    daily_consumption=("value", "sum"),
    event_count=("value", "size"),
    mean_event_value=("value", "mean"),
    maximum_event=("value", "max"),
    active_timestamps=("timestamp", "nunique")
).reset_index()

# Add consecutive-day comparison
daily = daily.sort_values(["sensor_id", "date"])

daily["previous_day_consumption"] = (
    daily.groupby("sensor_id")["daily_consumption"].shift(1)
)

daily["consumption_change"] = (
    daily["daily_consumption"]
    - daily["previous_day_consumption"]
)

# Print sensor-level statistics
print("SENSOR DAILY PATTERN COMPARISON")
print("--------------------------------")

for sensor in priority_sensors:

    sensor_df = daily[daily["sensor_id"] == sensor]

    print(f"\nSensor: {sensor}")

    print("Number of observed days:", len(sensor_df))
    print("Mean daily consumption:",
          round(sensor_df["daily_consumption"].mean(), 5))
    print("Median daily consumption:",
          round(sensor_df["daily_consumption"].median(), 5))
    print("Maximum daily consumption:",
          round(sensor_df["daily_consumption"].max(), 5))
    print("Mean events per observed day:",
          round(sensor_df["event_count"].mean(), 2))

    print("\nTop 10 days:")
    print(
        sensor_df.sort_values(
            "daily_consumption", ascending=False
        ).head(10).to_string(index=False)
    )

# Save full daily patterns
daily.to_csv(OUTPUT_FILE, index=False)

print("\nSaved to:", OUTPUT_FILE)
