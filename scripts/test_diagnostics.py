import pandas as pd

from src.diagnostics.orders import diagnose_carrier_delivery_timestamp


orders = pd.read_csv(
    "Project-Data/raw/olist_orders_dataset.csv"
)

failed_rows = diagnose_carrier_delivery_timestamp(orders)

print("Diagnostic rows:", len(failed_rows))
print()

for _, row in failed_rows.head(5).iterrows():
    print("Order:", row["order_id"])
    print("Purchase:", row["order_purchase_timestamp"])
    print("Carrier:", row["order_delivered_carrier_date"])
    print()