-- =============================================================================
-- 070_regional_churn.sql
-- -----------------------------------------------------------------------------
-- Source:     `analytics.clean_customers` (see 010 for the column contract)
--             LEFT JOIN `analytics.telecom_zipcode_population` on zip_code.
--
-- Zip-population load convention (used at verification time; columns are the
-- canonical snake_case names this view reads):
--   CREATE TABLE analytics.telecom_zipcode_population AS
--   SELECT "Zip Code" AS zip_code, Population AS population
--   FROM read_csv_auto('data/raw/telecom_zipcode_population.csv', header = true);
--   -> 1,671 zips. 1,626 of the customers' distinct zips join (full coverage in
--      this dataset; the LEFT JOIN keeps any unmatched customer zip, with
--      population left NULL).
--
-- Denominator rule (all views): churn rate = churned / n, where n EXCLUDES
-- `customer_status = 'Joined'` (454 acquisition rows). Churn is the engineered
-- boolean `churn` = (customer_status = 'Churned').
--
-- Threshold: zips/cities with fewer than 20 existing (non-Joined) customers are
-- suppressed (n >= 20) to avoid noisy small-sample churn rates.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1) v_churn_by_zip — one row per zip_code (with n >= 20), ordered by churn
--    rate descending. `city` and `population` are zip-level attributes
--    (zip_code -> city is 1:1 in this dataset).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_churn_by_zip AS
SELECT
    c.zip_code,
    c.city,
    p.population,
    COUNT(*)                                          AS n,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM analytics.clean_customers AS c
LEFT JOIN analytics.telecom_zipcode_population AS p
    ON c.zip_code = p.zip_code
WHERE c.customer_status != 'Joined'
GROUP BY c.zip_code, c.city, p.population
HAVING COUNT(*) >= 20
ORDER BY churn_rate DESC, churned DESC, c.zip_code;

-- ---------------------------------------------------------------------------
-- 2) v_churn_by_city — one row per city (with n >= 20), ordered by churn rate
--    descending.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_churn_by_city AS
SELECT
    city,
    COUNT(*)                                          AS n,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)            AS churned,
    SUM(CASE WHEN churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM analytics.clean_customers
WHERE customer_status != 'Joined'
GROUP BY city
HAVING COUNT(*) >= 20
ORDER BY churn_rate DESC, churned DESC, city;

-- ---------------------------------------------------------------------------
-- 3) v_churn_by_technology_region — cross-tab of churn rate by internet_type
--    across the top-10 cities by population. City population = Σ population of
--    its distinct zips (zip_code -> city is 1:1, so no double counting).
--    `internet_type IS NULL` (no internet) is labeled '(No internet)'.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_churn_by_technology_region AS
WITH city_pop AS (
    SELECT
        c.city,
        SUM(p.population)                             AS city_population
    FROM (SELECT DISTINCT city, zip_code FROM analytics.clean_customers) AS c
    JOIN analytics.telecom_zipcode_population AS p
        ON c.zip_code = p.zip_code
    GROUP BY c.city
),
top_cities AS (
    SELECT
        city,
        city_population,
        ROW_NUMBER() OVER (ORDER BY city_population DESC, city) AS city_rank
    FROM city_pop
)
SELECT
    COALESCE(c.internet_type, '(No internet)')        AS internet_type,
    tc.city_rank,
    tc.city,
    tc.city_population,
    COUNT(*)                                          AS n,
    SUM(CASE WHEN c.churn THEN 1 ELSE 0 END)          AS churned,
    SUM(CASE WHEN c.churn THEN 1 ELSE 0 END)::DOUBLE
        / NULLIF(COUNT(*), 0)                         AS churn_rate
FROM analytics.clean_customers AS c
JOIN top_cities AS tc
    ON c.city = tc.city
WHERE c.customer_status != 'Joined'
  AND tc.city_rank <= 10
GROUP BY tc.city_rank, tc.city, tc.city_population,
         COALESCE(c.internet_type, '(No internet)')
ORDER BY tc.city_rank, internet_type;
