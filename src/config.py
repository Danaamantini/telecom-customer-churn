"""Project configuration and the canonical customer schema."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DATA_PATH = RAW_DIR / "telecom_customer_churn.csv"
PROCESSED_DATA_PATH = PROCESSED_DIR / "clean_customers.csv"
DATABASE_PATH = PROCESSED_DIR / "churn.duckdb"
SQL_DIR = PROJECT_ROOT / "sql"

EXPECTED_FULL_ROWS = 7043
EXPECTED_CHURNED = 1869
EXPECTED_JOINED = 454

RAW_COLUMN_MAP = {
    "Customer ID": "customer_id", "Gender": "gender", "Age": "age",
    "Married": "married", "Number of Dependents": "num_dependents",
    "City": "city", "Zip Code": "zip_code", "Latitude": "latitude",
    "Longitude": "longitude", "Number of Referrals": "num_referrals",
    "Tenure in Months": "tenure_months", "Offer": "offer",
    "Phone Service": "phone_service",
    "Avg Monthly Long Distance Charges": "avg_monthly_long_distance_charges",
    "Multiple Lines": "multiple_lines", "Internet Service": "internet_service",
    "Internet Type": "internet_type",
    "Avg Monthly GB Download": "avg_monthly_gb_download",
    "Online Security": "online_security", "Online Backup": "online_backup",
    "Device Protection Plan": "device_protection_plan",
    "Premium Tech Support": "premium_tech_support",
    "Streaming TV": "streaming_tv", "Streaming Movies": "streaming_movies",
    "Streaming Music": "streaming_music", "Unlimited Data": "unlimited_data",
    "Contract": "contract", "Paperless Billing": "paperless_billing",
    "Payment Method": "payment_method", "Monthly Charge": "monthly_charge",
    "Total Charges": "total_charges", "Total Refunds": "total_refunds",
    "Total Extra Data Charges": "total_extra_data_charges",
    "Total Long Distance Charges": "total_long_distance_charges",
    "Total Revenue": "total_revenue", "Customer Status": "customer_status",
    "Churn Category": "churn_category", "Churn Reason": "churn_reason",
}

BASE_COLUMNS = tuple(RAW_COLUMN_MAP.values())

BOOLEAN_COLUMNS = (
    "married", "phone_service", "multiple_lines", "internet_service",
    "online_security", "online_backup", "device_protection_plan",
    "premium_tech_support", "streaming_tv", "streaming_movies",
    "streaming_music", "unlimited_data", "paperless_billing",
)

ADDON_COLUMNS = (
    "online_security", "online_backup", "device_protection_plan",
    "premium_tech_support", "streaming_tv", "streaming_movies",
    "streaming_music", "unlimited_data",
)

INTEGER_COLUMNS = (
    "age", "num_dependents", "zip_code", "num_referrals", "tenure_months",
    "avg_monthly_gb_download", "total_extra_data_charges",
)

FLOAT_COLUMNS = (
    "latitude", "longitude", "avg_monthly_long_distance_charges",
    "monthly_charge", "total_charges", "total_refunds",
    "total_long_distance_charges", "total_revenue",
)

NULLABLE_TEXT_COLUMNS = ("internet_type", "churn_category", "churn_reason")
ENGINEERED_COLUMNS = (
    "churn", "tenure_group", "contract_commitment", "bundle_count", "is_fiber",
)
PROCESSED_COLUMNS = BASE_COLUMNS + ENGINEERED_COLUMNS
