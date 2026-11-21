
import pandas as pd

input_file = "data/processed/HSB_Water_Consumption_Cleaned.csv"
output_file = "data/processed/HSB_Forecasting_Daily.csv"

selected_sensors = [
    "S0102", "S0103", "S0104", "S0105",
    "S0106", "S0107", "S0109"
]

df = pd.read_csv(input_file)

df = df[df["sensor_id"].isin(selected_sensors)].copy()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.normalize()

# Aggregate recorded consumption by sensor and day
daily = (
    df.groupby(["sensor_id", "date"], as_index=False)
    .agg(
        daily_consumption=("value", "sum"),
        event_count=("value", "count"),
        mean_event_value=("value", "mean"),
        max_event_value=("value", "max")
    )
)

# Create complete calendar separately for each sensor
all_dates = pd.date_range(
    daily["date"].min(),
    daily["date"].max(),
    freq="D"
)

sensors = daily["sensor_id"].unique()

calendar = pd.MultiIndex.from_product(
    [sensors, all_dates],
    names=["sensor_id", "date"]
).to_frame(index=False)

daily = calendar.merge(
    daily,
    on=["sensor_id", "date"],
    how="left"
)

daily["observed"] = daily["daily_consumption"].notna().astype(int)

daily = daily.sort_values(
    ["sensor_id", "date"]
).reset_index(drop=True)

daily.to_csv(output_file, index=False)

print("FORECASTING DATASET CREATED")
print("---------------------------")
print("Rows:", len(daily))
print("Sensors:", daily["sensor_id"].nunique())
print("Date range:", daily["date"].min(), "to", daily["date"].max())

print("\nObservations by sensor:")
print(
    daily.groupby("sensor_id")
    .agg(
        observed_days=("observed", "sum"),
        total_days=("date", "count"),
        missing_days=("observed", lambda x: (x == 0).sum())
    )
)

print("\nMissing daily consumption:", daily["daily_consumption"].isna().sum())
print("\nSaved to:", output_file)
