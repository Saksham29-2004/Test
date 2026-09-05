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
            s.order_id,
            s.customer_id,
            s.order_status,
            NULLIF(s.order_purchase_timestamp, '')::timestamp,
            NULLIF(s.order_approved_at, '')::timestamp,
            NULLIF(s.order_delivered_carrier_date, '')::timestamp,
            NULLIF(s.order_delivered_customer_date, '')::timestamp,
            NULLIF(s.order_estimated_delivery_date, '')::timestamp
        FROM staging_orders s
        WHERE s.ingestion_id = %s
          AND NOT EXISTS (
              SELECT 1
              FROM orders o
              WHERE o.order_id = s.order_id
          )
        ON CONFLICT (order_id) DO NOTHING
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (ingestion_id,),
        )

        return cur.rowcount