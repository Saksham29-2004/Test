from pathlib import Path

from src.ingestion.orders import load_orders_to_staging


csv_path = Path(
    "Project-Data/raw/olist_orders_dataset.csv"
)

ingestion_id = load_orders_to_staging(csv_path)

print("Ingestion ID:", ingestion_id)