
import pandas as pd

input_file = "data/processed/HSB_Forecasting_Daily.csv"
output_file = "data/processed/HSB_Forecasting_Continuous.csv"

df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])

start_date = "2020-08-21"
end_date = "2021-11-22"

# Select the longest common observation period
continuous = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
].copy()

# Verify all seven sensors have observations every day
daily_sensor_counts = (
    continuous.groupby("date")["observed"].sum()
)

assert (daily_sensor_counts == 7).all(), (
    "Some dates do not have all seven sensor observations."
)

assert continuous["daily_consumption"].notna().all(), (
    "Missing consumption values found."
)

continuous = continuous.sort_values(
    ["sensor_id", "date"]
).reset_index(drop=True)

continuous.to_csv(output_file, index=False)

print("CONTINUOUS FORECASTING DATASET")
print("------------------------------")
print("Rows:", len(continuous))
print("Sensors:", continuous["sensor_id"].nunique())
print("Dates:", continuous["date"].nunique())
print("Start:", continuous["date"].min())
print("End:", continuous["date"].max())
print("Missing consumption:", continuous["daily_consumption"].isna().sum())

print("\nRows per sensor:")
print(continuous.groupby("sensor_id").size())

print("\nSaved to:", output_file)
