-- ============================================================================
-- 020_feature_engineering.sql
-- Feature engineering — Maven Analytics Telecom Customer Churn
--
-- Engine: DuckDB (default analytical engine for this project)
-- Input : analytics.clean_typed       (from 001->002, or 010)
-- Output: analytics.clean_customers   <-- CANONICAL analysis-ready table that
--         ALL analytical views (sql/views/*) read from.
--
-- The final table carries the 38 canonical columns plus 5 engineered features
-- (43 columns total):
--   churn               BOOLEAN   (customer_status = 'Churned')
--   tenure_bin          VARCHAR   6 cohorts: '0-12','13-24','25-36','37-48',
--                                  '49-60','60+'  (supports the 12/24/36-month
--                                  revenue-leakage windows)
--   contract_commitment INTEGER   ordinal: Month-to-Month=0, One Year=1,
--                                  Two Year=2
--   bundle_count        INTEGER   0-8: count of the 8 internet add-ons = TRUE
--   is_fiber            BOOLEAN   (internet_type = 'Fiber Optic')
--
-- Idempotent: CREATE OR REPLACE TABLE.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE TABLE analytics.clean_customers AS
SELECT
    -- --- base 38 canonical columns ----------------------------------------
    customer_id,
    gender,
    age,
    married,
    num_dependents,
    city,
    zip_code,
    latitude,
    longitude,
    num_referrals,
    tenure_months,
    offer,
    phone_service,
    avg_monthly_long_distance_charges,
    multiple_lines,
    internet_service,
    internet_type,
    avg_monthly_gb_download,
    online_security,
    online_backup,
    device_protection_plan,
    premium_tech_support,
    streaming_tv,
    streaming_movies,
    streaming_music,
    unlimited_data,
    contract,
    paperless_billing,
    payment_method,
    monthly_charge,
    total_charges,
    total_refunds,
    total_extra_data_charges,
    total_long_distance_charges,
    total_revenue,
    customer_status,
    churn_category,
    churn_reason,

    -- --- engineered feature 1: churn flag ---------------------------------
    (customer_status = 'Churned') AS churn,

    -- --- engineered feature 2: tenure_bin (6 cohorts) ----------------------
    CASE
        WHEN tenure_months BETWEEN 0  AND 12 THEN '0-12'
        WHEN tenure_months BETWEEN 13 AND 24 THEN '13-24'
        WHEN tenure_months BETWEEN 25 AND 36 THEN '25-36'
        WHEN tenure_months BETWEEN 37 AND 48 THEN '37-48'
        WHEN tenure_months BETWEEN 49 AND 60 THEN '49-60'
        ELSE '60+'
    END AS tenure_bin,

    -- --- engineered feature 3: contract_commitment (ordinal) --------------
    CASE contract
        WHEN 'Month-to-Month' THEN 0
        WHEN 'One Year'       THEN 1
        WHEN 'Two Year'       THEN 2
        ELSE NULL
    END AS contract_commitment,

    -- --- engineered feature 4: bundle_count (0-8) --------------------------
    (
        online_security::INTEGER +
        online_backup::INTEGER +
        device_protection_plan::INTEGER +
        premium_tech_support::INTEGER +
        streaming_tv::INTEGER +
        streaming_movies::INTEGER +
        streaming_music::INTEGER +
        unlimited_data::INTEGER
    ) AS bundle_count,

    -- --- engineered feature 5: is_fiber ------------------------------------
    -- A customer with no internet (internet_type IS NULL) is NOT on fiber, so
    -- COALESCE forces FALSE rather than letting NULL propagate as a null flag.
    COALESCE(internet_type = 'Fiber Optic', FALSE) AS is_fiber

FROM analytics.clean_typed;
