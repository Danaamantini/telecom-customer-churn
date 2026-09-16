-- ============================================================================
-- 001_raw_staging.sql
-- Raw staging layer — Maven Analytics Telecom Customer Churn
--
-- Engine: DuckDB (default analytical engine for this project)
-- Purpose: land the raw 38-column CSV into a lossless staging table with the
--          canonical snake_case column names. Raw data is NEVER modified on
--          disk; this is a pure load that renames headers and preserves every
--          value (empty cells surface as NULL), leaving all coercion to
--          002_clean_typed.sql.
--
-- Input : data/raw/telecom_customer_churn.csv  (7,043 rows x 38 cols)
-- Output: staging.raw_customer_churn            (38 snake_case cols, all VARCHAR)
--
-- Lossless by construction: every column is read as VARCHAR and nothing is
-- dropped, imputed, or re-typed here. Empty upstream cells become NULL.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS staging;

-- ----------------------------------------------------------------------------
-- Idempotent lossless staging table (snake_case, all VARCHAR)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE TABLE staging.raw_customer_churn AS
SELECT * FROM read_csv(
    'data/raw/telecom_customer_churn.csv',
    header = true,
    columns = {
        'customer_id':                      'VARCHAR',
        'gender':                           'VARCHAR',
        'age':                              'VARCHAR',
        'married':                          'VARCHAR',
        'num_dependents':                   'VARCHAR',
        'city':                             'VARCHAR',
        'zip_code':                         'VARCHAR',
        'latitude':                         'VARCHAR',
        'longitude':                        'VARCHAR',
        'num_referrals':                    'VARCHAR',
        'tenure_months':                    'VARCHAR',
        'offer':                            'VARCHAR',
        'phone_service':                    'VARCHAR',
        'avg_monthly_long_distance_charges':'VARCHAR',
        'multiple_lines':                   'VARCHAR',
        'internet_service':                 'VARCHAR',
        'internet_type':                    'VARCHAR',
        'avg_monthly_gb_download':          'VARCHAR',
        'online_security':                  'VARCHAR',
        'online_backup':                    'VARCHAR',
        'device_protection_plan':           'VARCHAR',
        'premium_tech_support':             'VARCHAR',
        'streaming_tv':                     'VARCHAR',
        'streaming_movies':                 'VARCHAR',
        'streaming_music':                  'VARCHAR',
        'unlimited_data':                   'VARCHAR',
        'contract':                         'VARCHAR',
        'paperless_billing':                'VARCHAR',
        'payment_method':                   'VARCHAR',
        'monthly_charge':                   'VARCHAR',
        'total_charges':                    'VARCHAR',
        'total_refunds':                    'VARCHAR',
        'total_extra_data_charges':         'VARCHAR',
        'total_long_distance_charges':      'VARCHAR',
        'total_revenue':                    'VARCHAR',
        'customer_status':                  'VARCHAR',
        'churn_category':                   'VARCHAR',
        'churn_reason':                     'VARCHAR'
    }
);
