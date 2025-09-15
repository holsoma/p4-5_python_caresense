# """
# Stream and sample rows from a large CSV (233,025 records in your dataset).
# Sticks to built-ins: 'csv' and plain loops (Lec 4: File I/O; Lec 2/3: loops & types).

# Expected columns (tab-separated or comma-separated):
# Author, Review Text, Review Rating, Date, Owner Answer, Owner Answer Date,
# Author Profile, Author Image, Review URL, label, zip, spill1..spill8, state

# We only use a few fields here to keep it light.
# """

# """
# Streaming CSV helpers. We keep the path configurable and support uploads.
# """

# import csv
# import os
# from typing import Iterable, Dict, Generator

# DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
# DEFAULT_DATASET = os.path.join(DATA_DIR, "reviews.csv")

# def ensure_data_dir() -> None:
#     if not os.path.isdir(DATA_DIR):
#         os.makedirs(DATA_DIR, exist_ok=True)

# def dataset_path() -> str:
#     """Return current dataset path; default to data/reviews.csv if present."""
#     ensure_data_dir()
#     if os.path.isfile(DEFAULT_DATASET):
#         return DEFAULT_DATASET
#     return ""  # not set yet

# def read_reviews_csv(path: str, delimiter: str = ",") -> Generator[Dict[str, str], None, None]:
#     with open(path, mode="r", encoding="utf-8", newline="") as f:
#         reader = csv.DictReader(f, delimiter=delimiter)
#         for row in reader:
#             yield row

# def sample_reviews(path: str, limit: int = 100, delimiter: str = ",") -> Iterable[Dict[str, str]]:
#     count = 0
#     for row in read_reviews_csv(path, delimiter=delimiter):
#         yield row
#         count += 1
#         if count >= limit:
#             break

# def extract_text(row: Dict[str, str]) -> str:
#     return row.get("Review Text", "") or ""


"""Simple CSV loader using the stdlib (no pandas), to practice file I/O.
Columns expected: Author, Review Text, Review Rating, Date, State
"""
import csv
from datetime import datetime


def parse_date(s: str) -> str:
    """Normalize dates to YYYY-MM format for grouping. Accepts many forms."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m")
        except ValueError:
            pass
    return "Unknown"


def load_reviews_csv(path: str) -> list[dict]:
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "Author": row.get("Author", "Anonymous"),
                    "Review Text": row.get("Review Text", ""),
                    "Review Rating": int(row.get("Review Rating", "0") or 0),
                    "Date": row.get("Date", ""),
                    "YearMonth": parse_date(row.get("Date", "")),
                    "State": row.get("State", "Unknown"),
                    "Label": row.get("Label", ""),  # may be empty; analyzer will fill
                }
            )
    return rows