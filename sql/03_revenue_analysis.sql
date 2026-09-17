-- Observed monthly revenue associated with churn, not a discounted forecast.
CREATE OR REPLACE VIEW v_revenue_by_contract AS
SELECT
    contract,
    COUNT(*) FILTER (WHERE customer_status != 'Joined') AS existing_customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE
        / NULLIF(COUNT(*) FILTER (WHERE customer_status != 'Joined'), 0) AS churn_rate,
    SUM(monthly_charge) FILTER (WHERE churn) AS churned_mrr,
    12 * SUM(monthly_charge) FILTER (WHERE churn) AS annualized_churned_mrr
FROM clean_customers
GROUP BY contract;

CREATE OR REPLACE VIEW v_churn_by_city AS
SELECT
    city,
    COUNT(*) AS customers,
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) FILTER (WHERE churn)::DOUBLE / NULLIF(COUNT(*), 0) AS churn_rate
FROM clean_customers
WHERE customer_status != 'Joined'
GROUP BY city
HAVING COUNT(*) >= 20;
