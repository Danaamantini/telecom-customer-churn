-- =============================================================================
-- 010_customer_360.sql
-- -----------------------------------------------------------------------------
-- Grain:      ONE ROW PER CUSTOMER (customer_id is the natural key).
-- Source:     `analytics.clean_customers` — canonical analysis-ready table
--             produced by `sql/transformations/020_feature_engineering.sql`
--             (DuckDB, `analytics` schema). 38 base columns + 5 engineered.
--
-- Purpose:    Denormalized customer dimension + fact snapshot. This is the
--             single customer-level source for Tableau and all drill-downs.
--             Aggregated views (020–050) are consumed independently, NOT joined
--             back to this view (avoids fan-out / double counting).
--
-- Interface contract (engineered columns on `analytics.clean_customers`):
--   churn               BOOLEAN   TRUE when customer_status = 'Churned'
--   tenure_bin          VARCHAR   0-12 / 13-24 / 25-36 / 37-48 / 49-60 / 60+
--   contract_commitment INTEGER   0 = Month-to-Month, 1 = One Year, 2 = Two Year
--   bundle_count        INTEGER   0-8 (count of internet add-ons = TRUE)
--   is_fiber            BOOLEAN   TRUE when internet_type = 'Fiber Optic'
--
-- Exposed here (in addition to the 43 source columns):
--   is_joined           BOOLEAN   TRUE when customer_status = 'Joined'
--   is_churned          BOOLEAN   alias of churn (customer_status = 'Churned')
--   expected_lifetime_months  months = 1 / contract churn rate
--   clv_estimate        USD       CLV = monthly_charge x gross margin x (1 / rate)
--
-- Assumptions (documented, replaceable):
--   * Gross margin is absent from the dataset. CLV uses GROSS_MARGIN = 0.50.
--   * CLV uses the CONTRACT-LEVEL churn rate as the lifetime horizon, because
--     month-to-month vs. term churn rates differ materially.
--   * Contract churn rate is computed over EXISTING customers only
--     (customer_status != 'Joined'); 'Joined' (454 rows) is a distinct
--     acquisition cohort, not part of the churn denominator.
--   * CLV formula: ARPU x gross margin x (1 / churn rate), per domain-context.md.
-- =============================================================================

CREATE OR REPLACE VIEW v_customer_360 AS
WITH contract_churn AS (
    SELECT
        contract,
        SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
            / NULLIF(COUNT(*), 0) AS churn_rate
    FROM analytics.clean_customers
    WHERE customer_status != 'Joined'
    GROUP BY contract
)
SELECT
    -- Base columns (38)
    c.customer_id,
    c.gender,
    c.age,
    c.married,
    c.num_dependents,
    c.city,
    c.zip_code,
    c.latitude,
    c.longitude,
    c.num_referrals,
    c.tenure_months,
    c.offer,
    c.phone_service,
    c.avg_monthly_long_distance_charges,
    c.multiple_lines,
    c.internet_service,
    c.internet_type,
    c.avg_monthly_gb_download,
    c.online_security,
    c.online_backup,
    c.device_protection_plan,
    c.premium_tech_support,
    c.streaming_tv,
    c.streaming_movies,
    c.streaming_music,
    c.unlimited_data,
    c.contract,
    c.paperless_billing,
    c.payment_method,
    c.monthly_charge,
    c.total_charges,
    c.total_refunds,
    c.total_extra_data_charges,
    c.total_long_distance_charges,
    c.total_revenue,
    c.customer_status,
    c.churn_category,
    c.churn_reason,
    -- Engineered columns (5)
    c.churn,
    c.tenure_bin,
    c.contract_commitment,
    c.bundle_count,
    c.is_fiber,
    -- Derived booleans
    (c.customer_status = 'Joined')                       AS is_joined,
    c.churn                                              AS is_churned,
    -- Expected lifetime in months = 1 / contract churn rate.
    CASE
        WHEN cc.churn_rate IS NULL OR cc.churn_rate = 0 THEN NULL
        ELSE 1.0 / cc.churn_rate
    END                                                  AS expected_lifetime_months,
    -- CLV = ARPU x gross margin x (1 / churn rate).
    -- ARPU is the customer's own monthly_charge at the snapshot.
    c.monthly_charge * 0.50 * (1.0 / NULLIF(cc.churn_rate, 0))
                                                         AS clv_estimate
FROM analytics.clean_customers AS c
LEFT JOIN contract_churn AS cc
    ON c.contract = cc.contract;
