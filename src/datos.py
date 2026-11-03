"""Carga del dataset y nombres de variables usados en todo el proyecto."""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "raw" / "hillstrom.csv"
FIGURAS = RAIZ / "reports" / "figures"
POWERBI = RAIZ / "reports" / "powerbi"

GRUPOS = {"No E-Mail": "Control", "Mens E-Mail": "Hombre", "Womens E-Mail": "Mujer"}
ORDEN_GRUPOS = ["Control", "Hombre", "Mujer"]
COLORES = {"Control": "#8C8C8C", "Hombre": "#1F5A96", "Mujer": "#C0504D"}

METRICAS = {
    "spend": "Ingreso por cliente (USD)",
    "visit": "Tasa de visita",
    "conversion": "Tasa de conversión",
}

COVARIABLES = ["recency", "history", "mens", "womens", "newbie", "zip_code", "channel"]


def cargar() -> pd.DataFrame:
    """Lee el CSV y agrega la columna `grupo` con nombres cortos."""
    if not RUTA_DATOS.exists():
        raise FileNotFoundError(
            f"No encontré {RUTA_DATOS}. Corre primero: python src/descargar_datos.py"
        )
    df = pd.read_csv(RUTA_DATOS)
    df["grupo"] = pd.Categorical(df["segment"].map(GRUPOS), categories=ORDEN_GRUPOS)
    return df
