
import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.normalize()

priority_sensors = {
    "S0208": ["2020-10-10", "2020-10-11", "2020-10-12"],
    "S0101": ["2021-03-20", "2021-03-21", "2021-03-22", "2021-03-23"],
    "S0212": ["2022-04-17", "2022-07-06", "2021-01-12"]
}

for sensor, dates in priority_sensors.items():

    sensor_df = df[df["sensor_id"] == sensor].copy()

    print("\n" + "=" * 65)
    print("SENSOR:", sensor)
    print("=" * 65)

    # Overall daily event-frequency statistics
    daily = sensor_df.groupby("date").agg(
        event_count=("value", "size"),
        daily_consumption=("value", "sum")
    )

    print("\nDaily event count distribution:")
    print(daily["event_count"].describe(
        percentiles=[0.50, 0.90, 0.95, 0.99]
    ))

    for date in dates:

        target_date = pd.Timestamp(date)

        day_df = sensor_df[
            sensor_df["date"] == target_date
        ].sort_values("timestamp").copy()

        if day_df.empty:
            print("\nNo records:", date)
            continue

        # Time difference between consecutive events
        day_df["minutes_since_previous"] = (
            day_df["timestamp"].diff().dt.total_seconds() / 60
        )

        print("\nDate:", date)
        print("Event count:", len(day_df))
        print("Daily consumption:", round(day_df["value"].sum(), 5))
        print("Mean event value:", round(day_df["value"].mean(), 5))
        print("Maximum event:", day_df["value"].max())

        print("\nTime gap statistics (minutes):")
        print(
            day_df["minutes_since_previous"].describe().round(2)
        )

        print("\nFirst 10 events:")
        print(
            day_df[
                ["timestamp", "value", "type", "attached_to",
                 "minutes_since_previous"]
            ].head(10).to_string(index=False)
        )

        print("\nLast 5 events:")
        print(
            day_df[
                ["timestamp", "value", "minutes_since_previous"]
            ].tail(5).to_string(index=False)
        )

print("\nEVENT FREQUENCY INVESTIGATION COMPLETED")
