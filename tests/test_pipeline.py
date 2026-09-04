from pathlib import Path

import pandas as pd

from src.ingestion.pipeline import (
    get_connection,
    ingest_orders,
)


VALID_CSV_PATH = Path(
    "Project-Data/raw/olist_orders_dataset.csv"
)

INVALID_CSV_PATH = Path(
    "tests/data/invalid_customer.csv"
)


def test_valid_orders_ingest_successfully():
    result = ingest_orders(
        VALID_CSV_PATH
    )

    assert result["status"] == "SUCCESS"

    assert result["blocking_rules"] == []

    assert (
        result["staged_count"]
        == result["finalized_count"]
    )


def test_invalid_customer_is_rejected():
    orders = pd.read_csv(
        INVALID_CSV_PATH
    )

    test_order_id = orders.loc[
        0,
        "order_id",
    ]

    result = ingest_orders(
        INVALID_CSV_PATH
    )

    assert result["status"] == "REJECTED"

    assert (
        "order_customer_exists"
        in result["blocking_rules"]
    )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM orders
                WHERE order_id = %s
                """,
                (test_order_id,),
            )

            count = cur.fetchone()[0]

    finally:
        conn.close()

    assert count == 0