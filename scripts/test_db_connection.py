import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="olist",
    user="olist_user",
    password="olist_password",
)

with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO customers (
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        )
        VALUES (
            'TEST_CUSTOMER',
            'TEST_UNIQUE',
            12345,
            'test_city',
            'TS'
        )
    """)

conn.commit()

print("Inserted")

conn.close()