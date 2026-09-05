import csv
import uuid
from pathlib import Path


SOURCE = Path("Project-Data/raw/olist_orders_dataset.csv")
OUTPUT_DIR = Path("Project-Data/snapshots")


def generate_snapshot():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_id = uuid.uuid4().hex[:8]
    output = OUTPUT_DIR / f"orders_snapshot_{snapshot_id}.csv"

    with SOURCE.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    # Modify one existing record.
    existing_order = rows[0]
    original_status = existing_order["order_status"]

    existing_order["order_status"] = (
        "processing"
        if original_status != "processing"
        else "delivered"
    )

    # Add one genuinely new order.
    new_order = {
        field: "" for field in fieldnames
    }

    new_order["order_id"] = str(uuid.uuid4())
    new_order["customer_id"] = rows[0]["customer_id"]
    new_order["order_status"] = "created"
    new_order["order_purchase_timestamp"] = "2018-10-01 12:00:00"
    new_order["order_approved_at"] = ""
    new_order["order_delivered_carrier_date"] = ""
    new_order["order_delivered_customer_date"] = ""
    new_order["order_estimated_delivery_date"] = "2018-10-15 12:00:00"

    rows.append(new_order)

    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {output}")
    print(f"Rows: {len(rows)}")
    print(f"Modified existing order: {existing_order['order_id']}")
    print(f"Original status: {original_status}")
    print(f"New status: {existing_order['order_status']}")
    print(f"New order: {new_order['order_id']}")

    return output


if __name__ == "__main__":
    generate_snapshot()