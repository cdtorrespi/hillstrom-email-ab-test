"""Statistical functions for the experiment analysis."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

Z_975 = stats.norm.ppf(0.975)


@dataclass
class Result:
    metric: str
    comparison: str
    treatment: float
    control: float
    difference: float
    ci_low: float
    ci_high: float
    p_value: float

    @property
    def lift(self) -> float:
        return self.difference / self.control if self.control else np.nan


# --------------------------------------------------------------------------
# Validation checks
# --------------------------------------------------------------------------
def srm_test(counts: pd.Series, proportions: list[float] | None = None) -> tuple[float, float]:
    """Chi-square sample ratio mismatch test. Returns (statistic, p-value)."""
    obs = np.asarray(counts, dtype=float)
    if proportions is None:
        proportions = [1 / len(obs)] * len(obs)
    expected = obs.sum() * np.asarray(proportions)
    chi2, p = stats.chisquare(obs, expected)
    return float(chi2), float(p)


def standardized_difference(x_t: np.ndarray, x_c: np.ndarray) -> float:
    """Standardized mean difference (SMD) between two groups."""
    x_t, x_c = np.asarray(x_t, float), np.asarray(x_c, float)
    sd = np.sqrt((x_t.var(ddof=1) + x_c.var(ddof=1)) / 2)
    return float((x_t.mean() - x_c.mean()) / sd) if sd > 0 else 0.0


def minimum_detectable_effect(sd: float, n_t: int, n_c: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Absolute MDE for a difference in means (or proportions, with sd = sqrt(p(1-p)))."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return float(z * sd * np.sqrt(1 / n_t + 1 / n_c))


# --------------------------------------------------------------------------
# Effect tests
# --------------------------------------------------------------------------
def compare_proportions(y_t: np.ndarray, y_c: np.ndarray, metric: str, comparison: str) -> Result:
    """Difference in proportions: Wald CI (unpooled) and z-test (pooled)."""
    y_t, y_c = np.asarray(y_t), np.asarray(y_c)
    n_t, n_c = len(y_t), len(y_c)
    p_t, p_c = y_t.mean(), y_c.mean()
    diff = p_t - p_c
    se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    p_pool = (y_t.sum() + y_c.sum()) / (n_t + n_c)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    p_val = 2 * stats.norm.sf(abs(diff / se_pool))
    return Result(metric, comparison, p_t, p_c, diff, diff - Z_975 * se, diff + Z_975 * se, float(p_val))


def compare_means(y_t: np.ndarray, y_c: np.ndarray, metric: str, comparison: str) -> Result:
    """Difference in means with Welch's test.

    The CI uses z = 1.96; with ~21k customers per group the difference from Welch's t is negligible.
    """
    y_t, y_c = np.asarray(y_t, float), np.asarray(y_c, float)
    diff = y_t.mean() - y_c.mean()
    se = np.sqrt(y_t.var(ddof=1) / len(y_t) + y_c.var(ddof=1) / len(y_c))
    p_val = stats.ttest_ind(y_t, y_c, equal_var=False).pvalue
    return Result(metric, comparison, y_t.mean(), y_c.mean(), diff, diff - Z_975 * se, diff + Z_975 * se, float(p_val))


def bootstrap_difference(y_t: np.ndarray, y_c: np.ndarray, n_boot: int = 10_000, seed: int = 42,
                         block: int = 500) -> np.ndarray:
    """Bootstrap distribution of the difference in means (resampling within each group)."""
    rng = np.random.default_rng(seed)
    y_t, y_c = np.asarray(y_t, float), np.asarray(y_c, float)
    out = np.empty(n_boot)
    for i in range(0, n_boot, block):
        k = min(block, n_boot - i)
        m_t = y_t[rng.integers(0, len(y_t), size=(k, len(y_t)))].mean(axis=1)
        m_c = y_c[rng.integers(0, len(y_c), size=(k, len(y_c)))].mean(axis=1)
        out[i:i + k] = m_t - m_c
    return out


def holm_adjust(p_values) -> np.ndarray:
    """Holm-Bonferroni adjusted p-values."""
    p = np.asarray(p_values, float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(running, 1.0)
    return adjusted


def results_table(results: list[Result]) -> pd.DataFrame:
    df = pd.DataFrame([{**r.__dict__, "lift": r.lift} for r in results])
    df["p_holm"] = df.groupby("metric")["p_value"].transform(holm_adjust)
    return df


# --------------------------------------------------------------------------
# Regression with robust standard errors (for segment interactions)
# --------------------------------------------------------------------------
def robust_ols(X: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
    """OLS with HC1 robust standard errors. X must include the constant."""
    Xm = X.to_numpy(float)
    y = np.asarray(y, float)
    n, k = Xm.shape
    XtX_inv = np.linalg.pinv(Xm.T @ Xm)
    beta = XtX_inv @ Xm.T @ y
    resid = y - Xm @ beta
    meat = (Xm * resid[:, None] ** 2).T @ Xm
    cov = XtX_inv @ meat @ XtX_inv * n / (n - k)
    se = np.sqrt(np.diag(cov))
    table = pd.DataFrame(
        {"coef": beta, "se": se, "p_value": 2 * stats.norm.sf(np.abs(beta / se))},
        index=X.columns,
    )
    # Keep the covariance matrix for joint Wald tests
    table.attrs["cov"] = pd.DataFrame(cov, index=X.columns, columns=X.columns)
    return table


def wald_test(table: pd.DataFrame, terms: list[str]) -> float:
    """Joint Wald test that the coefficients in `terms` are all zero."""
    if not terms:
        return np.nan
    b = table.loc[terms, "coef"].to_numpy()
    V = table.attrs["cov"].loc[terms, terms].to_numpy()
    w = float(b @ np.linalg.pinv(V) @ b)
    return float(stats.chi2.sf(w, df=len(terms)))
