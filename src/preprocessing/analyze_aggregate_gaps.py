
from pathlib import Path
import pandas as pd

# ======================================
# 1. LOAD AGGREGATE DATASET
# ======================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Aggregate_10min.csv"
)

df = pd.read_csv(DATA_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

print("AGGREGATE DATA LOADED:", len(df))


# ======================================
# 2. MISSING INTERVAL SUMMARY
# ======================================

print("\nMISSING INTERVAL SUMMARY")

missing = df["observed"] == 0

print("Observed intervals:", int((~missing).sum()))
print("Unobserved intervals:", int(missing.sum()))


# ======================================
# 3. CONSECUTIVE MISSING INTERVALS
# ======================================

print("\nCONSECUTIVE MISSING INTERVAL ANALYSIS")

# Identify continuous missing/observed sections
group_id = missing.ne(missing.shift()).cumsum()

runs = (
    df.groupby(group_id)
    .agg(
        status=("observed", "first"),
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        intervals=("timestamp", "size")
    )
)

missing_runs = runs[runs["status"] == 0].copy()

missing_runs["duration_minutes"] = (
    missing_runs["intervals"] * 10
)

print("Total missing periods:", len(missing_runs))

print("\nMissing period duration distribution:")

print(
    missing_runs["duration_minutes"]
    .describe()
)

print("\nLongest missing periods:")

print(
    missing_runs
    .sort_values("duration_minutes", ascending=False)
    .head(15).to_string(index=False)
)


# ======================================
# 4. DAILY COVERAGE
# ======================================

print("\nDAILY COVERAGE ANALYSIS")

df["date"] = df["timestamp"].dt.date

daily = (
    df.groupby("date")
    .agg(
        total_intervals=("observed", "size"),
        observed_intervals=("observed", "sum"),
        consumption=(
        "total_consumption",
        lambda x: x.sum(min_count=1)
    )
    )
)

daily["coverage_pct"] = (
    daily["observed_intervals"]
    / daily["total_intervals"] * 100
)

print("\nDaily coverage statistics:")

print(daily["coverage_pct"].describe())

print("\nDays with lowest coverage:")

print(
    daily.sort_values("coverage_pct")
    .head(15)
)

print("\nDays with highest coverage:")

print(
    daily.sort_values("coverage_pct", ascending=False)
    .head(15)
)


# ======================================
# 5. HIGH CONSUMPTION INVESTIGATION
# ======================================

print("\nHIGH CONSUMPTION INTERVALS")

observed_df = df[df["observed"] == 1].copy()

print("\nHighest consumption timestamps:")

print(
    observed_df
    .nlargest(15, "total_consumption")[
        [
            "timestamp",
            "total_consumption",
            "event_count",
            "active_sensors"
        ]
    ].to_string(index=False)
)


# ======================================
# 6. SAVE DIAGNOSTICS
# ======================================

OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

missing_runs.to_csv(
    OUTPUT_DIR / "missing_interval_runs.csv",
    index=False
)

daily.to_csv(
    OUTPUT_DIR / "aggregate_daily_coverage.csv"
)

print("\nDiagnostic files saved.")
print("\nAGGREGATE GAP ANALYSIS COMPLETED")
