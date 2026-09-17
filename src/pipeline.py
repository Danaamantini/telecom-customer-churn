"""Single reproducible pipeline for the Telecom Customer Churn project."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.config import (
    ADDON_COLUMNS, BASE_COLUMNS, BOOLEAN_COLUMNS, DATABASE_PATH,
    EXPECTED_FULL_ROWS, FLOAT_COLUMNS, INTEGER_COLUMNS, NULLABLE_TEXT_COLUMNS,
    PROCESSED_DATA_PATH, RAW_COLUMN_MAP, RAW_DATA_PATH, SQL_DIR,
)
from src.validation import validate_processed, validate_raw


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the source CSV without silently converting the literal 'None'."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {path}. See data/README.md for instructions."
        )
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    renamed = raw.rename(columns=RAW_COLUMN_MAP)
    unknown = [column for column in renamed.columns if column not in BASE_COLUMNS]
    missing = [column for column in BASE_COLUMNS if column not in renamed.columns]
    if unknown or missing:
        raise ValueError(f"Unexpected raw schema. Missing={missing}; unknown={unknown}")
    return renamed.loc[:, BASE_COLUMNS]


def _to_boolean(series: pd.Series) -> pd.Series:
    normalized = series.fillna("").astype(str).str.strip().str.lower()
    unexpected = set(normalized.unique()) - {"", "yes", "no"}
    if unexpected:
        raise ValueError(f"Unexpected boolean values: {sorted(unexpected)}")
    return normalized.eq("yes").astype(bool)


def _to_numeric(
    series: pd.Series, column: str, fill_value: int | float | None = None
) -> pd.Series:
    normalized = series.replace(r"^\s*$", pd.NA, regex=True)
    numeric = pd.to_numeric(normalized, errors="coerce")
    invalid = normalized.notna() & numeric.isna()
    if invalid.any():
        examples = normalized.loc[invalid].astype(str).unique()[:3].tolist()
        raise ValueError(f"{column} contains invalid numeric values: {examples}")
    if fill_value is not None:
        numeric = numeric.fillna(fill_value)
    return numeric


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert types and engineer five documented, analysis-ready features."""
    cleaned = raw.copy()

    for column in BOOLEAN_COLUMNS:
        cleaned[column] = _to_boolean(cleaned[column])

    for column in NULLABLE_TEXT_COLUMNS:
        cleaned[column] = cleaned[column].map(
            lambda value: pd.NA if not str(value).strip() else str(value).strip()
        )

    for column in INTEGER_COLUMNS:
        fill = 0 if column == "avg_monthly_gb_download" else None
        cleaned[column] = _to_numeric(cleaned[column], column, fill).astype("int64")

    for column in FLOAT_COLUMNS:
        fill = 0.0 if column == "avg_monthly_long_distance_charges" else None
        cleaned[column] = _to_numeric(cleaned[column], column, fill).astype("float64")

    text_columns = set(BASE_COLUMNS) - set(BOOLEAN_COLUMNS) - set(INTEGER_COLUMNS) - set(FLOAT_COLUMNS)
    for column in text_columns - set(NULLABLE_TEXT_COLUMNS):
        cleaned[column] = cleaned[column].astype(str).str.strip()

    cleaned["churn"] = cleaned["customer_status"].eq("Churned").astype(bool)
    cleaned["tenure_group"] = pd.cut(
        cleaned["tenure_months"],
        bins=[0, 12, 24, 36, 48, 60, float("inf")],
        labels=["0-12", "13-24", "25-36", "37-48", "49-60", "61+"],
        include_lowest=True,
    ).astype("string")
    cleaned["contract_commitment"] = cleaned["contract"].map(
        {"Month-to-Month": 0, "One Year": 1, "Two Year": 2}
    ).astype("Int64")
    cleaned["bundle_count"] = cleaned.loc[:, ADDON_COLUMNS].sum(axis=1).astype("int64")
    cleaned["is_fiber"] = cleaned["internet_type"].eq("Fiber Optic").fillna(False).astype(bool)
    return cleaned


def save_processed_data(df: pd.DataFrame, path: Path = PROCESSED_DATA_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def build_database(df: pd.DataFrame, database_path: Path = DATABASE_PATH) -> None:
    """Load the clean table into DuckDB and create the analytical views."""
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError(
            "DuckDB is required. Install dependencies with pip install -r requirements.txt."
        ) from exc

    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database_path)) as connection:
        connection.register("clean_frame", df)
        connection.execute("CREATE OR REPLACE TABLE clean_customers AS SELECT * FROM clean_frame")
        for sql_path in sorted(SQL_DIR.glob("*.sql")):
            connection.execute(sql_path.read_text(encoding="utf-8"))


def run_pipeline(
    raw_path: Path = RAW_DATA_PATH,
    processed_path: Path = PROCESSED_DATA_PATH,
    database_path: Path = DATABASE_PATH,
    strict_reference_checks: bool = True,
) -> dict[str, Any]:
    """Run the full data pipeline and return its validation summary."""
    raw = load_raw_data(Path(raw_path))
    expected_rows = EXPECTED_FULL_ROWS if strict_reference_checks else None
    raw_summary = validate_raw(raw, expected_rows=expected_rows)
    clean = clean_data(raw)
    clean_summary = validate_processed(
        clean,
        expected_rows=expected_rows,
        check_reference_metrics=strict_reference_checks,
    )
    output_path = save_processed_data(clean, Path(processed_path))
    build_database(clean, Path(database_path))
    return {"raw": raw_summary, "processed": clean_summary, "output_path": str(output_path)}
