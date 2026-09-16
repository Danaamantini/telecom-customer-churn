-- =============================================================================
-- 040_cohort_retention.sql
-- -----------------------------------------------------------------------------
-- Grain:      ONE ROW PER (tenure_bin, contract). Retention % by tenure cohort
--             and contract.
-- Source:     `analytics.clean_customers` (see 010 for the column contract).
--
-- Denominator rule: excludes `customer_status = 'Joined'` (acquisition cohort).
-- Churn is the engineered boolean `churn` = (customer_status = 'Churned').
--
-- Metrics:
--   total_customers    COUNT(*) of existing (non-Joined) customers
--   churned_customers  count where churn = TRUE
--   retained_customers total - churned
--   retention_rate     retained / total  (1 - churn rate)
--   churn_rate         churned / total   (0-1 ratio)
--
-- Sorting helper: `cohort_min_tenure` = MIN(tenure_months) within the cohort,
-- giving a label-independent numeric ordering for tenure_bin
-- (0-12 < 13-24 < ... < 60+).
--
-- Retention % = retained customers / total customers over the cohort.
-- =============================================================================

CREATE OR REPLACE VIEW v_cohort_retention AS
SELECT
    tenure_bin,
    MIN(tenure_months)                                                AS cohort_min_tenure,
    contract,
    COUNT(*)                                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)                            AS churned_customers,
    COUNT(*) - SUM(CASE WHEN churn THEN 1 ELSE 0 END)                 AS retained_customers,
    (COUNT(*) - SUM(CASE WHEN churn THEN 1 ELSE 0 END))::DOUBLE
        / NULLIF(COUNT(*), 0)                                         AS retention_rate,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                                         AS churn_rate
FROM analytics.clean_customers
WHERE customer_status != 'Joined'
GROUP BY tenure_bin, contract;
