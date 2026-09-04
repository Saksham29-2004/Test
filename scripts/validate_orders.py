from pathlib import Path

import pandas as pd


raw_dir = Path("Project-Data/raw")

customers = pd.read_csv(
    raw_dir / "olist_customers_dataset.csv"
)

orders = pd.read_csv(
    raw_dir / "olist_orders_dataset.csv"
)

def validate_order_customer_ids(orders, customers):
    # Customer IDs that are valid according to the customers dataset
    valid_customer_ids = set(customers["customer_id"])

    # True for every order whose customer_id does not exist
    invalid_customer_ids = (
        ~orders["customer_id"].isin(valid_customer_ids)
    )

    # Number of orders that failed the rule
    invalid_count = invalid_customer_ids.sum()

    # Number of orders that passed the rule
    valid_count = len(orders) - invalid_count

    return {
        "rule": "order_customer_exists",
        "type": "referential_integrity",
        "severity": "ERROR",
        "passed": valid_count,
        "failed": invalid_count,
    }


result = validate_order_customer_ids(orders, customers)

print(result)