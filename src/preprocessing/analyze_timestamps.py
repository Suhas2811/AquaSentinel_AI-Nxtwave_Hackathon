
from pathlib import Path
import pandas as pd

# ======================================
# 1. PROJECT PATHS
# ======================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Water_Consumption_Cleaned.csv"
)

df = pd.read_csv(DATA_PATH)

print("DATASET LOADED")
print("Rows:", len(df))


# ======================================
# 2. TIMESTAMP VALIDATION
# ======================================

print("\nTIMESTAMP VALIDATION")

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

print("Invalid timestamps:", df["timestamp"].isna().sum())

print("Earliest timestamp:", df["timestamp"].min())
print("Latest timestamp:", df["timestamp"].max())

print(
    "Unique timestamps:",
    df["timestamp"].nunique()
)


# ======================================
# 3. DATE AND TIME CONSISTENCY
# ======================================

print("\nDATE AND TIME CONSISTENCY")

df["date_parsed"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

checks = {
    "Date mismatch": (
        df["timestamp"].dt.date != df["date_parsed"].dt.date
    ).sum(),

    "Hour mismatch": (
        df["timestamp"].dt.hour != df["hour"]
    ).sum(),

    "Month mismatch": (
        df["timestamp"].dt.month != df["month"]
    ).sum(),

    "Year mismatch": (
        df["timestamp"].dt.year != df["year"]
    ).sum()
}

for name, count in checks.items():
    print(f"{name}: {count}")


# ======================================
# 4. TIME INTERVAL ANALYSIS
# ======================================

print("\nTIME INTERVAL ANALYSIS")

df = df.sort_values(
    ["sensor_id", "timestamp"]
)

df["time_difference"] = (
    df.groupby("sensor_id")["timestamp"]
    .diff()
)

print("\nTime interval distribution:")

print(
    df["time_difference"]
    .value_counts()
    .head(10)
)

print("\nInterval statistics in minutes:")

print(
    df["time_difference"]
    .dt.total_seconds()
    .div(60)
    .describe()
)


# ======================================
# 5. SENSOR DATA COVERAGE
# ======================================

print("\nSENSOR DATA COVERAGE")

sensor_coverage = (
    df.groupby("sensor_id")
    .agg(
        records=("timestamp", "count"),
        first_reading=("timestamp", "min"),
        last_reading=("timestamp", "max"),
        unique_timestamps=("timestamp", "nunique")
    )
)

print(sensor_coverage.describe())

print("\nSensors with the fewest records:")

print(
    sensor_coverage
    .sort_values("records")
    .head(10)
)


# ======================================
# 6. MISSING TIME INTERVALS
# ======================================

print("\nMISSING TIME INTERVAL ANALYSIS")

interval_minutes = (
    df["time_difference"]
    .dt.total_seconds()
    .div(60)
)

print(
    "Intervals greater than 10 minutes:",
    int((interval_minutes > 10).sum())
)

print(
    "Intervals greater than 60 minutes:",
    int((interval_minutes > 60).sum())
)

print(
    "Intervals greater than 24 hours:",
    int((interval_minutes > 1440).sum())
)


print("\nTIMESTAMP ANALYSIS COMPLETED")
