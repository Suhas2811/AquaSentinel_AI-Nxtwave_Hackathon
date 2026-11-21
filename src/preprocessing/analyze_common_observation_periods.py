
import pandas as pd

input_file = "data/processed/HSB_Forecasting_Daily.csv"

df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])

# Pivot: one row per date, one column per sensor
pivot = df.pivot(
    index="date",
    columns="sensor_id",
    values="observed"
)

# Dates where all seven sensors have observations
all_observed = pivot.eq(1).all(axis=1)

# Identify consecutive common-observation periods
run_id = all_observed.ne(all_observed.shift()).cumsum()

periods = (
    pd.DataFrame({
        "date": pivot.index,
        "all_seven_observed": all_observed.values,
        "run_id": run_id.values
    })
    .loc[lambda x: x["all_seven_observed"]]
    .groupby("run_id")
    .agg(
        start_date=("date", "min"),
        end_date=("date", "max"),
        days=("date", "count")
    )
    .reset_index(drop=True)
)

periods = periods.sort_values("days", ascending=False)

print("COMMON OBSERVATION PERIODS")
print("--------------------------")
print(periods.to_string(index=False))

print("\nTotal days with all seven sensors observed:")
print(int(all_observed.sum()))

print("\nLongest common observation period:")
if len(periods):
    print(periods.iloc[0].to_string())

periods.to_csv(
    "data/metadata/common_observation_periods.csv",
    index=False
)

print("\nSaved to: data/metadata/common_observation_periods.csv")
