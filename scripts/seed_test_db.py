from pathlib import Path

import pandas as pd

from src.ingestion.pipeline import get_connection


CUSTOMERS_CSV = Path(
    "Project-Data/raw/olist_customers_dataset.csv"
)


def seed_customers():
    customers = pd.read_csv(CUSTOMERS_CSV)

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            for row in customers.itertuples(index=False):
                cur.execute(
                    """
                    INSERT INTO customers (
                        customer_id,
                        customer_unique_id,
                        customer_zip_code_prefix,
                        customer_city,
                        customer_state
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id)
                    DO NOTHING
                    """,
                    (
                        row.customer_id,
                        row.customer_unique_id,
                        row.customer_zip_code_prefix,
                        row.customer_city,
                        row.customer_state,
                    ),
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    seed_customers()
    print("Test customers seeded successfully.")