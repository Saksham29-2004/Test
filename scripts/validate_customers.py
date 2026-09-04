from pathlib import Path

import pandas as pd


file_path = Path("Project-Data/raw/olist_customers_dataset.csv")

df = pd.read_csv(file_path)

def validate_customers(df):
    errors = []

    # 1. Required columns
    required_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing columns: {missing_columns}"
        )

    # Stop here if the schema is wrong
    if errors:
        return errors

    # 2. customer_id cannot be NULL
    null_ids = df["customer_id"].isna().sum()

    if null_ids > 0:
        errors.append(
            f"customer_id contains {null_ids} null values"
        )

    # 3. customer_id must be unique
    duplicate_ids = df["customer_id"].duplicated().sum()

    if duplicate_ids > 0:
        errors.append(
            f"customer_id contains {duplicate_ids} duplicate values"
        )

    # 4. customer_unique_id cannot be NULL
    null_unique_ids = df["customer_unique_id"].isna().sum()

    if null_unique_ids > 0:
        errors.append(
            f"customer_unique_id contains {null_unique_ids} null values"
        )

    # 5. ZIP code cannot be NULL
    null_zip_codes = df["customer_zip_code_prefix"].isna().sum()

    if null_zip_codes > 0:
        errors.append(
            f"customer_zip_code_prefix contains {null_zip_codes} null values"
        )

    # 6. City cannot be NULL
    null_cities = df["customer_city"].isna().sum()

    if null_cities > 0:
        errors.append(
            f"customer_city contains {null_cities} null values"
        )

    # 7. State cannot be NULL
    null_states = df["customer_state"].isna().sum()

    if null_states > 0:
        errors.append(
            f"customer_state contains {null_states} null values"
        )

    return errors


errors = validate_customers(df)


if errors:
    print("VALIDATION FAILED")

    for error in errors:
        print(f"- {error}")

else:
    print("VALIDATION PASSED")
    print(f"Validated {len(df)} rows")