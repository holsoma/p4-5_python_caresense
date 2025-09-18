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


# upload dataset function here