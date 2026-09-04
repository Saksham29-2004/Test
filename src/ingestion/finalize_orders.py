import psycopg


def finalize_orders(conn, ingestion_id):
    query = """
        INSERT INTO orders (
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        )
        SELECT
            order_id,
            customer_id,
            order_status,
            NULLIF(order_purchase_timestamp, '')::timestamp,
            NULLIF(order_approved_at, '')::timestamp,
            NULLIF(order_delivered_carrier_date, '')::timestamp,
            NULLIF(order_delivered_customer_date, '')::timestamp,
            NULLIF(order_estimated_delivery_date, '')::timestamp
        FROM staging_orders
        WHERE ingestion_id = %s
        ON CONFLICT (order_id)
        DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            order_status = EXCLUDED.order_status,
            order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
            order_approved_at = EXCLUDED.order_approved_at,
            order_delivered_carrier_date = EXCLUDED.order_delivered_carrier_date,
            order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
            order_estimated_delivery_date = EXCLUDED.order_estimated_delivery_date;
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (ingestion_id,),
        )

        return cur.rowcount