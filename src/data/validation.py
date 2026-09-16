"""Schema & hygiene validation for the churn dataset.

Every function returns structured, machine-checkable results rather than
printing, so they can be wired into tests or CI later.

Two validation stages are supported:

* **Raw** (pre-coercion) — ``validate_shape``, ``validate_columns`` and
  ``validate_null_profile`` operate on the raw DataFrame returned by
  ``ingestion.load_raw`` (empty cells -> NaN, spaced headers already renamed).
* **Coerced** (post-coercion) — ``validate_dtypes`` checks the canonical dtype
  profile against the output of ``ingestion.coerce_types``.

This split exists because the empty-value coercion rules resolve most raw nulls
(e.g. the 8 internet add-ons empty -> FALSE), so the *raw* null profile and the
*coerced* dtype profile describe different stages of the pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from src.data.config import (
    EXPECTED_COLUMNS,
    EXPECTED_NULLS,
    SCHEMA,
)


def validate_shape(
    df: pd.DataFrame,
    expected_rows: int,
    expected_cols: int,
) -> Dict[str, Any]:
    """Assert the DataFrame has the expected row and column counts."""
    actual_rows, actual_cols = df.shape
    ok = actual_rows == expected_rows and actual_cols == expected_cols
    return {
        "check": "shape",
        "passed": ok,
        "expected": {"rows": expected_rows, "cols": expected_cols},
        "actual": {"rows": actual_rows, "cols": actual_cols},
    }


def validate_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Assert the DataFrame contains exactly the canonical columns (in order)."""
    actual = list(df.columns)
    expected = list(EXPECTED_COLUMNS)
    missing = [c for c in expected if c not in actual]
    extra = [c for c in actual if c not in expected]
    ok = not missing and not extra and actual == expected
    return {
        "check": "columns",
        "passed": ok,
        "expected": expected,
        "actual": actual,
        "missing": missing,
        "extra": extra,
        "in_order": actual == expected,
    }


def validate_dtypes(df: pd.DataFrame) -> Dict[str, Any]:
    """Check each column against the canonical dtype profile.

    Run this against the **coerced** DataFrame (``ingestion.coerce_types``), not
    the raw one — the raw file stores Yes/No flags and empty cells as strings.
    """
    mismatches: List[Dict[str, str]] = []
    for col, expected in SCHEMA.items():
        if col not in df.columns:
            mismatches.append({"column": col, "expected": expected, "actual": "MISSING"})
            continue
        actual = str(df[col].dtype)
        if actual != expected:
            mismatches.append(
                {"column": col, "expected": expected, "actual": actual}
            )
    return {
        "check": "dtypes",
        "passed": not mismatches,
        "mismatches": mismatches,
        "profile": {c: str(df[c].dtype) for c in df.columns},
    }


def validate_null_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Assert the *raw* null profile matches ``EXPECTED_NULLS``.

    Run this against the raw DataFrame (empty cells -> NaN). Only the 14
    columns in ``EXPECTED_NULLS`` may contain nulls, and each must match its
    expected count exactly. Any null in a column not listed, or a count
    mismatch, is reported as a failure.
    """
    null_counts = {col: int(df[col].isna().sum()) for col in df.columns}

    mismatches: List[Dict[str, Any]] = []
    for col, expected in EXPECTED_NULLS.items():
        actual = null_counts.get(col, 0)
        if actual != expected:
            mismatches.append(
                {"column": col, "expected": expected, "actual": actual}
            )

    unexpected = {
        col: cnt
        for col, cnt in null_counts.items()
        if cnt > 0 and col not in EXPECTED_NULLS
    }

    passed = not mismatches and not unexpected
    return {
        "check": "null_profile",
        "passed": passed,
        "null_counts": null_counts,
        "expected_nulls": dict(EXPECTED_NULLS),
        "mismatches": mismatches,
        "unexpected_nulls": unexpected,
    }


def validate_raw(
    df: pd.DataFrame,
    expected_rows: int,
    expected_cols: int,
) -> Dict[str, Any]:
    """Run the raw-stage battery: shape, columns, and null profile.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from ``ingestion.load_raw``.
    expected_rows, expected_cols : int
        Canonical shape (7,043 x 38).
    """
    results = [
        validate_shape(df, expected_rows, expected_cols),
        validate_columns(df),
        validate_null_profile(df),
    ]
    return {
        "passed": all(r["passed"] for r in results),
        "n_checks": len(results),
        "n_passed": sum(1 for r in results if r["passed"]),
        "results": results,
    }


def validate_dataset(
    df: pd.DataFrame,
    expected_rows: int,
    expected_cols: int,
) -> Dict[str, Any]:
    """Run the full validation battery and return a structured report.

    This is the raw-stage battery plus the dtype check. The dtype check only
    passes when ``df`` is the **coerced** frame (Yes/No -> bool, empty -> typed
    default); to validate a raw frame, use :func:`validate_raw` instead.
    """
    results = [
        validate_shape(df, expected_rows, expected_cols),
        validate_columns(df),
        validate_dtypes(df),
        validate_null_profile(df),
    ]
    return {
        "passed": all(r["passed"] for r in results),
        "n_checks": len(results),
        "n_passed": sum(1 for r in results if r["passed"]),
        "results": results,
    }
