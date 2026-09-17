from pathlib import Path

import pandas as pd
import pytest

from src.pipeline import clean_data, load_raw_data
from src.validation import DataValidationError, validate_processed, validate_raw


FIXTURE = Path(__file__).parent / "fixtures" / "sample_customers.csv"


def test_raw_validation_rejects_duplicate_customer_ids():
    raw = load_raw_data(FIXTURE)
    duplicated = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    with pytest.raises(DataValidationError, match="unique"):
        validate_raw(duplicated)


def test_processed_validation_reports_business_metrics():
    clean = clean_data(load_raw_data(FIXTURE))
    result = validate_processed(clean)

    assert result["rows"] == 6
    assert result["columns"] == 43
    assert result["churned"] == 2
    assert result["joined"] == 1
    assert result["churn_rate"] == pytest.approx(2 / 5)


def test_reference_validation_rejects_incomplete_dataset():
    clean = clean_data(load_raw_data(FIXTURE))
    with pytest.raises(DataValidationError, match="Expected 7043 rows"):
        validate_processed(clean, expected_rows=7043, check_reference_metrics=True)
