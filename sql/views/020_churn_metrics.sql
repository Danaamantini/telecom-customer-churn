-- =============================================================================
-- 020_churn_metrics.sql
-- -----------------------------------------------------------------------------
-- Grain:      ONE ROW PER (segment, segment_value). A stacked rollup across the
--             six segment dimensions below plus a single OVERALL row. This shape
--             is Tableau-friendly (one data source, a `segment` dimension to
--             facet on, no joins needed).
-- Source:     `analytics.clean_customers` (see 010 for the column contract).
--
-- Denominator rule: churn rate = churned / total, where `total` EXCLUDES
-- `customer_status = 'Joined'` (454 acquisition rows). Churn is the engineered
-- boolean `churn` = (customer_status = 'Churned').
--
-- Segments:   contract, internet_type, payment_method, tenure_bin, offer,
--             is_fiber (+ overall).
--
-- Metrics:
--   total_customers   COUNT(*) of existing (non-Joined) customers
--   churned_customers count where churn = TRUE
--   churn_rate        churned / total  (0-1 ratio; format as % in Tableau)
--
-- Churn rate = churned customers / total customers, per domain-context.md.
-- =============================================================================

CREATE OR REPLACE VIEW v_churn_metrics AS
WITH base AS (
    SELECT
        customer_id,
        contract,
        internet_type,
        payment_method,
        tenure_bin,
        offer,
        is_fiber,
        churn
    FROM analytics.clean_customers
    WHERE customer_status != 'Joined'
)
SELECT
    'overall'                                         AS segment,
    'ALL'                                             AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base

UNION ALL

SELECT
    'contract'                                        AS segment,
    contract                                          AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY contract

UNION ALL

SELECT
    'internet_type'                                   AS segment,
    COALESCE(internet_type, '(No internet)')          AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY internet_type

UNION ALL

SELECT
    'payment_method'                                  AS segment,
    payment_method                                    AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY payment_method

UNION ALL

SELECT
    'tenure_bin'                                      AS segment,
    tenure_bin                                        AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY tenure_bin

UNION ALL

SELECT
    'offer'                                           AS segment,
    offer                                             AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY offer

UNION ALL

SELECT
    'is_fiber'                                        AS segment,
    CASE WHEN is_fiber THEN 'Fiber Optic' ELSE 'Non-Fiber' END
                                                      AS segment_value,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM base
GROUP BY CASE WHEN is_fiber THEN 'Fiber Optic' ELSE 'Non-Fiber' END;
