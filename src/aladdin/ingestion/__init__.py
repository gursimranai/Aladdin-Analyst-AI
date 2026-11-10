from aladdin.ingestion.csv_loader import load_csv
from aladdin.ingestion.excel_loader import load_excel
from aladdin.ingestion.json_loader import load_json
from aladdin.ingestion.loader import load_data
from aladdin.ingestion.parquet_loader import load_parquet

__all__ = [
    "load_csv",
    "load_excel",
    "load_json",
    "load_parquet",
    "load_data",
]
