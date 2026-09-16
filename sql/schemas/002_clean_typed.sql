-- ============================================================================
-- 002_clean_typed.sql
-- Cleaned & typed layer — Maven Analytics Telecom Customer Churn
--
-- Engine: DuckDB (default analytical engine for this project)
-- Purpose: apply the canonical coercion rules to produce the typed, analysis-
--          ready table from the lossless string staging table. This is the
--          single source of truth that feature engineering (020) reads from.
--
-- Input : staging.raw_customer_churn   (from 001_raw_staging.sql)
-- Output: analytics.clean_typed         (38 canonical typed columns)
--
-- Coercion rules (see reports/insights/data_dictionary.md + config.py):
--   BOOLEAN ('Yes' -> TRUE, else FALSE, empty -> FALSE):
--     married, phone_service, multiple_lines, internet_service, the 8 internet
--     add-ons, paperless_billing.
--   internet_type          VARCHAR  keep DSL / Fiber Optic / Cable; empty -> NULL
--   avg_monthly_gb_download INTEGER  empty -> 0
--   avg_monthly_long_distance_charges DOUBLE empty -> 0.0
--   churn_category / churn_reason VARCHAR empty -> NULL
--   offer                  VARCHAR  keep 'None' literal (no change)
--   monthly_charge         DOUBLE   keeps 120 negative values (flagged for EDA)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- ----------------------------------------------------------------------------
-- Cleaned / typed table (idempotent)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE TABLE analytics.clean_typed AS
SELECT
    customer_id,
    gender,
    CAST(age AS INTEGER)                                             AS age,
    (COALESCE(married, 'No') = 'Yes')                                AS married,
    CAST(num_dependents AS INTEGER)                                  AS num_dependents,
    city,
    CAST(zip_code AS INTEGER)                                        AS zip_code,
    CAST(latitude AS DOUBLE)                                         AS latitude,
    CAST(longitude AS DOUBLE)                                        AS longitude,
    CAST(num_referrals AS INTEGER)                                   AS num_referrals,
    CAST(tenure_months AS INTEGER)                                   AS tenure_months,
    offer,
    (COALESCE(phone_service, 'No') = 'Yes')                          AS phone_service,
    COALESCE(CAST(avg_monthly_long_distance_charges AS DOUBLE), 0.0) AS avg_monthly_long_distance_charges,
    (COALESCE(multiple_lines, 'No') = 'Yes')                         AS multiple_lines,
    (COALESCE(internet_service, 'No') = 'Yes')                       AS internet_service,
    NULLIF(internet_type, '')                                        AS internet_type,
    COALESCE(CAST(avg_monthly_gb_download AS INTEGER), 0)            AS avg_monthly_gb_download,
    (COALESCE(online_security, 'No') = 'Yes')                        AS online_security,
    (COALESCE(online_backup, 'No') = 'Yes')                          AS online_backup,
    (COALESCE(device_protection_plan, 'No') = 'Yes')                 AS device_protection_plan,
    (COALESCE(premium_tech_support, 'No') = 'Yes')                   AS premium_tech_support,
    (COALESCE(streaming_tv, 'No') = 'Yes')                           AS streaming_tv,
    (COALESCE(streaming_movies, 'No') = 'Yes')                       AS streaming_movies,
    (COALESCE(streaming_music, 'No') = 'Yes')                        AS streaming_music,
    (COALESCE(unlimited_data, 'No') = 'Yes')                         AS unlimited_data,
    contract,
    (COALESCE(paperless_billing, 'No') = 'Yes')                      AS paperless_billing,
    payment_method,
    CAST(monthly_charge AS DOUBLE)                                   AS monthly_charge,
    CAST(total_charges AS DOUBLE)                                    AS total_charges,
    CAST(total_refunds AS DOUBLE)                                    AS total_refunds,
    CAST(total_extra_data_charges AS INTEGER)                        AS total_extra_data_charges,
    CAST(total_long_distance_charges AS DOUBLE)                      AS total_long_distance_charges,
    CAST(total_revenue AS DOUBLE)                                    AS total_revenue,
    customer_status,
    NULLIF(churn_category, '')                                       AS churn_category,
    NULLIF(churn_reason, '')                                         AS churn_reason
FROM staging.raw_customer_churn;
