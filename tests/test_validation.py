"""Unit tests for ``src.data.validation`` schema/shape checks."""

from __future__ import annotations

import pandas as pd

from src.data import config, validation


def _make_df(columns, nrows=2):
    """Build a tiny DataFrame with the given columns (order-preserving)."""
    return pd.DataFrame({c: range(nrows) for c in columns})


def test_validate_shape_detects_wrong_column_count():
    df = _make_df(["a", "b", "c"], nrows=2)
    report = validation.validate_shape(df, expected_rows=2, expected_cols=38)

    assert report["check"] == "shape"
    assert report["passed"] is False
    assert report["actual"]["cols"] == 3
    assert report["actual"]["rows"] == 2
    assert report["expected"]["cols"] == 38


def test_validate_columns_detects_missing_required_columns():
    df = _make_df(["customer_id", "age", "unexpected_col"], nrows=2)
    report = validation.validate_columns(df)

    assert report["passed"] is False
    assert "monthly_charge" in report["missing"]
    assert "unexpected_col" in report["extra"]


def test_validate_dataset_returns_report_and_flags_shape_columns():
    df = _make_df(["customer_id", "age"], nrows=2)
    report = validation.validate_dataset(df, expected_rows=2, expected_cols=38)

    assert isinstance(report, dict)
    assert "passed" in report
    assert "results" in report
    assert report["passed"] is False

    checks = {r["check"]: r for r in report["results"]}
    assert checks["shape"]["passed"] is False
    assert checks["columns"]["passed"] is False
    assert checks["columns"]["missing"]


def test_correctly_shaped_38_col_df_passes_shape_and_columns():
    df = _make_df(config.EXPECTED_COLUMNS, nrows=2)

    shape = validation.validate_shape(df, expected_rows=2, expected_cols=38)
    assert shape["passed"] is True

    cols = validation.validate_columns(df)
    assert cols["passed"] is True
    assert cols["missing"] == []
    assert cols["extra"] == []
    assert cols["in_order"] is True
