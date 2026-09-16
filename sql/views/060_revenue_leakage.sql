-- =============================================================================
-- 060_revenue_leakage.sql
-- -----------------------------------------------------------------------------
-- Source:     `analytics.clean_customers` (see 010 for the column contract).
-- Purpose:    Two revenue-leakage views over CHURNED customers only. Both are
--             standalone and consumed independently (do NOT join back to
--             v_customer_360). The `Joined` acquisition cohort (454 rows) is
--             excluded by construction (it is never `churn = TRUE`).
--
-- Key assumption (documented, replaceable):
--   revenue_at_risk(h) = mrr_impact x h  is an UPPER-BOUND estimate of revenue
--   at risk over a horizon of h months. It treats every churned customer's
--   monthly_charge as fully lost for the entire window and therefore IGNORES
--   (a) within-window churn probability (a customer may have churned later
--   anyway) and (b) time discounting. It is a "gross MRR at risk" ceiling, not
--   a discounted net-present-value loss.
--
--   mrr_impact (baseline) = Σ monthly_charge over churned = 137,086.65 (known).
--   lifetime_revenue_collected = Σ total_revenue over churned = actual revenue
--   already recognized from these customers to date.
--
-- Metrics:
--   churned_customers           count where churn = TRUE
--   mrr_impact                  Σ monthly_charge of churned customers
--   revenue_at_risk_12m/24m/36m mrr_impact x 12 / 24 / 36
--   lifetime_revenue_collected  Σ total_revenue of churned customers
--   avg_monthly_charge_churned  mean monthly_charge among churned
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1) v_revenue_leakage — one row per (contract, tenure_bin) with subtotals and
--    a grand total via GROUPING SETS. Rolled-up levels are labeled
--    '(All contracts)' / '(All tenure)'.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_revenue_leakage AS
SELECT
    COALESCE(contract, '(All contracts)')          AS contract,
    COALESCE(tenure_bin, '(All tenure)')           AS tenure_bin,
    COUNT(*)                                       AS churned_customers,
    SUM(monthly_charge)                            AS mrr_impact,
    SUM(monthly_charge) * 12                       AS revenue_at_risk_12m,
    SUM(monthly_charge) * 24                       AS revenue_at_risk_24m,
    SUM(monthly_charge) * 36                       AS revenue_at_risk_36m,
    SUM(total_revenue)                             AS lifetime_revenue_collected
FROM analytics.clean_customers
WHERE churn = TRUE
GROUP BY GROUPING SETS (
    (contract, tenure_bin),
    (contract),
    (tenure_bin),
    ()
);

-- ---------------------------------------------------------------------------
-- 2) v_revenue_leakage_by_contract — one row per contract (no rollups).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_revenue_leakage_by_contract AS
SELECT
    contract,
    COUNT(*)                                       AS churned_customers,
    SUM(monthly_charge)                            AS mrr_impact,
    SUM(monthly_charge) * 12                       AS revenue_at_risk_12m,
    SUM(monthly_charge) * 24                       AS revenue_at_risk_24m,
    SUM(monthly_charge) * 36                       AS revenue_at_risk_36m,
    AVG(monthly_charge)                            AS avg_monthly_charge_churned
FROM analytics.clean_customers
WHERE churn = TRUE
GROUP BY contract;
