from .base import validate_result

from .orders import (
    validate_order_customer_ids,
    validate_order_id_unique,
    validate_carrier_delivery_timestamp,
    validate_estimated_delivery_timestamp,
    validate_purchase_timestamp_parseable,
    validate_estimated_delivery_timestamp_parseable,
    validate_required_order_fields,
)


def run_validations(orders, customers):
    context = {
        "orders": orders,
        "customers": customers,
    }

    validators = [
        validate_order_customer_ids,
        validate_order_id_unique,
        validate_carrier_delivery_timestamp,
        validate_estimated_delivery_timestamp,
        validate_purchase_timestamp_parseable,
        validate_estimated_delivery_timestamp_parseable,
        validate_required_order_fields,
    ]

    results = []

    for validator in validators:
        result = validator(context)
        validate_result(result)
        results.append(result)

    return results


def should_block(results):
    blocking_rules = []

    for result in results:
        if result["failed"] > 0:
            if result["severity"] == "ERROR":
                blocking_rules.append(result["rule"])

    return blocking_rules


if __name__ == "__main__":
    import pandas as pd
    from pathlib import Path

    raw_dir = Path("Project-Data/raw")

    customers = pd.read_csv(
        raw_dir / "olist_customers_dataset.csv"
    )

    orders = pd.read_csv(
        raw_dir / "olist_orders_dataset.csv"
    )

    results = run_validations(
        orders,
        customers,
    )

    print(results)

    blocking_rules = should_block(results)

    print("BLOCKING RULES:", blocking_rules)

    if blocking_rules:
        print("BLOCK INGESTION: True")
    else:
        print("BLOCK INGESTION: False")