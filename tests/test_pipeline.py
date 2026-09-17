from pathlib import Path

import pandas as pd

from src.config import PROCESSED_COLUMNS
from src.pipeline import clean_data, load_raw_data, run_pipeline


FIXTURE = Path(__file__).parent / "fixtures" / "sample_customers.csv"


def test_clean_data_contract_and_features():
    raw = load_raw_data(FIXTURE)
    clean = clean_data(raw)

    assert tuple(clean.columns) == PROCESSED_COLUMNS
    assert len(clean) == 6
    assert clean["customer_id"].is_unique
    assert clean["churn"].sum() == 2
    assert clean.loc[clean["customer_id"] == "0001-AAAAA", "bundle_count"].item() == 4
    assert clean.loc[clean["customer_id"] == "0001-AAAAA", "is_fiber"].item()
    assert clean.loc[clean["customer_id"] == "0004-DDDDD", "monthly_charge"].item() == -5.0
    assert pd.isna(clean.loc[clean["customer_id"] == "0004-DDDDD", "internet_type"]).item()


def test_pipeline_writes_csv_and_database(tmp_path):
    output = tmp_path / "clean_customers.csv"
    database = tmp_path / "churn.duckdb"
    result = run_pipeline(
        raw_path=FIXTURE,
        processed_path=output,
        database_path=database,
        strict_reference_checks=False,
    )

    assert output.is_file()
    assert database.is_file()
    assert result["processed"]["rows"] == 6
    assert result["processed"]["churned"] == 2
