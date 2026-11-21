
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/HSB_Daily_Consumption.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.sort_values("date")

# Plot 1: Total daily consumption
plt.figure(figsize=(14, 5))
plt.plot(df["date"], df["total_consumption"])
plt.title("Daily Recorded Water Consumption")
plt.xlabel("Date")
plt.ylabel("Recorded Consumption")
plt.grid(True)
plt.tight_layout()
plt.savefig("data/metadata/daily_consumption.png")
plt.show()

# Plot 2: Cold and hot water consumption
plt.figure(figsize=(14, 5))
plt.plot(df["date"], df["cold_consumption"], label="Cold Water")
plt.plot(df["date"], df["hot_consumption"], label="Hot Water")
plt.title("Daily Cold and Hot Water Consumption")
plt.xlabel("Date")
plt.ylabel("Recorded Consumption")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("data/metadata/daily_water_types.png")
plt.show()

# Plot 3: Daily observation coverage
plt.figure(figsize=(14, 5))
plt.plot(df["date"], df["observation_coverage_pct"])
plt.title("Daily Observation Coverage")
plt.xlabel("Date")
plt.ylabel("Coverage (%)")
plt.grid(True)
plt.tight_layout()
plt.savefig("data/metadata/daily_coverage.png")
plt.show()

# Identify unusually high daily values
valid = df["total_consumption"].dropna()

q1 = valid.quantile(0.25)
q3 = valid.quantile(0.75)
iqr = q3 - q1
upper_limit = q3 + 1.5 * iqr

high_days = df[
    df["total_consumption"] > upper_limit
].sort_values("total_consumption", ascending=False)

print("DAILY PATTERN ANALYSIS")
print("----------------------")
print("Q1:", round(q1, 4))
print("Q3:", round(q3, 4))
print("IQR:", round(iqr, 4))
print("Upper investigation threshold:", round(upper_limit, 4))

print("\nHigh-consumption days:", len(high_days))
print(high_days[
    ["date", "total_consumption", "cold_consumption",
     "hot_consumption", "observation_coverage_pct"]
].head(15).to_string(index=False))

print("\nPlots saved in data/metadata/")
