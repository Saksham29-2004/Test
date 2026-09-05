import psycopg

from src.ingestion.finalize_orders import finalize_orders


INGESTION_ID = "ee1ab6dd-a4f6-4086-abb0-3c1066e777f4"

conn = psycopg.connect(
    "dbname=olist user=olist_user password=olist_password host=localhost port=5432"
)

try:
    before = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    inserted = finalize_orders(conn, INGESTION_ID)

    after = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    print("Before:", before)
    print("finalize_orders rowcount:", inserted)
    print("After:", after)

    conn.commit()

finally:
    conn.close()