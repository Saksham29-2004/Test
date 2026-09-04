from pathlib import Path
import pandas as pd
import time

raw_dir = Path("../Project-Data/raw")
files = raw_dir.glob("*.csv")
print(files)

orders_file = raw_dir / "olist_orders_dataset.csv"
orders = pd.read_csv(orders_file)
print(orders.shape)
def inspect_dataframe(df):
    print("Rows:", len(df))
    print("Columns:", df.columns.tolist())
    print("Nulls:")
    print(df.isna().sum())
    print("Dtypes:")
    print(df.dtypes)
inspect_dataframe(orders)

orders_schema = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

orders_dtypes = {
    "order_id": "object",
    "customer_id": "object",
    "order_status": "object",
    "order_purchase_timestamp": "object",
    "order_approved_at": "object",
    "order_delivered_carrier_date": "object",
    "order_delivered_customer_date": "object",
    "order_estimated_delivery_date": "object"
}

def validate_schema(df, expected_columns):
    missing_columns = set(expected_columns) - set(df.columns)
    extra_columns = set(df.columns) - set(expected_columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if extra_columns:
        raise ValueError(f"Unexpected columns: {extra_columns}")

def validate_unique(df, column):
    if df[column].isna().any():
        raise ValueError(f"{column} contains null values")

    if df[column].nunique() != len(df):
        raise ValueError(f"{column} contains duplicates")

def validate_foreign_key(child_df, child_column, parent_df, parent_column):
    invalid = ~child_df[child_column].isin(parent_df[parent_column])

    if invalid.any():
        raise ValueError(
            f"{invalid.sum()} invalid {child_column} values"
        )
    
orders = pd.read_csv(raw_dir / "olist_orders_dataset.csv")
items = pd.read_csv(raw_dir / "olist_order_items_dataset.csv")

validate_foreign_key(
    items,
    "order_id",
    orders,
    "order_id"
)

print("Foreign key validation passed")
start = time.perf_counter()
dataframes = {}

for file in files:
    print("\n" + "=" * 60)
    print("FILE:", file.name)

    size_mb = file.stat().st_size / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")

    try:
        df = pd.read_csv(file)

        dataframes[file.stem] = df

        inspect_dataframe(df)

    except FileNotFoundError as e:
        print(f"FILE NOT FOUND: {file.name}")
        print(f"ERROR: {e}")
elapsed = time.perf_counter() - start
print(f"Load time: {elapsed:.2f} seconds")
for name, df in dataframes.items():
    print(name, df.memory_usage(deep=True).sum() / (1024 * 1024), "MB")

orders = dataframes["olist_orders_dataset"]
items = dataframes["olist_order_items_dataset"]

print(orders["order_id"].isna().sum())
print(orders["order_id"].nunique())
print(len(orders))
validation_start = time.perf_counter()
validate_schema(orders, orders_schema)

validate_foreign_key(
    items,
    "order_id",
    orders,
    "order_id"
)

print("Foreign key validation passed")
validation_elapsed = time.perf_counter() - validation_start
print(f"Validation time: {validation_elapsed:.4f} seconds")

total_memory = sum(
    df.memory_usage(deep=True).sum()
    for df in dataframes.values()
)

print(
    "Total:",
    total_memory / (1024 * 1024),
    "MB"
)

print(orders["order_status"].value_counts())
