from pathlib import Path
import time

import pandas as pd
import psycopg


conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="olist",
    user="olist_user",
    password="olist_password",
)

df = pd.read_csv(
    Path("Project-Data/raw/olist_customers_dataset.csv")
)

batch_size = 10000

start_time = time.perf_counter()

with conn.cursor() as cur:

    for start in range(0, len(df), batch_size):

        batch = df.iloc[start:start + batch_size]

        parameters = [
            (
                row["customer_id"],
                row["customer_unique_id"],
                row["customer_zip_code_prefix"],
                row["customer_city"],
                row["customer_state"],
            )
            for _, row in batch.iterrows()
        ]

        cur.executemany(
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
            DO UPDATE SET
                customer_unique_id = EXCLUDED.customer_unique_id,
                customer_zip_code_prefix = EXCLUDED.customer_zip_code_prefix,
                customer_city = EXCLUDED.customer_city,
                customer_state = EXCLUDED.customer_state
            """,
            parameters
        )

        conn.commit()

elapsed = time.perf_counter() - start_time

print(f"Processed {len(df)} rows")
print(f"Ingestion took {elapsed:.2f} seconds")

conn.close()