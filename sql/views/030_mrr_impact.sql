-- =============================================================================
-- 030_mrr_impact.sql
-- -----------------------------------------------------------------------------
-- Grain:      ONE ROW PER (contract, tenure_bin) rollup, including subtotals
--             and a grand total (produced via GROUPING SETS). Rolled-up levels
--             are labeled '(All contracts)' / '(All tenure)'.
-- Source:     `analytics.clean_customers` (see 010 for the column contract).
--
-- Denominator/scope: metrics are computed over churned customers only; the
-- `WHERE customer_status != 'Joined'` filter keeps the 454 acquisition rows out
-- of the contract x tenure rollup (they are never churned and would otherwise
-- inflate the '(All ...)' cells' scope).
--
-- Metrics:
--   churned_customers           count where churn = TRUE
--   mrr_impact                  Σ monthly_charge of churned customers
--   annualized_revenue_at_risk  mrr_impact x 12
--   avg_monthly_charge_churned  mean monthly_charge among churned
--
-- MRR impact of churn = Σ(monthly_charge of churned customers);
-- annualized revenue at risk = MRR impact x 12, per domain-context.md.
-- =============================================================================

CREATE OR REPLACE VIEW v_mrr_impact AS
SELECT
    COALESCE(contract, '(All contracts)')          AS contract,
    COALESCE(tenure_bin, '(All tenure)')           AS tenure_bin,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)         AS churned_customers,
    SUM(CASE WHEN churn THEN monthly_charge
             ELSE 0 END)                           AS mrr_impact,
    SUM(CASE WHEN churn THEN monthly_charge
             ELSE 0 END) * 12                      AS annualized_revenue_at_risk,
    AVG(CASE WHEN churn THEN monthly_charge END)   AS avg_monthly_charge_churned
FROM analytics.clean_customers
WHERE customer_status != 'Joined'
GROUP BY GROUPING SETS (
    (contract, tenure_bin),
    (contract),
    (tenure_bin),
    ()
);
