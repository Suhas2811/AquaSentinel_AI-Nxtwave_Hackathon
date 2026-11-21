import pandas as pd

INPUT_FILE = "data/processed/HSB_Water_Consumption_Cleaned.csv"
OUTPUT_FILE = "data/metadata/high_consumption_records.csv"

df = pd.read_csv(INPUT_FILE)

high_values = df[df["value"] >= 0.10].copy()

high_values = high_values.sort_values(
    by="value",
    ascending=False
)

high_values.to_csv(OUTPUT_FILE, index=False)

print("HIGH-VALUE RECORD EXTRACTION")
print("----------------------------")
print("Total records:", len(df))
print("Extracted records:", len(high_values))
print("Minimum extracted value:", high_values["value"].min())
print("Maximum extracted value:", high_values["value"].max())

print("\nRecords by fixture:")
print(high_values["attached_to"].value_counts())

print("\nRecords by water type:")
print(high_values["type"].value_counts())

print("\nSaved to:", OUTPUT_FILE)