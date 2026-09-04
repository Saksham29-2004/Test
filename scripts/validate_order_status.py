from pathlib import Path

import pandas as pd


raw_dir = Path("Project-Data/raw")

orders = pd.read_csv(
    raw_dir / "olist_orders_dataset.csv"
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)


def validate_order_status(orders):
    errors = []

    delivered_without_date = (
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].isna()
    )

    count = delivered_without_date.sum()

    if count > 0:
        errors.append(
            f"{count} delivered orders have no "
            f"order_delivered_customer_date"
        )

    return errors, delivered_without_date


errors, delivered_without_date = validate_order_status(orders)


if errors:
    print("VALIDATION FAILED")

    for error in errors:
        print(f"- {error}")
else:
    print("VALIDATION PASSED")
    print(f"Validated {len(orders)} orders")


violations = orders.loc[
    delivered_without_date,
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
]

print("\nViolations:")
print(violations.to_string(index=False))

invalid_non_delivered = (
    (orders["order_status"] != "delivered")
    & orders["order_delivered_customer_date"].notna()
)

print("\nNon-delivered orders with delivery date:")

print(
    orders.loc[
        invalid_non_delivered,
        [
            "order_id",
            "order_status",
            "order_delivered_customer_date",
        ],
    ].to_string(index=False)
)

print(
    orders.loc[
        invalid_non_delivered,
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    ].to_string(index=False)
)

print(
    f"\nCount: {invalid_non_delivered.sum()}"
)