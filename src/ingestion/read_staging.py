import pandas as pd


COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def read_staging_orders(conn, ingestion_id):
    query = """
        SELECT
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        FROM staging_orders
        WHERE ingestion_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (ingestion_id,),
        )

        rows = cur.fetchall()

    return pd.DataFrame(
        rows,
        columns=COLUMNS,
        dtype="string",
    )