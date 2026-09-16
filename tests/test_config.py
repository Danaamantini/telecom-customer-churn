"""Unit tests for ``src.data.config`` — the canonical 38-column contract."""

from __future__ import annotations

from pathlib import Path

from src.data import config


def test_project_root_is_repo_root():
    root = config.PROJECT_ROOT
    assert isinstance(root, Path)
    assert root.is_dir()
    # The repo root is the directory that contains ``src/`` and ``data/``.
    assert (root / "src").is_dir()
    assert (root / "data").is_dir()
    # This config file itself must live under <root>/src/data/.
    assert (root / "src" / "data" / "config.py").is_file()


def test_schema_has_exactly_38_keys():
    assert isinstance(config.SCHEMA, dict)
    assert len(config.SCHEMA) == 38


def test_schema_contains_canonical_snake_case_columns():
    required = {
        "customer_id", "gender", "age", "married", "num_dependents",
        "city", "zip_code", "latitude", "longitude",
        "num_referrals", "tenure_months", "offer",
        "phone_service", "avg_monthly_long_distance_charges", "multiple_lines",
        "internet_service", "internet_type", "avg_monthly_gb_download",
        "online_security", "online_backup", "device_protection_plan",
        "premium_tech_support", "streaming_tv", "streaming_movies",
        "streaming_music", "unlimited_data",
        "contract", "paperless_billing", "payment_method",
        "monthly_charge", "total_charges", "total_refunds",
        "total_extra_data_charges", "total_long_distance_charges", "total_revenue",
        "customer_status", "churn_category", "churn_reason",
    }
    assert required <= set(config.SCHEMA.keys())


def test_expected_columns_matches_schema_keys():
    # EXPECTED_COLUMNS is exposed as the ordered tuple of schema keys.
    assert list(config.EXPECTED_COLUMNS) == list(config.SCHEMA.keys())
    assert len(config.EXPECTED_COLUMNS) == 38
    assert set(config.EXPECTED_COLUMNS) == set(config.SCHEMA.keys())


def test_raw_csv_path_points_under_data_raw():
    assert config.RAW_CSV_PATH.parent == config.PROJECT_ROOT / "data" / "raw"
    assert "data" in config.RAW_CSV_PATH.parts
    assert "raw" in config.RAW_CSV_PATH.parts
