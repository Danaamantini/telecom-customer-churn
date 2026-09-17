"""Fail-fast data-quality checks used by the pipeline and tests."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import (
    BASE_COLUMNS, EXPECTED_CHURNED, EXPECTED_FULL_ROWS, EXPECTED_JOINED,
    PROCESSED_COLUMNS,
)


class DataValidationError(ValueError):
    """Raised when an input or generated dataset violates its contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DataValidationError(message)


def validate_raw(df: pd.DataFrame, expected_rows: int | None = None) -> dict[str, Any]:
    """Validate a raw dataset after its headers have been canonicalized."""
    _require(tuple(df.columns) == BASE_COLUMNS, "Raw columns do not match the 38-column contract.")
    _require(df["customer_id"].notna().all(), "customer_id contains missing values.")
    _require(df["customer_id"].is_unique, "customer_id must be unique.")
    _require(
        set(df["customer_status"].dropna().unique()) <= {"Churned", "Stayed", "Joined"},
        "customer_status contains an unexpected value.",
    )
    if expected_rows is not None:
        _require(len(df) == expected_rows, f"Expected {expected_rows} rows, found {len(df)}.")
    return {"rows": len(df), "columns": len(df.columns), "customer_ids_unique": True}


def validate_processed(
    df: pd.DataFrame,
    expected_rows: int | None = None,
    check_reference_metrics: bool = False,
) -> dict[str, Any]:
    """Validate the analysis-ready 43-column customer table."""
    _require(tuple(df.columns) == PROCESSED_COLUMNS, "Processed columns do not match the 43-column contract.")
    _require(df["customer_id"].is_unique, "Processed customer_id must be unique.")
    _require(df["churn"].dtype == bool, "churn must be boolean.")
    _require(df["is_fiber"].dtype == bool, "is_fiber must be boolean.")
    _require(df["bundle_count"].between(0, 8).all(), "bundle_count must be between 0 and 8.")
    _require(
        df["contract_commitment"].dropna().isin([0, 1, 2]).all(),
        "contract_commitment must contain only 0, 1, or 2.",
    )
    _require(df["tenure_group"].notna().all(), "tenure_group contains missing values.")
    if expected_rows is not None:
        _require(len(df) == expected_rows, f"Expected {expected_rows} rows, found {len(df)}.")

    churned = int(df["churn"].sum())
    joined = int((df["customer_status"] == "Joined").sum())
    if check_reference_metrics:
        _require(len(df) == EXPECTED_FULL_ROWS, "Reference metrics require the full dataset.")
        _require(churned == EXPECTED_CHURNED, f"Expected {EXPECTED_CHURNED} churned customers, found {churned}.")
        _require(joined == EXPECTED_JOINED, f"Expected {EXPECTED_JOINED} joined customers, found {joined}.")

    existing = df["customer_status"] != "Joined"
    churn_rate = float(df.loc[existing, "churn"].mean()) if existing.any() else 0.0
    return {
        "rows": len(df), "columns": len(df.columns), "churned": churned,
        "joined": joined, "churn_rate": churn_rate,
    }
