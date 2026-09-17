from pathlib import Path

import duckdb
import pytest

from src.pipeline import run_pipeline


FIXTURE = Path(__file__).parent / "fixtures" / "sample_customers.csv"


def test_sql_views_reconcile_with_fixture(tmp_path: Path):
    database = tmp_path / "churn.duckdb"
    run_pipeline(
        raw_path=FIXTURE,
        processed_path=tmp_path / "clean.csv",
        database_path=database,
        strict_reference_checks=False,
    )

    with duckdb.connect(str(database), read_only=True) as connection:
        kpis = connection.execute("SELECT * FROM v_kpis").fetchone()
        views = {
            row[0]
            for row in connection.execute(
                "SELECT view_name FROM duckdb_views() WHERE internal = false"
            ).fetchall()
        }

    assert kpis[0] == 5
    assert kpis[1] == 2
    assert kpis[2] == pytest.approx(0.4)
    assert kpis[4] == pytest.approx(90.0)
    assert {"v_kpis", "v_churn_by_segment", "v_churn_reasons", "v_revenue_by_contract", "v_churn_by_city"} <= views
