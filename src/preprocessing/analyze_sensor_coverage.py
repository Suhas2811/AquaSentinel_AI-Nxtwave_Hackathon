
import pandas as pd

INPUT_FILE = "data/processed/HSB_Sensor_Daily_Complete.csv"
OUTPUT_FILE = "data/metadata/sensor_coverage_summary.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

summary = df.groupby("sensor_id").agg(
    total_calendar_days=("date", "size"),
    observed_days=("observed", "sum")
)

summary["missing_days"] = (
    summary["total_calendar_days"] - summary["observed_days"]
)

summary["coverage_pct"] = (
    summary["observed_days"]
    / summary["total_calendar_days"] * 100
)

summary = summary.sort_values("coverage_pct")

print("SENSOR COVERAGE ANALYSIS")
print("------------------------")

print("\nOverall sensor coverage:")
print(summary["coverage_pct"].describe().round(2))

print("\nLowest 15 sensor coverage:")
print(summary.head(15).round(2).to_string())

print("\nHighest 15 sensor coverage:")
print(summary.tail(15).round(2).to_string())

print("\nSensors with less than 25% coverage:",
      (summary["coverage_pct"] < 25).sum())

print("Sensors with more than 75% coverage:",
      (summary["coverage_pct"] > 75).sum())

summary.to_csv(OUTPUT_FILE)

print("\nSaved to:", OUTPUT_FILE)
