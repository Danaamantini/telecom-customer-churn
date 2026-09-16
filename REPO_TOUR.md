# Repository Guide

A tour of the Telecom Customer Churn analytics repository: how it is organized,
what each component does, and how to reproduce and validate the analysis.

---

## 1. Repository layout

```
telecom-customer-churn/
├── README.md                      # project overview & key results
├── PIPELINE.md                    # end-to-end walkthrough + commands
├── REPO_TOUR.md                   # this file
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT
├── .gitignore                     # excludes data/, venv, caches, secrets
│
├── data/                          # ALL gitignored (data files are never tracked)
│   ├── raw/                       # immutable source CSV (see raw/README.md)
│   ├── interim/                   # cleaned/typed intermediates
│   └── processed/                 # feature-engineered, analysis-ready
│
├── notebooks/                     # sequential analysis notebooks (01_eda … 05_storytelling)
├── sql/
│   ├── schemas/                   # canonical DDL (001_raw_staging, 002_clean_typed)
│   ├── transformations/           # DML (010_type_casting, 020_feature_engineering)
│   └── views/                     # analytical BI views (010_customer_360 … 070_regional_churn)
├── src/
│   ├── data/                      # config, ingestion, validation (reusable Python)
│   ├── analysis/                  # analysis helpers
│   └── utils/                     # io helpers
├── tests/                         # pytest suite for src/
└── reports/
    ├── figures/                   # saved charts (PNG)
    ├── insights/                  # data dictionary, findings, recommendations
    └── tableau/                   # data sources, calculated fields, dashboards, .twb
```

---

## 2. What each key component does

### `sql/`
- **schemas/** — canonical table DDL (the typed source of truth).
- **transformations/** — idempotent DML: type casting + feature engineering.
- **views/** — `CREATE OR REPLACE VIEW` analytical layers consumed by Tableau.
  All views read from the canonical table `analytics.clean_customers`.

### `src/`
Reusable Python. Notebooks import from here rather than duplicating logic.
`config.py` resolves `PROJECT_ROOT` from `__file__` (no hardcoded paths).

### `reports/`
Human-facing artifacts: data dictionary, analytical questions, findings,
Tableau specs, and figures.

---

## 3. The canonical data contract

Everything downstream reads from one table: **`analytics.clean_customers`**
(DuckDB, `analytics` schema) — 38 base + 5 engineered columns.

- **Canonical** (38 snake_case source columns): `customer_id`, `gender`, `age`,
  `married`, `num_dependents`, `city`, `zip_code`, `latitude`, `longitude`,
  `num_referrals`, `tenure_months`, `offer`, `phone_service`,
  `avg_monthly_long_distance_charges`, `multiple_lines`, `internet_service`,
  `internet_type`, `avg_monthly_gb_download`, `online_security`,
  `online_backup`, `device_protection_plan`, `premium_tech_support`,
  `streaming_tv`, `streaming_movies`, `streaming_music`, `unlimited_data`,
  `contract`, `paperless_billing`, `payment_method`, `monthly_charge`,
  `total_charges`, `total_refunds`, `total_extra_data_charges`,
  `total_long_distance_charges`, `total_revenue`, `customer_status`,
  `churn_category`, `churn_reason`.
- **Engineered** (5): `churn` (bool = `customer_status='Churned'`),
  `tenure_bin` (6 cohorts), `contract_commitment` (0/1/2), `bundle_count`
  (0–8 add-ons = TRUE), `is_fiber`.

If you change a column name or a bin boundary, update
`sql/transformations/020_feature_engineering.sql` **and** every affected view
**and** the data dictionary in lockstep.

---

## 4. Data-quality checks

1. **Check the contract.** Confirm every view's `FROM` clause points at
   `analytics.clean_customers` and that column names are snake_case (e.g.
   `churn` boolean, `bundle_count` counts add-ons = TRUE).
2. **Check immutability.** `data/` must be gitignored and the raw CSV never
   edited in place.
3. **Check coercion rules.** Yes/No → boolean (empty → FALSE); `internet_type`,
   `churn_category`, `churn_reason` empty → NULL; `avg_monthly_gb_download`
   and `avg_monthly_long_distance_charges` empty → 0; assert no unexpected
   NaNs are introduced.
4. **Check idempotency.** Every SQL object is `CREATE OR REPLACE` (or
   `CREATE TABLE IF NOT EXISTS` + explicit `DELETE`) so re-runs are safe.
5. **Check formula fidelity.** Reconcile every metric against the documented
   formulas (churn rate, MRR impact, CLV) in `reports/insights/data_dictionary.md`.
6. **Check for silent assumptions.** Gross margin `0.50` and contract-level
   churn rate for CLV are assumptions — verify or replace before reporting.

---

## 5. How to validate findings

```bash
# 1. Load the canonical table and eyeball row/column counts.
duckdb churn.db -c "SELECT COUNT(*) AS n, COUNT(DISTINCT customer_id) AS n_distinct FROM analytics.clean_customers"

# 2. Cross-check a headline metric (overall churn rate, excluding Joined) two ways.
duckdb churn.db -c "SELECT * FROM v_churn_metrics WHERE segment='overall'"
duckdb churn.db -c "SELECT AVG(churn::INT) FROM analytics.clean_customers WHERE customer_status != 'Joined'"   # must match

# 3. Validate MRR impact against a manual sum.
duckdb churn.db -c "SELECT SUM(monthly_charge) FROM analytics.clean_customers WHERE churn"

# 4. Spot-check feature engineering.
duckdb churn.db -c "SELECT tenure_months, tenure_bin, bundle_count, is_fiber FROM analytics.clean_customers LIMIT 20"
```

Only trust a finding once it reproduces from the canonical table using the
documented formulas.

---

## 6. Known gaps (do not treat as findings)

- **No support-ticket / interaction log** — "early-tenure friction" analysis
  uses `premium_tech_support` and `churn_reason = 'Attitude of support person'`
  as proxies, not true contact counts.
- **CAC and LTV:CAC** need external finance inputs (S&M spend, new-customer
  counts) — not present in the dataset.
- **Gross margin** is assumed `0.50` for CLV.
- **`monthly_charge`** has 120 negative values (likely credits) — retained and
  flagged, not yet explained.
