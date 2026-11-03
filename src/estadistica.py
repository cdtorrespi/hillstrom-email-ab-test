"""Funciones estadísticas para el análisis del experimento."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

Z_975 = stats.norm.ppf(0.975)


@dataclass
class Resultado:
    metrica: str
    comparacion: str
    tratamiento: float
    control: float
    diferencia: float
    ic_inf: float
    ic_sup: float
    p_valor: float

    @property
    def lift(self) -> float:
        return self.diferencia / self.control if self.control else np.nan


# --------------------------------------------------------------------------
# Validaciones
# --------------------------------------------------------------------------
def prueba_srm(conteos: pd.Series, proporciones: list[float] | None = None) -> tuple[float, float]:
    """Chi-cuadrada de sample ratio mismatch. Devuelve (estadístico, p-valor)."""
    obs = np.asarray(conteos, dtype=float)
    if proporciones is None:
        proporciones = [1 / len(obs)] * len(obs)
    esperados = obs.sum() * np.asarray(proporciones)
    chi2, p = stats.chisquare(obs, esperados)
    return float(chi2), float(p)


def diferencia_estandarizada(x_t: np.ndarray, x_c: np.ndarray) -> float:
    """Diferencia estandarizada de medias (DEM) entre dos grupos."""
    x_t, x_c = np.asarray(x_t, float), np.asarray(x_c, float)
    sd = np.sqrt((x_t.var(ddof=1) + x_c.var(ddof=1)) / 2)
    return float((x_t.mean() - x_c.mean()) / sd) if sd > 0 else 0.0


def efecto_minimo_detectable(sd: float, n_t: int, n_c: int, alpha: float = 0.05, poder: float = 0.8) -> float:
    """MDE absoluto para una diferencia de medias (o proporciones con sd = sqrt(p(1-p)))."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(poder)
    return float(z * sd * np.sqrt(1 / n_t + 1 / n_c))


# --------------------------------------------------------------------------
# Pruebas de efecto
# --------------------------------------------------------------------------
def comparar_proporciones(y_t: np.ndarray, y_c: np.ndarray, metrica: str, comparacion: str) -> Resultado:
    """Diferencia de proporciones: IC de Wald (no agrupado) y prueba z (agrupada)."""
    y_t, y_c = np.asarray(y_t), np.asarray(y_c)
    n_t, n_c = len(y_t), len(y_c)
    p_t, p_c = y_t.mean(), y_c.mean()
    dif = p_t - p_c
    se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    p_pool = (y_t.sum() + y_c.sum()) / (n_t + n_c)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    p_val = 2 * stats.norm.sf(abs(dif / se_pool))
    return Resultado(metrica, comparacion, p_t, p_c, dif, dif - Z_975 * se, dif + Z_975 * se, float(p_val))


def comparar_medias(y_t: np.ndarray, y_c: np.ndarray, metrica: str, comparacion: str) -> Resultado:
    """Diferencia de medias con prueba de Welch."""
    y_t, y_c = np.asarray(y_t, float), np.asarray(y_c, float)
    dif = y_t.mean() - y_c.mean()
    se = np.sqrt(y_t.var(ddof=1) / len(y_t) + y_c.var(ddof=1) / len(y_c))
    p_val = stats.ttest_ind(y_t, y_c, equal_var=False).pvalue
    return Resultado(metrica, comparacion, y_t.mean(), y_c.mean(), dif, dif - Z_975 * se, dif + Z_975 * se, float(p_val))


def bootstrap_diferencia(y_t: np.ndarray, y_c: np.ndarray, n_boot: int = 10_000, semilla: int = 42,
                         bloque: int = 500) -> np.ndarray:
    """Distribución bootstrap de la diferencia de medias (remuestreo dentro de cada grupo)."""
    rng = np.random.default_rng(semilla)
    y_t, y_c = np.asarray(y_t, float), np.asarray(y_c, float)
    salida = np.empty(n_boot)
    for i in range(0, n_boot, bloque):
        k = min(bloque, n_boot - i)
        m_t = y_t[rng.integers(0, len(y_t), size=(k, len(y_t)))].mean(axis=1)
        m_c = y_c[rng.integers(0, len(y_c), size=(k, len(y_c)))].mean(axis=1)
        salida[i:i + k] = m_t - m_c
    return salida


def ajuste_holm(p_valores) -> np.ndarray:
    """P-valores ajustados por Holm-Bonferroni."""
    p = np.asarray(p_valores, float)
    m = len(p)
    orden = np.argsort(p)
    ajustados = np.empty(m)
    acumulado = 0.0
    for rango, idx in enumerate(orden):
        acumulado = max(acumulado, (m - rango) * p[idx])
        ajustados[idx] = min(acumulado, 1.0)
    return ajustados


def tabla_resultados(resultados: list[Resultado]) -> pd.DataFrame:
    df = pd.DataFrame([{**r.__dict__, "lift": r.lift} for r in resultados])
    df["p_holm"] = df.groupby("metrica")["p_valor"].transform(ajuste_holm)
    return df


# --------------------------------------------------------------------------
# Regresión con errores robustos (para interacciones por segmento)
# --------------------------------------------------------------------------
def ols_robusto(X: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
    """MCO con errores estándar robustos HC1. X debe incluir la constante."""
    Xm = X.to_numpy(float)
    y = np.asarray(y, float)
    n, k = Xm.shape
    XtX_inv = np.linalg.pinv(Xm.T @ Xm)
    beta = XtX_inv @ Xm.T @ y
    resid = y - Xm @ beta
    meat = (Xm * resid[:, None] ** 2).T @ Xm
    cov = XtX_inv @ meat @ XtX_inv * n / (n - k)
    se = np.sqrt(np.diag(cov))
    tabla = pd.DataFrame(
        {"coef": beta, "se": se, "p_valor": 2 * stats.norm.sf(np.abs(beta / se))},
        index=X.columns,
    )
    # La matriz de covarianzas se guarda para las pruebas de Wald conjuntas
    tabla.attrs["cov"] = pd.DataFrame(cov, index=X.columns, columns=X.columns)
    return tabla


def prueba_wald(tabla: pd.DataFrame, terminos: list[str]) -> float:
    """Prueba de Wald conjunta de que los coeficientes en `terminos` son cero."""
    if not terminos:
        return np.nan
    b = tabla.loc[terminos, "coef"].to_numpy()
    V = tabla.attrs["cov"].loc[terminos, terminos].to_numpy()
    w = float(b @ np.linalg.pinv(V) @ b)
    return float(stats.chi2.sf(w, df=len(terminos)))
