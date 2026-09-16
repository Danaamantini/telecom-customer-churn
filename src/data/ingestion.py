"""Ingestion utilities: load raw CSV, stage immutably, and coerce types.

The raw Maven Analytics "Telecom Customer Churn" dataset is a **38-column**
schema with spaced/Title-Case headers. This module:

1. :func:`load_raw` — read the main CSV and rename headers to canonical
   snake_case (no type coercion yet; empty cells surface as NaN).
2. :func:`stage_raw` — copy the raw CSV byte-for-byte into ``data/interim/``
   for reproducibility.
3. :func:`coerce_types` — apply the canonical dtype + empty-value rules.

See ``src/data/config.py`` for the canonical ``SCHEMA`` and coercion groupings,
and ``reports/insights/data_dictionary.md`` for the human-readable contract.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import pandas as pd

from src.data.config import (
    BOOLEAN_COLUMNS,
    NULLABLE_VARCHAR_COLUMNS,
    RAW_COLUMN_MAP,
    RAW_CSV_PATH,
    SCHEMA,
    STAGED_CSV_PATH,
)


def load_raw(path: Optional[str] = None) -> pd.DataFrame:
    """Load the raw Maven Analytics CSV and rename headers to snake_case.

    Parameters
    ----------
    path : str or None
        Explicit path to the raw CSV. When ``None``, defaults to the canonical
        ``data/raw/telecom_customer_churn.csv`` location.

    Returns
    -------
    pd.DataFrame
        Raw dataset with canonical snake_case column names. No type coercion is
        applied here: empty cells surface as NaN (pandas' default) and values
        keep their upstream representation.

    Raises
    ------
    FileNotFoundError
        If the raw CSV has not been dropped into ``data/raw/`` yet.
    """
    csv_path = RAW_CSV_PATH if path is None else Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at {csv_path}. "
            "Drop the Maven Analytics dataset there "
            "(expected filename 'telecom_customer_churn.csv'). "
            "See data/raw/README.md for details."
        )
    df = pd.read_csv(csv_path)
    # Rename spaced/Title-Case headers -> canonical snake_case. Unknown headers
    # are preserved as-is (defensive), but the canonical 38 are always mapped.
    df = df.rename(columns=RAW_COLUMN_MAP)
    return df


def stage_raw() -> pd.DataFrame:
    """Copy the raw CSV into ``data/interim/`` immutably and return it loaded.

    A byte-for-byte copy of the raw CSV is written to the interim staging path
    (``staged_raw.csv``). The raw file is never modified — this is a pure,
    idempotent copy that preserves the exact upstream bytes for reproducibility.

    Returns
    -------
    pd.DataFrame
        The raw dataset (snake_case headers), loaded via :func:`load_raw`.
    """
    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at {RAW_CSV_PATH}. "
            "Drop the Maven Analytics dataset there before staging. "
            "See data/raw/README.md for details."
        )
    STAGED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RAW_CSV_PATH, STAGED_CSV_PATH)
    return load_raw(STAGED_CSV_PATH)


# ---------------------------------------------------------------------------
# Coercion helpers
# ---------------------------------------------------------------------------
def _isna_scalar(value) -> bool:
    """Return True for NaN/None/pd.NA without raising on non-scalar inputs."""
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _yes_to_bool(series: pd.Series) -> pd.Series:
    """Map 'Yes' -> True, everything else (incl. empty/NaN) -> False."""

    def _f(v):
        if _isna_scalar(v):
            return False
        return str(v).strip().lower() == "yes"

    return series.map(_f).astype("bool")


def _nullify_empty(series: pd.Series) -> pd.Series:
    """Map empty/whitespace/NaN values to None, preserving non-empty strings."""

    def _f(v):
        if _isna_scalar(v):
            return None
        s = str(v).strip()
        return s if s else None

    return series.map(_f).astype("object")


def _to_numeric(series: pd.Series, default, dtype: str) -> pd.Series:
    """Parse a column to numeric, mapping empty/NaN/malformed to ``default``."""
    num = pd.to_numeric(series, errors="coerce")
    return num.fillna(default).astype(dtype)


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the canonical dtype profile and empty-value coercion rules.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame as returned by :func:`load_raw` (snake_case columns,
        empty cells -> NaN).

    Returns
    -------
    pd.DataFrame
        A copy with every column cast to its canonical dtype per the rules:

        * BOOLEAN ('Yes' -> True, else False, empty -> False): ``married``,
          ``phone_service``, ``multiple_lines``, ``internet_service``, the 8
          internet add-ons, and ``paperless_billing``.
        * ``internet_type``: keep 'DSL'/'Fiber Optic'/'Cable'; empty -> NULL.
        * ``avg_monthly_gb_download``: empty -> 0 (INTEGER).
        * ``avg_monthly_long_distance_charges``: empty -> 0.0 (DOUBLE).
        * ``churn_category`` / ``churn_reason``: empty -> NULL.
        * ``offer``: keep the 'None' literal (no change).
        * ``monthly_charge`` keeps its 120 negative values — they are flagged
          for EDA, never dropped or imputed here.
    """
    out = df.copy()

    # 1. Boolean flags: 'Yes' -> True, else False (empty -> False).
    for col in BOOLEAN_COLUMNS:
        if col in out.columns:
            out[col] = _yes_to_bool(out[col])

    # 2. Nullable VARCHAR: empty/whitespace -> None.
    for col in NULLABLE_VARCHAR_COLUMNS:
        if col in out.columns:
            out[col] = _nullify_empty(out[col])

    # 3. Numeric columns with a documented empty->default rule.
    if "avg_monthly_gb_download" in out.columns:
        out["avg_monthly_gb_download"] = _to_numeric(
            out["avg_monthly_gb_download"], 0, "int64"
        )
    if "avg_monthly_long_distance_charges" in out.columns:
        out["avg_monthly_long_distance_charges"] = _to_numeric(
            out["avg_monthly_long_distance_charges"], 0.0, "float64"
        )

    # 4. Everything else: cast to its canonical dtype.
    handled = set(BOOLEAN_COLUMNS) | set(NULLABLE_VARCHAR_COLUMNS) | {
        "avg_monthly_gb_download",
        "avg_monthly_long_distance_charges",
    }
    for col, dtype in SCHEMA.items():
        if col in out.columns and col not in handled:
            out[col] = out[col].astype(dtype)

    return out
