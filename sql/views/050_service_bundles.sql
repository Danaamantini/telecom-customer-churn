-- =============================================================================
-- 050_service_bundles.sql
-- -----------------------------------------------------------------------------
-- Source:     `analytics.clean_customers` (see 010 for the column contract).
-- Purpose:    Two churn views over service bundling. Both are standalone and
--             consumed independently (do NOT join back to v_customer_360).
--             Both EXCLUDE `customer_status = 'Joined'` (acquisition cohort).
--
-- 1) v_churn_by_bundle_count
--    Grain: ONE ROW PER bundle_count (engineered count of subscribed internet
--    add-ons, range 0-8). Churn rate by how many add-ons a customer bundles.
--
-- 2) v_churn_by_addon_combo
--    Grain: ONE ROW PER (premium_tech_support x online_security x
--    device_protection_plan) combination (8 total). Each add-on is a BOOLEAN
--    (TRUE = subscribed). `No internet service` rows are already coerced to
--    FALSE at the transformation layer, so an add-on requires internet service.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 2a) Churn rate by bundle count (0-8).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_churn_by_bundle_count AS
SELECT
    bundle_count,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM analytics.clean_customers
WHERE customer_status != 'Joined'
GROUP BY bundle_count;

-- ---------------------------------------------------------------------------
-- 2b) Churn rate by add-on combination (Premium Tech Support x Online Security
--     x Device Protection Plan).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_churn_by_addon_combo AS
SELECT
    premium_tech_support                              AS has_premium_tech_support,
    online_security                                   AS has_online_security,
    device_protection_plan                            AS has_device_protection_plan,
    CASE
        WHEN NOT premium_tech_support
         AND NOT online_security
         AND NOT device_protection_plan
            THEN '(no add-ons)'
        ELSE CONCAT(
            CASE WHEN premium_tech_support THEN 'TechSupport|'      ELSE '' END,
            CASE WHEN online_security      THEN 'OnlineSecurity|'   ELSE '' END,
            CASE WHEN device_protection_plan THEN 'DeviceProtection' ELSE '' END
        )
    END                                               AS combo_label,
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned_customers,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM analytics.clean_customers
WHERE customer_status != 'Joined'
GROUP BY premium_tech_support, online_security, device_protection_plan;
