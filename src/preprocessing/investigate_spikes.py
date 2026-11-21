
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
# 2. FIND TOP 15 AGGREGATE SPIKES
# ======================================

aggregate = (
    df.groupby("timestamp")
    .agg(
        total_consumption=("value", "sum"),
        event_count=("value", "size"),
        active_sensors=("sensor_id", "nunique")
    )
    .sort_values("total_consumption", ascending=False)
)

top_timestamps = aggregate.head(15).index

print("\nTOP 15 AGGREGATE EVENTS")

print(aggregate.head(15))


# ======================================
# 3. INSPECT INDIVIDUAL RECORDS
# ======================================

print("\nINDIVIDUAL RECORD DETAILS")

for timestamp in top_timestamps[:10]:

    records = df[df["timestamp"] == timestamp]

    print("\n" + "=" * 65)
    print("TIMESTAMP:", timestamp)
    print("TOTAL CONSUMPTION:", records["value"].sum())
    print("RECORD COUNT:", len(records))
    print("ACTIVE SENSORS:", records["sensor_id"].nunique())

    print("\nConsumption by water type:")

    print(
        records.groupby("type")["value"]
        .agg(["count", "sum", "mean"])
    )

    print("\nLargest individual readings:")

    print(
        records.nlargest(10, "value")[
            [
                "sensor_id",
                "room_type",
                "type",
                "attached_to",
                "value",
                "aggregated_value"
            ]
        ].to_string(index=False)
    )


# ======================================
# 4. SAVE SPIKE SUMMARY
# ======================================

OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

aggregate.head(15).to_csv(
    OUTPUT_DIR / "top_consumption_events.csv"
)

print("\nSPIKE INVESTIGATION COMPLETED")
