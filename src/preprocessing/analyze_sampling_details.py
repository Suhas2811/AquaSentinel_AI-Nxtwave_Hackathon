
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
# 2. REPEATED SENSOR-TIMESTAMP GROUPS
# ======================================

print("\nREPEATED SENSOR-TIMESTAMP GROUPS")

group_sizes = (
    df.groupby(["sensor_id", "timestamp"])
    .size()
)

repeated_groups = group_sizes[group_sizes > 1]

print("Repeated groups:", len(repeated_groups))
print("Rows in repeated groups:", int(repeated_groups.sum()))
print("Extra rows beyond unique combinations:", int((group_sizes - 1).clip(lower=0).sum()))

print("\nGroup size distribution:")
print(repeated_groups.value_counts().sort_index())


# ======================================
# 3. CHECK REPEATED GROUP DETAILS
# ======================================

print("\nREPEATED GROUP DETAILS")

repeated_keys = repeated_groups.index

repeated_records = (
    df.set_index(["sensor_id", "timestamp"])
    .loc[repeated_keys]
    .reset_index()
)

print(
    repeated_records[
        [
            "sensor_id",
            "timestamp",
            "type",
            "attached_to",
            "value",
            "aggregated_value"
        ]
    ].head(30).to_string(index=False)
)


# ======================================
# 4. CHECK 10-MINUTE ALIGNMENT
# ======================================

print("\n10-MINUTE TIMESTAMP ALIGNMENT")

minutes = df["timestamp"].dt.minute
seconds = df["timestamp"].dt.second

aligned = (
    (minutes % 10 == 0)
    & (seconds == 0)
)

print("Aligned records:", int(aligned.sum()))
print("Non-aligned records:", int((~aligned).sum()))

print("\nNon-aligned timestamp examples:")

print(
    df.loc[~aligned, "timestamp"]
    .drop_duplicates()
    .head(20).to_list()
)


# ======================================
# 5. DAILY COVERAGE ANALYSIS
# ======================================

print("\nDAILY COVERAGE ANALYSIS")

daily = (
    df.groupby(df["timestamp"].dt.date)
    .agg(
        records=("value", "size"),
        sensors=("sensor_id", "nunique"),
        consumption=("value", "sum")
    )
)

print("\nDays with the fewest records:")
print(daily.sort_values("records").head(15))

print("\nDaily coverage statistics:")
print(daily.describe())


# ======================================
# 6. SAVE DIAGNOSTIC RESULTS
# ======================================

OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

daily.to_csv(OUTPUT_DIR / "daily_coverage_analysis.csv")

print("\nSaved daily coverage analysis.")
print("\nDETAILED SAMPLING ANALYSIS COMPLETED")
