from pathlib import Path

from src.ingestion.pipeline import ingest_orders


csv_path = Path(
    "Project-Data/raw/olist_orders_dataset.csv"
)

result = ingest_orders(csv_path)

print(result)