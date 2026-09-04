from pathlib import Path

import pandas as pd


SOURCE = Path(
    "Project-Data/raw/olist_orders_dataset.csv"
)

OUTPUT = Path(
    "tests/data/invalid_customer.csv"
)


def main():
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    orders = pd.read_csv(
        SOURCE
    )

    orders = orders.head(3).copy()

    # Create a brand-new order ID so this test
    # cannot accidentally refer to an order that
    # already exists in the final table.
    orders.loc[
        0,
        "order_id",
    ] = "TEST_INVALID_CUSTOMER_001"

    # Deliberately corrupt the customer reference.
    orders.loc[
        0,
        "customer_id",
    ] = "DOES_NOT_EXIST"

    orders.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()