from pathlib import Path

import pandas as pd


raw_dir = Path("Project-Data/raw")

orders = pd.read_csv(
    raw_dir / "olist_orders_dataset.csv"
)

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders["order_approved_at"] = pd.to_datetime(
    orders["order_approved_at"]
)


def validate_order_timestamps(orders):
    errors = []

    invalid_approved = (
        orders["order_approved_at"].notna()
        & (
            orders["order_approved_at"]
            < orders["order_purchase_timestamp"]
        )
    )

    invalid_count = invalid_approved.sum()

    if invalid_count > 0:
        errors.append(
            f"{invalid_count} orders have "
            f"order_approved_at before order_purchase_timestamp"
        )

    return errors


errors = validate_order_timestamps(orders)


if errors:
    print("VALIDATION FAILED")

    for error in errors:
        print(f"- {error}")

else:
    print("VALIDATION PASSED")
    print(f"Validated {len(orders)} orders")