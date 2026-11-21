
import pandas as pd

INPUT_FILE = "data/processed/HSB_Sensor_Daily_Features.csv"
OUTPUT_FILE = "data/processed/HSB_Sensor_Daily_Complete.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# Generate complete calendar for every sensor
all_dates = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max(),
    freq="D"
)

all_sensors = df["sensor_id"].unique()

calendar = pd.MultiIndex.from_product(
    [all_sensors, all_dates],
    names=["sensor_id", "date"]
).to_frame(index=False)

# Merge actual observations into the calendar
complete = calendar.merge(
    df,
    on=["sensor_id", "date"],
    how="left",
    indicator=True
)

# Identify whether a sensor had an observation that day
complete["observed"] = (
    complete["_merge"] == "both"
).astype(int)

complete.drop(columns=["_merge"], inplace=True)

# Recalculate historical features using observed records only
complete = complete.sort_values(["sensor_id", "date"])

# Missing days remain NaN; do not replace with zero
complete.to_csv(OUTPUT_FILE, index=False)

print("COMPLETE SENSOR CALENDAR CREATED")
print("--------------------------------")

print("Total possible sensor-day records:", len(complete))
print("Observed sensor-days:", complete["observed"].sum())
print("Unobserved sensor-days:", (complete["observed"] == 0).sum())

print("\nObservation distribution:")
print(complete["observed"].value_counts())

print("\nMissing values in daily consumption:")
print(complete["daily_consumption"].isna().sum())

print("\nSaved to:", OUTPUT_FILE)
