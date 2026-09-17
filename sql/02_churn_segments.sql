-- Tableau-friendly long table: one row per segment and value.
CREATE OR REPLACE VIEW v_churn_by_segment AS
WITH existing AS (
    SELECT * FROM clean_customers WHERE customer_status != 'Joined'
), segments AS (
    SELECT 'contract' AS segment, contract AS segment_value, churn FROM existing
    UNION ALL
    SELECT 'internet_type', COALESCE(internet_type, 'No internet'), churn FROM existing
    UNION ALL
    SELECT 'payment_method', payment_method, churn FROM existing
    UNION ALL
    SELECT 'tenure_group', tenure_group, churn FROM existing
    UNION ALL
    SELECT 'offer', offer, churn FROM existing
    UNION ALL
    SELECT 'bundle_count', CAST(bundle_count AS VARCHAR), churn FROM existing
)
SELECT
    segment,
    segment_value,
    COUNT(*) AS customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE / NULLIF(COUNT(*), 0) AS churn_rate
FROM segments
GROUP BY segment, segment_value;

CREATE OR REPLACE VIEW v_churn_reasons AS
SELECT churn_category, churn_reason, COUNT(*) AS churned_customers
FROM clean_customers
WHERE churn
GROUP BY churn_category, churn_reason;
