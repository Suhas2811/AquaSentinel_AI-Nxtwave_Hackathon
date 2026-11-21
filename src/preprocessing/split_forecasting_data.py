
import pandas as pd

INPUT_FILE = "data/processed/HSB_Forecasting_Features.csv"

TRAIN_FILE = "data/processed/forecast_train.csv"
VAL_FILE = "data/processed/forecast_validation.csv"
TEST_FILE = "data/processed/forecast_test.csv"

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])

# Identify unique dates in chronological order
dates = sorted(df["date"].unique())
n = len(dates)

train_end = int(n * 0.70)
val_end = int(n * 0.85)

train_dates = dates[:train_end]
val_dates = dates[train_end:val_end]
test_dates = dates[val_end:]

train = df[df["date"].isin(train_dates)].copy()
validation = df[df["date"].isin(val_dates)].copy()
test = df[df["date"].isin(test_dates)].copy()

# Verify chronological separation
assert train["date"].max() < validation["date"].min()
assert validation["date"].max() < test["date"].min()

train.to_csv(TRAIN_FILE, index=False)
validation.to_csv(VAL_FILE, index=False)
test.to_csv(TEST_FILE, index=False)

print("CHRONOLOGICAL DATA SPLIT")
print("-----------------------")

for name, data in [
    ("Training", train),
    ("Validation", validation),
    ("Testing", test)
]:
    print(f"\n{name}:")
    print("Rows:", len(data))
    print("Sensors:", data["sensor_id"].nunique())
    print("Start:", data["date"].min())
    print("End:", data["date"].max())

    print("\nRows per sensor:")
    print(data.groupby("sensor_id").size())

print("\nSaved all three datasets successfully.")
