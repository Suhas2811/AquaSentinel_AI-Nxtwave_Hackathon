
import pandas as pd

input_file = "data/processed/HSB_Water_Consumption_Cleaned.csv"

selected_sensors = [
    "S0109", "S0103", "S0102", "S0106",
    "S0107", "S0105", "S0104"
]

df = pd.read_csv(input_file)

df = df[df["sensor_id"].isin(selected_sensors)].copy()

print("FORECASTING SENSOR METADATA")
print("----------------------------")

for column in [
    "sensor_id", "room_type", "type", "attached_to",
    "apartment", "cluster_name"
]:
    print(f"\n{column}:")
    print(df.groupby("sensor_id")[column].agg(
        lambda x: x.dropna().unique().tolist()
    ).to_string())

print("\nRECORD COUNTS:")
print(df.groupby("sensor_id").size())

print("\nDATE RANGES:")
df["timestamp"] = pd.to_datetime(df["timestamp"])

print(
    df.groupby("sensor_id")["timestamp"]
    .agg(["min", "max", "count"])
    .to_string()
)
