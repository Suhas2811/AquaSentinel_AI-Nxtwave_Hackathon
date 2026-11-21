
import pandas as pd

coverage_file = "data/metadata/sensor_coverage_classified.csv"
calendar_file = "data/processed/HSB_Sensor_Daily_Complete.csv"
output_file = "data/metadata/high_coverage_continuity.csv"

# Load data
coverage = pd.read_csv(coverage_file)
calendar = pd.read_csv(calendar_file)

# Select high-coverage sensors
high_sensors = coverage.loc[
    coverage["coverage_category"] == "High", "sensor_id"
].tolist()

df = calendar[calendar["sensor_id"].isin(high_sensors)].copy()
df["date"] = pd.to_datetime(df["date"])

results = []

for sensor_id, group in df.groupby("sensor_id"):
    group = group.sort_values("date")

    observed = group.loc[group["observed"] == 1, "date"]

    # Days between consecutive observed dates
    gaps = observed.diff().dt.days.dropna()

    # Longest consecutive run of observed days
    observed_flags = group["observed"].astype(int)
    run_ids = observed_flags.ne(observed_flags.shift()).cumsum()
    observed_runs = (
        group.assign(run_id=run_ids)
        .loc[lambda x: x["observed"] == 1]
        .groupby("run_id")
        .size()
    )

    results.append({
        "sensor_id": sensor_id,
        "observed_days": len(observed),
        "coverage_pct": round(len(observed) / len(group) * 100, 2),
        "mean_gap_days": round(gaps.mean(), 2) if len(gaps) else 0,
        "median_gap_days": round(gaps.median(), 2) if len(gaps) else 0,
        "max_gap_days": int(gaps.max()) if len(gaps) else 0,
        "longest_consecutive_streak": int(observed_runs.max())
            if len(observed_runs) else 0
    })

result = pd.DataFrame(results)
result = result.sort_values(
    "longest_consecutive_streak", ascending=False
)

print("HIGH-COVERAGE SENSOR TEMPORAL CONTINUITY")
print("----------------------------------------")
print(result.to_string(index=False))

result.to_csv(output_file, index=False)
print(f"\nSaved to: {output_file}")
