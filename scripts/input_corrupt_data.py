from pathlib import Path

import pandas as pd


SOURCE = Path(
    "Project-Data/raw/olist_orders_dataset.csv"
)

OUTPUT = Path(
    "tests/data/recovery_test.csv"
)


def main():
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    orders = pd.read_csv(
        SOURCE
    )

    # Take two real Olist orders.
    orders = orders.head(2).copy()

    # Give them completely new order IDs.
    orders.loc[
        0,
        "order_id",
    ] = "TEST_RECOVERY_001"

    orders.loc[
        1,
        "order_id",
    ] = "TEST_RECOVERY_002"

    # Add one completely synthetic order.
    synthetic_order = {
        "order_id": "TEST_RECOVERY_003",
        "customer_id": orders.loc[0, "customer_id"],
        "order_status": "processing",
        "order_purchase_timestamp": "2026-09-04 10:00:00",
        "order_approved_at": "2026-09-04 10:05:00",
        "order_delivered_carrier_date": None,
        "order_delivered_customer_date": None,
        "order_estimated_delivery_date": "2026-09-15 00:00:00",
    }

    orders = pd.concat(
        [
            orders,
            pd.DataFrame([synthetic_order]),
        ],
        ignore_index=True,
    )

    orders.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()