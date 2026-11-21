
from pathlib import Path
import pandas as pd

DATA_PATH = Path(
    "data/raw/HSB_Living_Lab_Water_Consumption_Anonymized.csv"
)

df = pd.read_csv(DATA_PATH, sep=";")
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(["sensor_id", "timestamp"]).copy()

df["aggregated_diff"] = (
    df.groupby("sensor_id")["aggregated_value"].diff()
)

df["error"] = (
    df["aggregated_diff"] - df["value"]
).abs()

events = [
    ("2022-02-23 14:00:00", "2022-02-23"),
    ("2022-10-06 10:00:00", "2022-10-06"),
]

for timestamp, date in events:
    t = pd.Timestamp(timestamp)

    affected = df[
        (df["timestamp"] == t) &
        (df["error"] > 0.001)
    ].copy()

    print("\n", "=" * 65)
    print("EVENT:", timestamp)
    print("Affected sensors:", len(affected))

    print("\nDifference statistics:")
    print(affected["aggregated_diff"].describe())

    print("\nConsumption statistics:")
    print(affected["value"].describe())

    print("\nLargest cumulative jumps:")
    print(
        affected[
            ["sensor_id", "value",
             "aggregated_value", "aggregated_diff"]
        ]
        .sort_values("aggregated_diff", ascending=False)
        .head(15)
        .to_string(index=False)
    )
