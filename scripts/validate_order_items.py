from pathlib import Path

import pandas as pd


raw_dir = Path("Project-Data/raw")

orders = pd.read_csv(
    raw_dir / "olist_orders_dataset.csv"
)

order_items = pd.read_csv(
    raw_dir / "olist_order_items_dataset.csv"
)

def validate_order_items(order_items, orders):
    errors = []

    valid_order_ids = set(orders["order_id"])

    invalid_order_ids = (
        ~order_items["order_id"].isin(valid_order_ids)
    )

    invalid_count = invalid_order_ids.sum()

    if invalid_count > 0:
        errors.append(
            f"order_items contains {invalid_count} order_id values "
            f"that do not exist in orders"
        )

    return errors


errors = validate_order_items(order_items, orders)


if errors:
    print("VALIDATION FAILED")

    for error in errors:
        print(f"- {error}")

else:
    print("VALIDATION PASSED")
    print(f"Validated {len(order_items)} order items")