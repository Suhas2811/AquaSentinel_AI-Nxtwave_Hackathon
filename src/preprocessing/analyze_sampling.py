
from pathlib import Path
import pandas as pd

# ======================================
# 1. LOAD DATA
# ======================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Water_Consumption_Cleaned.csv"
)

df = pd.read_csv(DATA_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

print("DATA LOADED:", len(df))


# ======================================
# 2. SENSOR-TIMESTAMP DUPLICATES
# ======================================

print("\nSENSOR-TIMESTAMP ANALYSIS")

duplicate_sensor_time = df.duplicated(
    subset=["sensor_id", "timestamp"],
    keep=False
)

print(
    "Rows sharing sensor and timestamp:",
    int(duplicate_sensor_time.sum())
)

print(
    "Distinct sensor-timestamp combinations:",
    df[["sensor_id", "timestamp"]]
    .drop_duplicates()
    .shape[0]
)

print("\nExamples:")

print(
    df.loc[
        duplicate_sensor_time,
        ["sensor_id", "timestamp", "type", "value"]
    ].head(15).to_string(index=False)
)


# ======================================
# 3. DAILY RECORD DISTRIBUTION
# ======================================

print("\nDAILY RECORD DISTRIBUTION")

df["date"] = pd.to_datetime(df["date"])

daily_records = (
    df.groupby("date")
    .size()
)

print(daily_records.describe())

print(
    "\nDays with zero records between dataset dates:",
    len(
        pd.date_range(
            daily_records.index.min(),
            daily_records.index.max(),
            freq="D"
        ).difference(daily_records.index)
    )
)


# ======================================
# 4. SENSOR RECORD DISTRIBUTION
# ======================================

print("\nSENSOR RECORD DISTRIBUTION")

sensor_stats = (
    df.groupby("sensor_id")
    .agg(
        total_records=("value", "size"),
        active_days=("date", "nunique"),
        total_consumption=("value", "sum")
    )
)

print(sensor_stats.describe())

print("\nSensors with lowest record counts:")

print(
    sensor_stats
    .sort_values("total_records")
    .head(15)
)


# ======================================
# 5. AGGREGATE TIME SERIES
# ======================================

print("\nAGGREGATED TIME SERIES")

# Sum recorded consumption across sensors
# for each timestamp.

time_series = (
    df.groupby("timestamp")["value"]
    .sum()
    .sort_index()
)

print("Unique time points:", len(time_series))

print("\nTime-series statistics:")

print(time_series.describe())

print("\nIntervals between aggregate timestamps:")

print(
    time_series.index.to_series()
    .diff()
    .value_counts()
    .head(10)
)


print("\nSAMPLING ANALYSIS COMPLETED")
