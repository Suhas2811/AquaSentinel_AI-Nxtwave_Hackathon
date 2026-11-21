
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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Aggregate_10min.csv"
)

# ======================================
# 2. LOAD DATA
# ======================================

df = pd.read_csv(DATA_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

print("DATA LOADED:", len(df))


# ======================================
# 3. AGGREGATE CONSUMPTION
# ======================================

aggregate = (
    df.groupby("timestamp")
    .agg(
        total_consumption=("value", "sum"),
        event_count=("value", "size"),
        active_sensors=("sensor_id", "nunique")
    )
    .sort_index()
)

print("\nAGGREGATION COMPLETED")
print("Observed timestamps:", len(aggregate))


# ======================================
# 4. CREATE COMPLETE 10-MINUTE GRID
# ======================================

full_index = pd.date_range(
    start=aggregate.index.min(),
    end=aggregate.index.max(),
    freq="10min"
)

aggregate = aggregate.reindex(full_index)

aggregate.index.name = "timestamp"

# Mark timestamps with actual observations
aggregate["observed"] = (
    aggregate["event_count"].notna()
).astype(int)

# Do not fill missing consumption with zero yet
aggregate = aggregate.reset_index()


# ======================================
# 5. AGGREGATE DATASET SUMMARY
# ======================================

print("\nAGGREGATE TIME SERIES SUMMARY")

print("Total 10-minute intervals:", len(aggregate))

print(
    "Observed intervals:",
    int(aggregate["observed"].sum())
)

print(
    "Unobserved intervals:",
    int((aggregate["observed"] == 0).sum())
)

print(
    "Missing consumption intervals:",
    int(aggregate["total_consumption"].isna().sum())
)

print("\nConsumption statistics (observed intervals):")

print(
    aggregate["total_consumption"].describe()
)


# ======================================
# 6. SAVE DATASET
# ======================================

aggregate.to_csv(OUTPUT_PATH, index=False)

print("\nAGGREGATE DATASET SAVED:")
print(OUTPUT_PATH)

print("\nAGGREGATE TIME SERIES CREATED SUCCESSFULLY")
