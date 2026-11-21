
import pandas as pd

input_file = "data/processed/HSB_Forecasting_Daily.csv"

df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])

print("FORECASTING DATASET MISSING-DATA ANALYSIS")
print("-----------------------------------------")

for sensor_id, group in df.groupby("sensor_id"):

    group = group.sort_values("date")
    missing = group["observed"].eq(0)

    # Identify consecutive missing-day groups
    run_id = missing.ne(missing.shift()).cumsum()

    missing_runs = (
        group.loc[missing]
        .assign(run_id=run_id[missing])
        .groupby("run_id")
        .size()
    )

    print(f"\nSensor: {sensor_id}")
    print("Missing days:", int(missing.sum()))
    print("Missing periods:", len(missing_runs))
    print(
        "Longest missing period:",
        int(missing_runs.max()) if len(missing_runs) else 0,
        "days"
    )
    print(
        "Average missing period:",
        round(missing_runs.mean(), 2) if len(missing_runs) else 0,
        "days"
    )

print("\nOverall missing observations:")
print(int(df["daily_consumption"].isna().sum()))

print("\nMissing observations by sensor:")
print(
    df.groupby("sensor_id")["daily_consumption"]
    .apply(lambda x: x.isna().sum())
)
