
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# Calculate daily totals
daily_totals = df.groupby("date")["value"].sum()

q1 = daily_totals.quantile(0.25)
q3 = daily_totals.quantile(0.75)
threshold = q3 + 1.5 * (q3 - q1)

high_dates = daily_totals[daily_totals > threshold].index

# Keep records from high-consumption days
high_records = df[df["date"].isin(high_dates)].copy()

# Calculate consumption by sensor and day
sensor_daily = high_records.groupby(
    ["date", "sensor_id"]
).agg(
    sensor_consumption=("value", "sum"),
    event_count=("value", "size"),
    maximum_event=("value", "max")
).reset_index()

# Calculate daily total for each sensor's share
sensor_daily["daily_total"] = sensor_daily["date"].map(
    daily_totals
)

sensor_daily["share_pct"] = (
    sensor_daily["sensor_consumption"]
    / sensor_daily["daily_total"] * 100
)

# Get top 3 sensors for each high-consumption day
top_sensors = (
    sensor_daily.sort_values(
        ["date", "sensor_consumption"],
        ascending=[True, False]
    )
    .groupby("date")
    .head(3)
    .sort_values(
        ["date", "sensor_consumption"],
        ascending=[True, False]
    )
)

OUTPUT_FILE = "data/metadata/top_sensors_high_days.csv"
top_sensors.to_csv(OUTPUT_FILE, index=False)

print("TOP SENSORS ON HIGH-CONSUMPTION DAYS")
print("------------------------------------")

for date, group in top_sensors.groupby("date"):
    print(f"\nDate: {date}")
    print(
        group[
            ["sensor_id", "sensor_consumption",
             "event_count", "maximum_event", "share_pct"]
        ].to_string(index=False)
    )

print("\nSaved to:", OUTPUT_FILE)
