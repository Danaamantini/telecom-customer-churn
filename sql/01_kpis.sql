-- One row with the portfolio's headline metrics.
CREATE OR REPLACE VIEW v_kpis AS
SELECT
    COUNT(*) FILTER (WHERE customer_status != 'Joined') AS existing_customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE
        / NULLIF(COUNT(*) FILTER (WHERE customer_status != 'Joined'), 0) AS churn_rate,
    AVG(monthly_charge) FILTER (WHERE customer_status != 'Joined') AS avg_monthly_charge,
    SUM(monthly_charge) FILTER (WHERE churn) AS churned_mrr,
    12 * SUM(monthly_charge) FILTER (WHERE churn) AS annualized_churned_mrr
FROM clean_customers;
