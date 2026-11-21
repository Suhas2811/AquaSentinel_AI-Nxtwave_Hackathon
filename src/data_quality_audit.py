
from pathlib import Path
import pandas as pd
import numpy as np

DATA_PATH = Path(
    "data/raw/HSB_Living_Lab_Water_Consumption_Anonymized.csv"
)

print("=" * 70)
print("AQUASENTINEL AI - DATA QUALITY AUDIT")
print("=" * 70)

# Load original data
df = pd.read_csv(DATA_PATH, sep=";")

# --------------------------------------------------
# 1. TIMESTAMP VALIDATION
# --------------------------------------------------

print("\n1. TIMESTAMP VALIDATION")

df["timestamp_parsed"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

print("Invalid timestamps:",
      df["timestamp_parsed"].isna().sum())

print("Start:", df["timestamp_parsed"].min())
print("End:", df["timestamp_parsed"].max())

print("Date mismatch:",
      (df["timestamp_parsed"].dt.strftime("%Y-%m-%d")
       != df["date"]).sum())

print("Hour mismatch:",
      (df["timestamp_parsed"].dt.hour
       != df["hour"]).sum())

# --------------------------------------------------
# 2. MISSING VALUE ANALYSIS
# --------------------------------------------------

print("\n2. MISSING VALUE ANALYSIS")

missing = pd.DataFrame({
    "Missing_Count": df.isnull().sum(),
    "Missing_Percentage": (
        df.isnull().mean() * 100
    ).round(2)
})

print(missing[missing["Missing_Count"] > 0])

# --------------------------------------------------
# 3. DUPLICATE ANALYSIS
# --------------------------------------------------

print("\n3. DUPLICATE ANALYSIS")

print("Exact duplicate rows:", df.duplicated().sum())

duplicates = df[df.duplicated(keep=False)]

print("\nSample duplicate records:")
print(duplicates.head(10).to_string(index=False))

# --------------------------------------------------
# 4. CATEGORICAL DISTRIBUTIONS
# --------------------------------------------------

print("\n4. CATEGORICAL DISTRIBUTIONS")

categorical_columns = [
    "type",
    "attached_to",
    "room_type",
    "cluster_name"
]

for col in categorical_columns:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False))

# --------------------------------------------------
# 5. NUMERICAL DISTRIBUTIONS
# --------------------------------------------------

print("\n5. NUMERICAL DISTRIBUTIONS")

for col in ["value", "aggregated_value"]:
    print(f"\n{col}:")
    print(df[col].describe(
        percentiles=[0.90, 0.95, 0.99, 0.999]
    ))

    print("Zero values:", (df[col] == 0).sum())
    print("Negative values:", (df[col] < 0).sum())

# --------------------------------------------------
# 6. UNIQUE ENTITY COUNTS
# --------------------------------------------------

print("\n6. UNIQUE ENTITY COUNTS")

for col in [
    "sensor_id",
    "apartment",
    "cluster_name",
    "room_number"
]:
    print(
        col,
        ":", df[col].nunique(dropna=True)
    )

# --------------------------------------------------
# 7. TIME COVERAGE
# --------------------------------------------------

print("\n7. TIME COVERAGE")

print("Unique dates:", df["date"].nunique())

print("Unique years:")
print(df["year"].value_counts().sort_index())

print("\nRecords by water type:")
print(df["type"].value_counts())

# --------------------------------------------------
# 8. BASIC DATA VALIDATION
# --------------------------------------------------

print("\n8. DATA VALIDATION")

print("Invalid hour values:",
      (~df["hour"].between(0, 23)).sum())

print("Invalid month values:",
      (~df["month"].between(1, 12)).sum())

print("Invalid day_of_week values:",
      (~df["day_of_week"].between(0, 6)).sum())

print("\n" + "=" * 70)
print("DATA QUALITY AUDIT COMPLETED")
print("=" * 70)
