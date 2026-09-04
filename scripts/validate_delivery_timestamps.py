from pathlib import Path

import pandas as pd


raw_dir = Path("Project-Data/raw")

orders = pd.read_csv(
    raw_dir / "olist_orders_dataset.csv"
)

timestamp_columns = [
    "order_purchase_timestamp",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in timestamp_columns:
    orders[column] = pd.to_datetime(orders[column])


def validate_delivery_timestamps(orders):
    errors = []

    invalid_carrier = (
        orders["order_delivered_carrier_date"].notna()
        & (
            orders["order_delivered_carrier_date"]
            < orders["order_purchase_timestamp"]
        )
    )

    invalid_carrier_count = invalid_carrier.sum()

    if invalid_carrier_count > 0:
        errors.append(
            f"{invalid_carrier_count} orders have "
            f"order_delivered_carrier_date before "
            f"order_purchase_timestamp"
        )

    invalid_customer_delivery = (
        orders["order_delivered_customer_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_purchase_timestamp"]
        )
    )

    invalid_customer_delivery_count = invalid_customer_delivery.sum()

    if invalid_customer_delivery_count > 0:
        errors.append(
            f"{invalid_customer_delivery_count} orders have "
            f"order_delivered_customer_date before "
            f"order_purchase_timestamp"
        )

    return errors, invalid_carrier, invalid_customer_delivery


errors, invalid_carrier, invalid_customer_delivery = (
    validate_delivery_timestamps(orders)
)


violations = orders.loc[
    invalid_carrier,
    [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_carrier_date",
    ],
]

print("\nCarrier timestamp violations:")
print(
    violations.head(20).to_string(index=False)
)
carrier_difference = (
    orders["order_purchase_timestamp"]
    - orders["order_delivered_carrier_date"]
)

print("\nViolation difference:")
print(
    carrier_difference[invalid_carrier].describe()
)

if errors:
    print("\nVALIDATION FAILED")

    for error in errors:
        print(f"- {error}")

else:
    print("\nVALIDATION PASSED")
    print(f"Validated {len(orders)} orders")

print("\nLargest violations:")

largest_violations = orders.loc[
    invalid_carrier,
    [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_carrier_date",
    ],
].copy()

largest_violations["difference"] = (
    largest_violations["order_purchase_timestamp"]
    - largest_violations["order_delivered_carrier_date"]
)

print(
    largest_violations
    .sort_values("difference", ascending=False)
    .head(10)
    .to_string(index=False)
)

invalid_delivery_sequence = (
    orders["order_delivered_carrier_date"].notna()
    & orders["order_delivered_customer_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )
)

invalid_delivery_sequence_count = invalid_delivery_sequence.sum()

if invalid_delivery_sequence_count > 0:
    errors.append(
        f"{invalid_delivery_sequence_count} orders have "
        f"order_delivered_customer_date before "
        f"order_delivered_carrier_date"
    )