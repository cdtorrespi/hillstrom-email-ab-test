"""Download the Hillstrom dataset (MineThatData, 2008) to data/raw/hillstrom.csv.

Usage:
    python src/download_data.py

If the download fails (the original site is sometimes down), download the CSV
manually from the MineThatData blog or from Kaggle (search for
"Hillstrom email marketing") and save it as data/raw/hillstrom.csv.
"""
from pathlib import Path
import urllib.request

URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
DESTINATION = Path(__file__).resolve().parents[1] / "data" / "raw" / "hillstrom.csv"
COLUMNS = [
    "recency", "history_segment", "history", "mens", "womens", "zip_code",
    "newbie", "channel", "segment", "visit", "conversion", "spend",
]


def validate(path: Path) -> None:
    import pandas as pd

    df = pd.read_csv(path)
    assert list(df.columns) == COLUMNS, f"Unexpected columns: {list(df.columns)}"
    assert len(df) == 64_000, f"Expected 64,000 rows, found {len(df):,}"
    print(f"OK: {len(df):,} rows in {path}")


def main() -> None:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if not DESTINATION.exists():
        print(f"Downloading {URL} ...")
        urllib.request.urlretrieve(URL, DESTINATION)
    validate(DESTINATION)


if __name__ == "__main__":
    main()
