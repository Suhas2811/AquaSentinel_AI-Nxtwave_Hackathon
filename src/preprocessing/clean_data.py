
from pathlib import Path
import pandas as pd
import numpy as np
import json

# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "HSB_Living_Lab_Water_Consumption_Anonymized.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD RAW DATA
# ==========================================

def load_data():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATA_PATH}"
        )

    df = pd.read_csv(RAW_DATA_PATH, sep=";")

    print("RAW DATA LOADED")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    return df


# ==========================================
# 3. BASIC VALIDATION
# ==========================================

def validate_data(df):

    required_columns = [
        "timestamp",
        "date",
        "hour",
        "day_of_week",
        "day_name",
        "month",
        "year",
        "sensor_id",
        "apartment",
        "cluster_name",
        "room_number",
        "room_type",
        "type",
        "attached_to",
        "value",
        "aggregated_value"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("\nCOLUMN VALIDATION PASSED")


# ==========================================
# 4. INITIAL DATA QUALITY CHECKS
# ==========================================

def inspect_quality(df):

    report = {
        "raw_rows": int(len(df)),
        "raw_columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),

        "missing_values": {
            col: int(count)
            for col, count in df.isna().sum().items()
        },

        "invalid_or_nonpositive_value": int(
            (~np.isfinite(df["value"]) | (df["value"] <= 0)).sum()
        )
    }

    print("\nINITIAL DATA QUALITY")

    print("Duplicate rows:", report["duplicate_rows"])

    print(
        "Invalid/nonpositive consumption values:",
        report["invalid_or_nonpositive_value"]
    )

    # ======================================
    # 5. DUPLICATE INVESTIGATION
    # ======================================

    duplicate_mask = df.duplicated(keep=False)

    duplicate_records = df[duplicate_mask].copy()

    print("\nDUPLICATE INVESTIGATION")

    print(
        "Rows involved in duplicate groups:",
        len(duplicate_records)
    )

    print("\nDuplicate records by sensor:")

    print(
        duplicate_records["sensor_id"]
        .value_counts()
        .head(10)
    )

    print("\nSample duplicate records:")

    if not duplicate_records.empty:
        print(
            duplicate_records.head(10).to_string(index=False)
        )
    else:
        print("No duplicate records found.")

    report["rows_in_duplicate_groups"] = int(
        len(duplicate_records)
    )

    report["duplicate_sensors"] = int(
        duplicate_records["sensor_id"].nunique()
    )

    # ======================================
    # 6. DUPLICATE GROUP FREQUENCIES
    # ======================================

    duplicate_groups = (
        df[df.duplicated(keep=False)]
        .groupby(list(df.columns), dropna=False)
        .size()
    )

    print("\nDUPLICATE GROUP FREQUENCIES")

    print(
        duplicate_groups.value_counts().sort_index()
    )

    groups_more_than_twice = int(
        (duplicate_groups > 2).sum()
    )

    print(
        "\nGroups appearing more than twice:",
        groups_more_than_twice
    )

    report["duplicate_group_frequencies"] = {
        str(count): int(groups)
        for count, groups in
        duplicate_groups.value_counts().sort_index().items()
    }

    report["duplicate_groups_more_than_twice"] = (
        groups_more_than_twice
    )

    return report



# ==========================================
# 7. CLEAN EXACT DUPLICATES
# ==========================================

def clean_data(df):

    print("\nDATA CLEANING")

    original_rows = len(df)

    # Remove exact duplicate rows
    cleaned_df = df.drop_duplicates().copy()

    removed_rows = original_rows - len(cleaned_df)

    print("Original rows:", original_rows)
    print("Removed exact duplicates:", removed_rows)
    print("Cleaned rows:", len(cleaned_df))

    # Verify no exact duplicates remain
    remaining_duplicates = cleaned_df.duplicated().sum()

    print("Remaining duplicates:", remaining_duplicates)

    if remaining_duplicates != 0:
        raise ValueError("Duplicate removal verification failed.")

    # Save processed dataset
    output_path = (
        PROCESSED_DIR / "HSB_Water_Consumption_Cleaned.csv"
    )

    cleaned_df.to_csv(output_path, index=False)

    print("\nCleaned dataset saved to:")
    print(output_path)

    return cleaned_df


# ==========================================
# 8. MAIN EXECUTION
# ==========================================

def main():

    df = load_data()

    validate_data(df)

    report = inspect_quality(df)

    cleaned_df = clean_data(df)

    print("\n" + "=" * 60)
    print("DATA QUALITY AUDIT AND CLEANING COMPLETED")
    print("=" * 60)

    print("Raw dataset rows:", len(df))
    print("Processed dataset rows:", len(cleaned_df))
    print("Raw dataset remains unchanged.")

    print("\nReport summary:")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()

