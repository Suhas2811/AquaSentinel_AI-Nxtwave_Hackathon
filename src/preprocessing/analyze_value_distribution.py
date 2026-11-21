
from pathlib import Path
import pandas as pd
import numpy as np

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

print("DATA LOADED:", len(df))


# ======================================
# 2. VALUE DISTRIBUTION
# ======================================

print("\nCONSUMPTION VALUE DISTRIBUTION")

print(df["value"].describe(
    percentiles=[0.90, 0.95, 0.99, 0.995, 0.999]
))


# ======================================
# 3. THRESHOLD ANALYSIS
# ======================================

print("\nTHRESHOLD ANALYSIS")

for threshold in [0.05, 0.10, 0.15, 0.20, 0.25, 0.29, 0.30]:

    count = int((df["value"] >= threshold).sum())

    print(
        f"Values >= {threshold:.2f}: "
        f"{count} ({count / len(df) * 100:.4f}%)"
    )


# ======================================
# 4. CHECK VALUES ABOVE 0.300
# ======================================

print("\nVALUES ABOVE 0.300")

above = df[df["value"] > 0.300]

print("Count:", len(above))

if not above.empty:
    print(
        above[
            [
                "timestamp",
                "sensor_id",
                "room_type",
                "type",
                "attached_to",
                "value"
            ]
        ].head(20).to_string(index=False)
    )


# ======================================
# 5. HIGH VALUES BY CATEGORY
# ======================================

print("\nHIGH VALUES BY WATER TYPE")

print(
    df.groupby("type")["value"]
    .agg(["count", "mean", "median", "max"])
)

print("\nHIGH VALUES BY FIXTURE")

print(
    df.groupby("attached_to")["value"]
    .agg(["count", "mean", "median", "max"])
)


# ======================================
# 6. SAVE RESULTS
# ======================================

OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df[df["value"] >= 0.25].to_csv(
    OUTPUT_DIR / "high_consumption_records.csv",
    index=False
)

print("\nVALUE DISTRIBUTION ANALYSIS COMPLETED")
