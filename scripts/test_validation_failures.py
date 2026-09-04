import pandas as pd

from src.validation.runner import run_validations, should_block


raw_dir = "Project-Data/raw"

customers = pd.read_csv(
    f"{raw_dir}/olist_customers_dataset.csv"
)

orders = pd.read_csv(
    f"{raw_dir}/olist_orders_dataset.csv"
)

# Deliberate corruption
orders.loc[0, "customer_id"] = "DOES_NOT_EXIST"

results = run_validations(
    orders,
    customers
)

blocking_rules = should_block(results)

print("RESULTS:")
for result in results:
    if result["failed"] > 0:
        print(result)

print()
print("BLOCKING RULES:", blocking_rules)
print("BLOCK INGESTION:", bool(blocking_rules))