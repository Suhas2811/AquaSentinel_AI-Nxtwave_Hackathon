
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Water_Consumption_Cleaned.csv"
)

# Load cleaned dataset
df = pd.read_csv(DATA_PATH)

print("CLEANED DATA LOADED")
print("Rows:", len(df))

# ======================================
# 1. MISSING VALUE SUMMARY
# ======================================

print("\nMISSING VALUE SUMMARY")

for col in ["apartment", "cluster_name"]:

    missing = df[col].isna().sum()
    percentage = missing / len(df) * 100

    print(
        f"{col}: {missing} missing "
        f"({percentage:.2f}%)"
    )


# ======================================
# 2. MISSING VALUES BY SENSOR
# ======================================

print("\nMISSING VALUES BY SENSOR")

sensor_analysis = (
    df.groupby("sensor_id")
    .agg(
        total_records=("sensor_id", "size"),
        missing_apartment=("apartment", lambda x: x.isna().sum()),
        missing_cluster=("cluster_name", lambda x: x.isna().sum())
    )
)

sensor_analysis["apartment_missing_pct"] = (
    sensor_analysis["missing_apartment"]
    / sensor_analysis["total_records"] * 100
)

sensor_analysis["cluster_missing_pct"] = (
    sensor_analysis["missing_cluster"]
    / sensor_analysis["total_records"] * 100
)

print(
    sensor_analysis
    .sort_values("missing_apartment", ascending=False)
    .head(15)
)


# ======================================
# 3. MISSING VALUES BY ROOM TYPE
# ======================================

print("\nMISSING VALUES BY ROOM TYPE")

room_analysis = (
    df.groupby("room_type", dropna=False)
    .agg(
        total_records=("room_type", "size"),
        missing_apartment=("apartment", lambda x: x.isna().sum()),
        missing_cluster=("cluster_name", lambda x: x.isna().sum())
    )
)

print(room_analysis)


# ======================================
# 4. MISSING VALUE COMBINATIONS
# ======================================

print("\nMISSING VALUE COMBINATIONS")

apartment_missing = df["apartment"].isna()
cluster_missing = df["cluster_name"].isna()

print(
    "Both missing:",
    int((apartment_missing & cluster_missing).sum())
)

print(
    "Only apartment missing:",
    int((apartment_missing & ~cluster_missing).sum())
)

print(
    "Only cluster missing:",
    int((~apartment_missing & cluster_missing).sum())
)

print(
    "Neither missing:",
    int((~apartment_missing & ~cluster_missing).sum())
)


# ======================================
# 5. SENSOR-LEVEL CONSISTENCY
# ======================================

print("\nSENSOR-LEVEL CONSISTENCY")

sensor_consistency = (
    df.groupby("sensor_id")
    .agg(
        apartment_values=("apartment", "nunique"),
        cluster_values=("cluster_name", "nunique"),
        room_values=("room_number", "nunique")
    )
)

print(sensor_consistency.describe())


print("\nMISSING VALUE INVESTIGATION COMPLETED")


# ======================================
# 6. ROOM NUMBER MAPPING ANALYSIS
# ======================================

print("\nROOM NUMBER MAPPING ANALYSIS")

room_mapping = (
    df.groupby("room_number", dropna=False)
    .agg(
        total_records=("room_number", "size"),
        unique_apartments=("apartment", "nunique"),
        unique_clusters=("cluster_name", "nunique"),
        known_apartments=("apartment", "count"),
        known_clusters=("cluster_name", "count")
    )
)

print("\nRoom numbers with multiple apartment mappings:")

print(
    room_mapping[
        room_mapping["unique_apartments"] > 1
    ].head(20)
)

print("\nRoom numbers with multiple cluster mappings:")

print(
    room_mapping[
        room_mapping["unique_clusters"] > 1
    ].head(20)
)


# ======================================
# 7. SENSOR-LEVEL MISSINGNESS ANALYSIS
# ======================================

print("\nSENSOR-LEVEL MISSINGNESS DETAILS")

sensor_mapping = (
    df.groupby("sensor_id")
    .agg(
        total_records=("sensor_id", "size"),
        known_apartments=("apartment", "count"),
        known_clusters=("cluster_name", "count"),
        apartment=("apartment", "first"),
        cluster=("cluster_name", "first"),
        room_number=("room_number", "first"),
        room_type=("room_type", "first")
    )
)

sensor_mapping["apartment_missing_pct"] = (
    1 - sensor_mapping["known_apartments"]
    / sensor_mapping["total_records"]
) * 100

sensor_mapping["cluster_missing_pct"] = (
    1 - sensor_mapping["known_clusters"]
    / sensor_mapping["total_records"]
) * 100

print("\nSensors with partially missing apartment information:")

print(
    sensor_mapping[
        (sensor_mapping["known_apartments"] > 0)
        & (sensor_mapping["known_apartments"] < sensor_mapping["total_records"])
    ].head(20)
)

print("\nSensors with completely missing apartment information:")

print(
    sensor_mapping[
        sensor_mapping["known_apartments"] == 0
    ].head(20)
)

print("\nMETADATA MAPPING ANALYSIS COMPLETED")


# ======================================
# 8. CHECK RECOVERABLE METADATA
# ======================================

print("\nRECOVERABLE METADATA ANALYSIS")

# Build room-level mappings using known values
room_metadata = (
    df.groupby("room_number")
    .agg(
        known_apartments=("apartment", "nunique"),
        known_clusters=("cluster_name", "nunique"),
        apartment_value=("apartment", "first"),
        cluster_value=("cluster_name", "first")
    )
)

# Only accept mappings where exactly one known value exists
valid_apartment_rooms = room_metadata[
    room_metadata["known_apartments"] == 1
].index

valid_cluster_rooms = room_metadata[
    room_metadata["known_clusters"] == 1
].index

# Check missing records whose room has a unique known mapping
apartment_candidates = (
    df["apartment"].isna()
    & df["room_number"].isin(valid_apartment_rooms)
)

cluster_candidates = (
    df["cluster_name"].isna()
    & df["room_number"].isin(valid_cluster_rooms)
)

print(
    "Missing apartment records potentially recoverable:",
    int(apartment_candidates.sum())
)

print(
    "Missing cluster records potentially recoverable:",
    int(cluster_candidates.sum())
)

# Check how many distinct rooms have usable mappings
print(
    "Rooms with exactly one known apartment:",
    len(valid_apartment_rooms)
)

print(
    "Rooms with exactly one known cluster:",
    len(valid_cluster_rooms)
)

print("\nRECOVERABILITY CHECK COMPLETED")
