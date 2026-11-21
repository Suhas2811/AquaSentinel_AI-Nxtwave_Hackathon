
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/processed/HSB_Daily_Consumption.csv"

# Load cleaned dataset
df = pd.read_csv(INPUT_FILE)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Extract date
df["date"] = df["timestamp"].dt.date

# Separate cold and hot water consumption
df["cold_value"] = df["value"].where(
    df["type"] == "cold water consumption", 0
)

df["hot_value"] = df["value"].where(
    df["type"] == "hot water consumption", 0
)

# Aggregate observed records by day
daily = df.groupby("date").agg(
    total_consumption=("value", "sum"),
    cold_consumption=("cold_value", "sum"),
    hot_consumption=("hot_value", "sum"),
    event_count=("value", "size"),
    active_sensors=("sensor_id", "nunique"),
    observed_intervals=("timestamp", "nunique")
)

# Create a complete daily calendar
full_dates = pd.date_range(
    start=df["timestamp"].min().normalize(),
    end=df["timestamp"].max().normalize(),
    freq="D"
).date

daily = daily.reindex(full_dates)
daily.index.name = "date"

# Preserve missing days as NaN
daily["observed_intervals"] = daily["observed_intervals"].fillna(0)
daily["event_count"] = daily["event_count"].fillna(0)
daily["active_sensors"] = daily["active_sensors"].fillna(0)

# Calculate observation coverage
daily["observation_coverage_pct"] = (
    daily["observed_intervals"] / 144 * 100
)

# Mark days with at least one observed interval
daily["observed"] = (
    daily["observed_intervals"] > 0
).astype(int)

# Save daily dataset
daily.to_csv(OUTPUT_FILE)

print("DAILY DATASET CREATED")
print("---------------------")
print("Total calendar days:", len(daily))
print("Observed days:", daily["observed"].sum())
print("Missing days:", (daily["observed"] == 0).sum())

print("\nAverage observation coverage:",
      round(daily["observation_coverage_pct"].mean(), 2), "%")

print("\nDaily consumption summary:")
print(daily["total_consumption"].describe())

print("\nFirst 5 records:")
print(daily.head())

print("\nSaved to:", OUTPUT_FILE)
