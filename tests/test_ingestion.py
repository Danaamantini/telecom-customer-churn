"""Unit tests for ``src.data.ingestion.coerce_types`` type/empty-value rules."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data import ingestion


def test_yes_no_bool_coercion():
    df = pd.DataFrame(
        {
            "married": ["Yes", "No", "", "Yes", np.nan, "YES"],
            "phone_service": ["Yes", "No", "No", "", "Yes", np.nan],
        }
    )
    out = ingestion.coerce_types(df)

    assert str(out["married"].dtype) == "bool"
    assert str(out["phone_service"].dtype) == "bool"
    # 'Yes' -> True (case-insensitive), 'No'/empty/NaN -> False.
    assert out["married"].tolist() == [True, False, False, True, False, True]
    assert out["phone_service"].tolist() == [True, False, False, False, True, False]


def test_nullable_varchar_empty_to_null():
    df = pd.DataFrame(
        {
            "internet_type": ["Fiber Optic", "", " ", "Cable", None],
            "churn_category": ["Competitor", "", np.nan, "Price", "Other"],
            "churn_reason": ["Better offer", " ", "", None, "Price too high"],
        }
    )
    out = ingestion.coerce_types(df)

    # Empty / whitespace / NaN / None -> NULL; non-empty strings preserved.
    assert pd.isna(out["internet_type"]).tolist() == [False, True, True, False, True]
    assert out["internet_type"].iloc[0] == "Fiber Optic"
    assert out["internet_type"].iloc[3] == "Cable"

    assert pd.isna(out["churn_category"]).tolist() == [False, True, True, False, False]
    assert out["churn_category"].iloc[0] == "Competitor"

    assert pd.isna(out["churn_reason"]).tolist() == [False, True, True, True, False]
    assert out["churn_reason"].iloc[0] == "Better offer"


def test_empty_gb_download_coerced_to_zero_int():
    df = pd.DataFrame({"avg_monthly_gb_download": ["", "10", "5", np.nan, "20"]})
    out = ingestion.coerce_types(df)

    assert str(out["avg_monthly_gb_download"].dtype) == "int64"
    assert out["avg_monthly_gb_download"].tolist() == [0, 10, 5, 0, 20]


def test_empty_long_distance_coerced_to_zero_float():
    df = pd.DataFrame(
        {"avg_monthly_long_distance_charges": ["", "12.5", np.nan, "0"]}
    )
    out = ingestion.coerce_types(df)

    assert str(out["avg_monthly_long_distance_charges"].dtype) == "float64"
    assert out["avg_monthly_long_distance_charges"].tolist() == [0.0, 12.5, 0.0, 0.0]


def test_negative_monthly_charge_preserved():
    df = pd.DataFrame({"monthly_charge": [-5, "-2.5", 10, 0]})
    out = ingestion.coerce_types(df)

    assert str(out["monthly_charge"].dtype) == "float64"
    assert out["monthly_charge"].tolist() == [-5.0, -2.5, 10.0, 0.0]


def test_numeric_columns_cast_to_numeric_dtype():
    df = pd.DataFrame(
        {
            "age": ["42", "29", "80"],
            "tenure_months": ["1", "72", "13"],
            "monthly_charge": ["63.25", "74.5", "118.75"],
            "total_charges": ["100.0", "200.5", "0"],
            "latitude": ["33.98", "34.05", "37.77"],
        }
    )
    out = ingestion.coerce_types(df)

    assert str(out["age"].dtype) == "int64"
    assert str(out["tenure_months"].dtype) == "int64"
    assert str(out["monthly_charge"].dtype) == "float64"
    assert str(out["total_charges"].dtype) == "float64"
    assert str(out["latitude"].dtype) == "float64"

    assert out["age"].tolist() == [42, 29, 80]
    assert out["latitude"].tolist() == [33.98, 34.05, 37.77]
