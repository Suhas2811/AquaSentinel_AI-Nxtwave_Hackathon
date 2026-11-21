
import pandas as pd

input_file = "data/processed/HSB_Forecasting_Daily.csv"

df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])

# Find consecutive missing periods for each sensor
all_periods = []

for sensor_id, group in df.groupby("sensor_id"):
    group = group.sort_values("date").copy()

    missing = group["observed"].eq(0)
    run_id = missing.ne(missing.shift()).cumsum()

    missing_rows = group.loc[missing].copy()
    missing_rows["run_id"] = run_id[missing]

    periods = (
        missing_rows.groupby("run_id")
        .agg(
            start_date=("date", "min"),
            end_date=("date", "max"),
            missing_days=("date", "count")
        )
        .reset_index(drop=True)
    )

    periods["sensor_id"] = sensor_id
    all_periods.append(periods)

periods_df = pd.concat(all_periods, ignore_index=True)

periods_df = periods_df[
    ["sensor_id", "start_date", "end_date", "missing_days"]
].sort_values(["start_date", "sensor_id"])

print("MISSING PERIODS BY SENSOR")
print("-------------------------")
print(periods_df.to_string(index=False))

# Count how many sensors are missing on each calendar day
daily_missing = (
    df.groupby("date")["observed"]
    .apply(lambda x: (x == 0).sum())
)

print("\nCOMMON MISSING-DATA PERIODS")
print("---------------------------")
print("Dates when all 7 sensors are missing:")

all_missing_dates = daily_missing[daily_missing == 7]

if len(all_missing_dates):
    print(all_missing_dates.to_string())
else:
    print("No dates where all 7 sensors are missing.")

print("\nDates when at least 5 sensors are missing:")
print(daily_missing[daily_missing >= 5].to_string())

# Save detailed results
periods_df.to_csv(
    "data/metadata/forecasting_missing_periods.csv",
    index=False
)

print(
    "\nSaved to: data/metadata/forecasting_missing_periods.csv"
)
