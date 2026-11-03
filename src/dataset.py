"""Dataset loading and variable names used across the project."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "hillstrom.csv"
FIGURES = ROOT / "reports" / "figures"
POWERBI = ROOT / "reports" / "powerbi"

GROUPS = {"No E-Mail": "Control", "Mens E-Mail": "Mens", "Womens E-Mail": "Womens"}
GROUP_ORDER = ["Control", "Mens", "Womens"]
COLORS = {"Control": "#8C8C8C", "Mens": "#1F5A96", "Womens": "#C0504D"}

METRICS = {
    "spend": "Revenue per customer (USD)",
    "visit": "Visit rate",
    "conversion": "Conversion rate",
}

COVARIATES = ["recency", "history", "mens", "womens", "newbie", "zip_code", "channel"]


def load() -> pd.DataFrame:
    """Read the CSV and add a `group` column with short names."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run first: python src/download_data.py"
        )
    df = pd.read_csv(DATA_PATH)
    df["group"] = pd.Categorical(df["segment"].map(GROUPS), categories=GROUP_ORDER)
    return df
