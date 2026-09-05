import csv


def load_orders_to_staging(csv_path, ingestion_id, conn):
    staged_count = 0

    with conn.cursor() as cur:
        with open(
            csv_path,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            # Skip CSV header
            next(reader)

            with cur.copy(
                """
                COPY staging_orders (
                    ingestion_id,
                    order_id,
                    customer_id,
                    order_status,
                    order_purchase_timestamp,
                    order_approved_at,
                    order_delivered_carrier_date,
                    order_delivered_customer_date,
                    order_estimated_delivery_date
                )
                FROM STDIN
                """
            ) as copy:

                for row in reader:
                    copy.write_row(
                        (
                            str(ingestion_id),
                            *row,
                        )
                    )

                    staged_count += 1

    return staged_count