
from pathlib import Path
import pandas as pd

# Dataset location
DATA_PATH = Path(
    "data/raw/HSB_Living_Lab_Water_Consumption_Anonymized.csv"
)

print("=" * 65)
print("AQUASENTINEL AI - DATASET INSPECTION")
print("=" * 65)

# Check whether the dataset exists
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

# Load dataset
df = pd.read_csv(DATA_PATH, sep=";")

# 1. Dataset dimensions
print("\n1. DATASET DIMENSIONS")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 2. Column names
print("\n2. COLUMN NAMES")
print(df.columns.tolist())

# 3. Data types
print("\n3. DATA TYPES")
print(df.dtypes)

# 4. Missing values
print("\n4. MISSING VALUES")
print(df.isnull().sum())

# 5. Duplicate records
print("\n5. DUPLICATE RECORDS")
print(df.duplicated().sum())

# 6. First five records
print("\n6. FIRST FIVE RECORDS")
print(df.head().to_string())

# 7. Dataset information
print("\n7. DATASET INFORMATION")
df.info()

# 8. Numerical summary
print("\n8. NUMERICAL SUMMARY")
print(df.describe().to_string())

print("\n" + "=" * 65)
print("INITIAL INSPECTION COMPLETED")
print("=" * 65)
