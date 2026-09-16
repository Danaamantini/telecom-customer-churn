"""Central configuration for the Telecom Customer Churn project.

Resolves the repository root from this file's own location (``__file__``) so
that no absolute path is ever hardcoded, keeping the package portable.

This module is the *single source of truth* for the canonical **38-column**
Maven Analytics "Telecom Customer Churn" schema (NOT the 21-column IBM Telco
schema). Downstream code (``ingestion.py``, ``validation.py``, and the SQL
artifacts under ``sql/``) must derive their column contracts from here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Repository root resolution
# ---------------------------------------------------------------------------
# This file lives at <PROJECT_ROOT>/src/data/config.py
_DATA_DIR = Path(__file__).resolve().parent          # .../src/data
_SRC_DIR = _DATA_DIR.parent                           # .../src
PROJECT_ROOT: Path = _SRC_DIR.parent                  # .../telecom-customer-churn

# ---------------------------------------------------------------------------
# Canonical data paths
# ---------------------------------------------------------------------------
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR: Path = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"

# Expected raw dataset filename (see data/raw/README.md)
RAW_CSV_FILENAME: str = "telecom_customer_churn.csv"
RAW_CSV_PATH: Path = RAW_DIR / RAW_CSV_FILENAME

# Companion raw files (geography join + upstream data dictionary)
ZIPCODE_POPULATION_FILENAME: str = "telecom_zipcode_population.csv"
ZIPCODE_POPULATION_PATH: Path = RAW_DIR / ZIPCODE_POPULATION_FILENAME
DATA_DICTIONARY_FILENAME: str = "telecom_data_dictionary.csv"
DATA_DICTIONARY_PATH: Path = RAW_DIR / DATA_DICTIONARY_FILENAME

# Staged (immutable copy of raw) and cleaned/typed artifacts
STAGED_CSV_FILENAME: str = "staged_raw.csv"
STAGED_CSV_PATH: Path = INTERIM_DIR / STAGED_CSV_FILENAME
CLEAN_TYPED_CSV_FILENAME: str = "clean_typed.csv"
CLEAN_TYPED_CSV_PATH: Path = INTERIM_DIR / CLEAN_TYPED_CSV_FILENAME
PROCESSED_CSV_FILENAME: str = "analysis_ready.csv"
PROCESSED_CSV_PATH: Path = PROCESSED_DIR / PROCESSED_CSV_FILENAME

# ---------------------------------------------------------------------------
# Shape expectations (validated against the raw CSV)
# ---------------------------------------------------------------------------
EXPECTED_ROW_COUNT: int = 7043
EXPECTED_COLUMN_COUNT: int = 38

# ---------------------------------------------------------------------------
# Canonical schema (snake_case column -> pandas dtype)
# ---------------------------------------------------------------------------
# Dtypes are pandas ``astype``-compatible strings. The canonical (SQL-flavored)
# type per column is noted in the comment — VARCHAR / INTEGER / DOUBLE / BOOLEAN
# — and mirrored 1:1 in sql/schemas/*.sql.
SCHEMA: Dict[str, str] = {
    # --- identity & demographics -------------------------------------------
    "customer_id": "object",      # VARCHAR  (PK / grain of analysis)
    "gender": "object",           # VARCHAR
    "age": "int64",               # INTEGER
    "married": "bool",            # BOOLEAN
    "num_dependents": "int64",    # INTEGER
    # --- geography ----------------------------------------------------------
    "city": "object",             # VARCHAR
    "zip_code": "int64",          # INTEGER
    "latitude": "float64",        # DOUBLE
    "longitude": "float64",       # DOUBLE
    # --- tenure & acquisition ----------------------------------------------
    "num_referrals": "int64",     # INTEGER
    "tenure_months": "int64",     # INTEGER
    "offer": "object",            # VARCHAR  (keep 'None' literal)
    # --- phone service ------------------------------------------------------
    "phone_service": "bool",      # BOOLEAN
    "avg_monthly_long_distance_charges": "float64",  # DOUBLE  (empty -> 0.0)
    "multiple_lines": "bool",     # BOOLEAN  (empty -> FALSE)
    # --- internet service ---------------------------------------------------
    "internet_service": "bool",   # BOOLEAN
    "internet_type": "object",    # VARCHAR  (DSL/Fiber Optic/Cable/NULL)
    "avg_monthly_gb_download": "int64",              # INTEGER  (empty -> 0)
    "online_security": "bool",    # BOOLEAN
    "online_backup": "bool",      # BOOLEAN
    "device_protection_plan": "bool",  # BOOLEAN
    "premium_tech_support": "bool",    # BOOLEAN
    "streaming_tv": "bool",       # BOOLEAN
    "streaming_movies": "bool",   # BOOLEAN
    "streaming_music": "bool",    # BOOLEAN
    "unlimited_data": "bool",     # BOOLEAN
    # --- contract & billing -------------------------------------------------
    "contract": "object",         # VARCHAR
    "paperless_billing": "bool",  # BOOLEAN
    "payment_method": "object",   # VARCHAR
    # --- revenue ------------------------------------------------------------
    "monthly_charge": "float64",  # DOUBLE  (has 120 negative values — kept)
    "total_charges": "float64",   # DOUBLE
    "total_refunds": "float64",   # DOUBLE
    "total_extra_data_charges": "int64",   # INTEGER
    "total_long_distance_charges": "float64",  # DOUBLE
    "total_revenue": "float64",   # DOUBLE
    # --- target & churn reason ----------------------------------------------
    "customer_status": "object",  # VARCHAR  (Churned/Stayed/Joined)
    "churn_category": "object",   # VARCHAR  (empty -> NULL)
    "churn_reason": "object",     # VARCHAR  (empty -> NULL)
}

# Columns that must exist in a well-formed dataset, in canonical order.
EXPECTED_COLUMNS: Tuple[str, ...] = tuple(SCHEMA.keys())

# ---------------------------------------------------------------------------
# Raw header -> canonical snake_case rename map
# ---------------------------------------------------------------------------
# The raw CSV ships spaced/Title-Case headers. ``load_raw`` renames them to the
# canonical snake_case names below before any coercion is applied.
RAW_COLUMN_MAP: Dict[str, str] = {
    "Customer ID": "customer_id",
    "Gender": "gender",
    "Age": "age",
    "Married": "married",
    "Number of Dependents": "num_dependents",
    "City": "city",
    "Zip Code": "zip_code",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Number of Referrals": "num_referrals",
    "Tenure in Months": "tenure_months",
    "Offer": "offer",
    "Phone Service": "phone_service",
    "Avg Monthly Long Distance Charges": "avg_monthly_long_distance_charges",
    "Multiple Lines": "multiple_lines",
    "Internet Service": "internet_service",
    "Internet Type": "internet_type",
    "Avg Monthly GB Download": "avg_monthly_gb_download",
    "Online Security": "online_security",
    "Online Backup": "online_backup",
    "Device Protection Plan": "device_protection_plan",
    "Premium Tech Support": "premium_tech_support",
    "Streaming TV": "streaming_tv",
    "Streaming Movies": "streaming_movies",
    "Streaming Music": "streaming_music",
    "Unlimited Data": "unlimited_data",
    "Contract": "contract",
    "Paperless Billing": "paperless_billing",
    "Payment Method": "payment_method",
    "Monthly Charge": "monthly_charge",
    "Total Charges": "total_charges",
    "Total Refunds": "total_refunds",
    "Total Extra Data Charges": "total_extra_data_charges",
    "Total Long Distance Charges": "total_long_distance_charges",
    "Total Revenue": "total_revenue",
    "Customer Status": "customer_status",
    "Churn Category": "churn_category",
    "Churn Reason": "churn_reason",
}

# ---------------------------------------------------------------------------
# Coercion groupings (see ingestion.coerce_types + sql/transformations)
# ---------------------------------------------------------------------------
# The 8 internet add-ons whose value counts toward ``bundle_count`` (0-8).
ADDON_COLUMNS: Tuple[str, ...] = (
    "online_security",
    "online_backup",
    "device_protection_plan",
    "premium_tech_support",
    "streaming_tv",
    "streaming_movies",
    "streaming_music",
    "unlimited_data",
)

# Yes/No columns coerced to BOOLEAN ('Yes' -> TRUE, else FALSE, empty -> FALSE).
BOOLEAN_COLUMNS: Tuple[str, ...] = (
    "married",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection_plan",
    "premium_tech_support",
    "streaming_tv",
    "streaming_movies",
    "streaming_music",
    "unlimited_data",
    "paperless_billing",
)

# VARCHAR columns where an empty cell is genuinely missing (empty -> NULL).
NULLABLE_VARCHAR_COLUMNS: Tuple[str, ...] = (
    "internet_type",
    "churn_category",
    "churn_reason",
)

# ---------------------------------------------------------------------------
# Raw null profile (empty cell -> null), *before* coercion
# ---------------------------------------------------------------------------
# These are the only columns that carry empty cells in the raw CSV. The counts
# are asserted by validation.validate_null_profile against the raw DataFrame.
#   - no internet service (1,526 rows): internet_type, avg_monthly_gb_download,
#     and the 8 internet add-ons are empty.
#   - no phone service (682 rows): avg_monthly_long_distance_charges and
#     multiple_lines are empty.
#   - non-churned rows (5,174): churn_category and churn_reason are empty.
EXPECTED_NULLS: Dict[str, int] = {
    "internet_type": 1526,
    "avg_monthly_gb_download": 1526,
    "online_security": 1526,
    "online_backup": 1526,
    "device_protection_plan": 1526,
    "premium_tech_support": 1526,
    "streaming_tv": 1526,
    "streaming_movies": 1526,
    "streaming_music": 1526,
    "unlimited_data": 1526,
    "avg_monthly_long_distance_charges": 682,
    "multiple_lines": 682,
    "churn_category": 5174,
    "churn_reason": 5174,
}
