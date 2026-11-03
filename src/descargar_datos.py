"""Descarga el dataset de Hillstrom (MineThatData, 2008) en data/raw/hillstrom.csv.

Uso:
    python src/descargar_datos.py

Si la descarga falla (el sitio original a veces no responde), baja el CSV
manualmente desde el blog de MineThatData o desde Kaggle (buscar
"Hillstrom email marketing") y guárdalo como data/raw/hillstrom.csv.
"""
from pathlib import Path
import urllib.request

URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
DESTINO = Path(__file__).resolve().parents[1] / "data" / "raw" / "hillstrom.csv"
COLUMNAS = [
    "recency", "history_segment", "history", "mens", "womens", "zip_code",
    "newbie", "channel", "segment", "visit", "conversion", "spend",
]


def validar(ruta: Path) -> None:
    import pandas as pd

    df = pd.read_csv(ruta)
    assert list(df.columns) == COLUMNAS, f"Columnas inesperadas: {list(df.columns)}"
    assert len(df) == 64_000, f"Se esperaban 64,000 filas y hay {len(df):,}"
    print(f"OK: {len(df):,} filas en {ruta}")


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    if not DESTINO.exists():
        print(f"Descargando {URL} ...")
        urllib.request.urlretrieve(URL, DESTINO)
    validar(DESTINO)


if __name__ == "__main__":
    main()
