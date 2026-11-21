
import pandas as pd

input_file = "data/metadata/sensor_coverage_summary.csv"
output_file = "data/metadata/sensor_coverage_classified.csv"

df = pd.read_csv(input_file)

def classify_coverage(value):
    if value < 25:
        return "Very Low"
    elif value < 50:
        return "Low"
    elif value < 75:
        return "Moderate"
    else:
        return "High"

df["coverage_category"] = df["coverage_pct"].apply(classify_coverage)

print("SENSOR COVERAGE CLASSIFICATION")
print("-------------------------------")

print("\nCategory counts:")
print(df["coverage_category"].value_counts())

print("\nCategory percentages:")
print(
    df["coverage_category"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nSensors by category:")
print(
    df[["sensor_id", "observed_days", "coverage_pct",
        "coverage_category"]]
    .sort_values("coverage_pct")
    .to_string(index=False)
)

df.to_csv(output_file, index=False)

print(f"\nSaved to: {output_file}")
