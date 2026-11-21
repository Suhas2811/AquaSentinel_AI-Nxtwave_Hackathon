
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/metadata/high_consumption_day_details.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# Identify high-consumption days using the IQR threshold
daily = df.groupby("date").agg(
    total_consumption=("value", "sum"),
    event_count=("value", "size"),
    active_sensors=("sensor_id", "nunique")
)

q1 = daily["total_consumption"].quantile(0.25)
q3 = daily["total_consumption"].quantile(0.75)
upper_limit = q3 + 1.5 * (q3 - q1)

high_dates = daily[
    daily["total_consumption"] > upper_limit
].index

# Examine records belonging to high-consumption days
high_records = df[df["date"].isin(high_dates)].copy()

# Calculate each sensor's contribution on each high day
sensor_daily = high_records.groupby(
    ["date", "sensor_id"]
).agg(
    sensor_consumption=("value", "sum"),
    event_count=("value", "size")
).reset_index()

# Calculate the largest sensor contribution per day
sensor_summary = sensor_daily.groupby("date").agg(
    highest_sensor_consumption=("sensor_consumption", "max"),
    sensors_contributing=("sensor_id", "nunique")
)

sensor_summary["top_sensor_share_pct"] = (
    sensor_summary["highest_sensor_consumption"]
    / daily.loc[sensor_summary.index, "total_consumption"]
    * 100
)

# Combine daily statistics
result = daily.join(sensor_summary)
result = result.loc[high_dates].sort_values(
    "total_consumption", ascending=False
)

result.to_csv(OUTPUT_FILE)

print("HIGH-CONSUMPTION DAY INVESTIGATION")
print("---------------------------------")
print("IQR threshold:", round(upper_limit, 4))
print("High-consumption days:", len(result))

print("\nDetailed results:")
print(result.round(4).to_string())

print("\nSaved to:", OUTPUT_FILE)
