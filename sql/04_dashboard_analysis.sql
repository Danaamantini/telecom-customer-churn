-- Reproduce the executive Tableau dashboard and its recommended test cohorts.

CREATE OR REPLACE VIEW v_dashboard_kpis AS
WITH base AS (
    SELECT
        COUNT(*) FILTER (WHERE customer_status != 'Joined') AS existing_customers,
        COUNT(*) FILTER (WHERE churn) AS churned_customers,
        SUM(monthly_charge) FILTER (WHERE customer_status != 'Joined') AS existing_mrr,
        SUM(monthly_charge) FILTER (WHERE churn) AS churned_mrr,
        COUNT(*) FILTER (
            WHERE churn AND contract = 'Month-to-Month'
        ) AS m2m_churned_customers,
        SUM(monthly_charge) FILTER (
            WHERE churn AND monthly_charge >= 90.40
        ) AS high_value_churned_mrr
    FROM clean_customers
)
SELECT
    *,
    churned_customers::DOUBLE / NULLIF(existing_customers, 0) AS churn_rate,
    churned_mrr / NULLIF(existing_mrr, 0) AS churned_mrr_share,
    m2m_churned_customers::DOUBLE
        / NULLIF(churned_customers, 0) AS m2m_share_of_churn,
    high_value_churned_mrr / NULLIF(churned_mrr, 0) AS high_value_revenue_exposure
FROM base;

CREATE OR REPLACE VIEW v_priority_segment AS
WITH priority AS (
    SELECT *
    FROM clean_customers
    WHERE customer_status != 'Joined'
      AND contract = 'Month-to-Month'
      AND internet_type = 'Fiber Optic'
      AND tenure_months BETWEEN 4 AND 24
)
SELECT
    COUNT(*) AS existing_customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE / NULLIF(COUNT(*), 0) AS churn_rate,
    SUM(monthly_charge) FILTER (WHERE churn) AS churned_mrr
FROM priority;

CREATE OR REPLACE VIEW v_priority_churn_drivers AS
WITH priority_churn AS (
    SELECT
        CASE
            WHEN churn_category = 'Competitor' THEN 'Competitor'
            WHEN churn_category IN ('Dissatisfaction', 'Attitude')
                THEN 'Service Experience'
            WHEN churn_category = 'Price' THEN 'Price'
            ELSE 'Other'
        END AS driver_group
    FROM clean_customers
    WHERE churn
      AND contract = 'Month-to-Month'
      AND internet_type = 'Fiber Optic'
      AND tenure_months BETWEEN 4 AND 24
), grouped AS (
    SELECT driver_group, COUNT(*) AS churned_customers
    FROM priority_churn
    GROUP BY driver_group
)
SELECT
    driver_group,
    churned_customers,
    churned_customers::DOUBLE
        / NULLIF(SUM(churned_customers) OVER (), 0) AS share_of_priority_churn
FROM grouped;

CREATE OR REPLACE VIEW v_retention_test_candidates AS
WITH offer_e AS (
    SELECT
        'Redesign Offer E' AS test_name,
        COUNT(*) FILTER (
            WHERE customer_status != 'Joined'
        ) AS historical_existing,
        COUNT(*) FILTER (WHERE churn) AS historical_churned,
        COUNT(*) FILTER (
            WHERE customer_status != 'Churned'
        ) AS active_customers,
        SUM(monthly_charge) FILTER (
            WHERE customer_status != 'Churned'
        ) AS active_mrr
    FROM clean_customers
    WHERE offer = 'Offer E'
), high_value_m2m AS (
    SELECT
        'Protect high-value Month-to-Month' AS test_name,
        NULL::BIGINT AS historical_existing,
        NULL::BIGINT AS historical_churned,
        COUNT(*) AS active_customers,
        SUM(monthly_charge) AS active_mrr
    FROM clean_customers
    WHERE customer_status = 'Stayed'
      AND contract = 'Month-to-Month'
      AND monthly_charge >= 90.40
), fiber_support AS (
    SELECT
        'Test proactive Fiber support' AS test_name,
        NULL::BIGINT AS historical_existing,
        COUNT(*) FILTER (WHERE churn) AS historical_churned,
        COUNT(*) FILTER (
            WHERE customer_status = 'Stayed'
        ) AS active_customers,
        SUM(monthly_charge) FILTER (
            WHERE customer_status = 'Stayed'
        ) AS active_mrr
    FROM clean_customers
    WHERE contract = 'Month-to-Month'
      AND internet_type = 'Fiber Optic'
      AND tenure_months BETWEEN 4 AND 24
      AND NOT premium_tech_support
)
SELECT
    *,
    historical_churned::DOUBLE
        / NULLIF(historical_existing, 0) AS historical_churn_rate
FROM offer_e
UNION ALL
SELECT
    *,
    NULL::DOUBLE AS historical_churn_rate
FROM high_value_m2m
UNION ALL
SELECT
    *,
    NULL::DOUBLE AS historical_churn_rate
FROM fiber_support;

CREATE OR REPLACE VIEW v_zip3_diagnostic AS
WITH existing AS (
    SELECT
        LEFT(CAST(zip_code AS VARCHAR), 3) AS zip3,
        *
    FROM clean_customers
    WHERE customer_status != 'Joined'
)
SELECT
    zip3,
    COUNT(*) AS existing_customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE / NULLIF(COUNT(*), 0) AS churn_rate,
    COUNT(*) FILTER (
        WHERE churn AND churn_category = 'Competitor'
    ) AS competitor_churns,
    COUNT(*) FILTER (
        WHERE churn AND LOWER(churn_reason) LIKE '%offer%'
    ) AS offer_related_churns
FROM existing
GROUP BY zip3;
