# PIPELINE.md — End-to-End Execution Walkthrough

Telecom Customer Churn analytics pipeline. This document explains the five
operational stages, the data transformations, the methodological choices, and
the exact commands to reproduce every artifact.

> **Dataset:** Maven Analytics "Telecom Customer Churn" — **7,043 rows × 38
> columns** (California residential customers, end of Q2 2022), staged at
> `data/raw/telecom_customer_churn.csv` (plus
> `telecom_zipcode_population.csv` and `telecom_data_dictionary.csv`).

---

## 1. The five stages

| Stage | Name | Key output |
|-------|------|------------|
| 1 | Problem Definition & KPI Scoping | Scaffold, canonical schema, extended questions, blueprint docs |
| 2 | Exploratory Data Analysis | Hygiene report, distributions, correlations, hypothesis tests |
| 3 | Transformation & SQL Layering | Typed/feature-engineered tables, analytical BI views |
| 4 | In-depth Analysis | Cohorts, revenue leakage, feature importance, tipping points |
| 5 | Closing & Data Storytelling | Tableau specs, dashboard wireframes, recommendations |

> **Pipeline status:** all five stages complete. Final deliverables:
> `reports/insights/recommendations.md` + `reports/tableau/*` (data sources,
> calculated fields, dashboard wireframes).

---

## 2. Data flow & transformations

```
data/raw/            immutable source CSV (never modified)
   │  stage_raw()  (byte-for-byte copy, src/data/ingestion.py)
   ▼
data/interim/        cleaned/typed intermediates (coerced booleans + nulls)
   │  feature engineering (sql/transformations/020_feature_engineering.sql)
   ▼
data/processed/      analysis-ready artifacts
   │  analytical views (sql/views/*.sql)
   ▼
reports/ + Tableau   figures, insights, dashboard specs
```

### Key transformations

1. **Type casting** (`sql/transformations/010_type_casting.sql` /
   `src/data/ingestion.py::coerce_types`) — the raw file uses spaced
   Title-Case headers; they are renamed to snake_case and coerced:
   - Yes/No flags → BOOLEAN (`'Yes'`→TRUE, else FALSE; empty→FALSE): `married`,
     `phone_service`, `multiple_lines`, `internet_service`, the 8 internet
     add-ons, `paperless_billing`.
   - `internet_type` empty → NULL; `churn_category`/`churn_reason` empty → NULL.
   - `avg_monthly_gb_download` empty → 0; `avg_monthly_long_distance_charges`
     empty → 0.0.
   - Numeric types applied to `age`, `num_dependents`, `num_referrals`,
     `tenure_months`, `zip_code`, monetary/coordinate columns.
   - `monthly_charge` keeps its 120 negative values (flagged for EDA, never
     dropped silently).

2. **Feature engineering** (`sql/transformations/020_feature_engineering.sql`):
   - `churn` — boolean = `customer_status = 'Churned'`.
   - `tenure_bin` — 6 cohorts (`0-12`, `13-24`, `25-36`, `37-48`, `49-60`,
     `60+`), chosen to support the 12/24/36-month revenue-leakage windows.
   - `contract_commitment` — ordinal `0`/`1`/`2` (Month-to-Month / One year /
     Two year).
   - `bundle_count` — count of the **8 internet add-ons** = TRUE
     (`online_security`, `online_backup`, `device_protection_plan`,
     `premium_tech_support`, `streaming_tv`, `streaming_movies`,
     `streaming_music`, `unlimited_data`), range 0–8.
   - `is_fiber` — `internet_type = 'Fiber Optic'`.

### Canonical contract (single source of truth)

The analytical views read from **`analytics.clean_customers`** (DuckDB,
`analytics` schema) — 38 base columns + 5 engineered columns, with `churn`
(boolean) as the target. Every view documents its own grain in a header
comment. `Joined` customers are a distinct acquisition cohort and are excluded
from churn-rate denominators.

---

## 3. Methodological choices (summary)

- **Raw data immutability** — raw CSV is never edited; staging is a pure,
  lossless typed load.
- **Churn is a point-in-time snapshot** — `Customer Status` at end of Q2 2022
  is treated as a snapshot, not a longitudinal event stream.
- **Empty-cell coercion** — empty fields for no-internet / no-phone /
  non-churned rows are coerced to NULL / 0 / FALSE (never dropped), preserving
  the full 7,043-row grain.
- **Negative `monthly_charge`** — 120 rows have negative values (likely
  credits); retained and flagged for EDA rather than silently dropped.
- **CLV** — `ARPU × gross margin × (1 / churn rate)`, with a default gross
  margin of `0.50` (absent from the dataset) and the contract-level churn rate
  as the lifetime horizon. Documented and replaceable in `v_customer_360`.
- **No-join BI strategy** — aggregated views (`020`–`050`) are consumed
  independently and are **not** joined back to the customer-level view, avoiding
  fan-out and double counting.
- **CAC / LTV:CAC** — require external finance inputs (sales & marketing spend,
  new-customer counts); flagged as a data gap rather than fabricated.

---

## 4. End-to-end execution commands

### 4.1 Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4.2 Ingestion (Python)

```bash
python -c "from src.data import ingestion; df = ingestion.stage_raw(); print(df.shape)"   # (7043, 43)
python -c "from src.data import validation; import json; print(json.dumps(validation.validate_dataset(ingestion.load_raw()), indent=2))"
```

### 4.3 SQL layering (DuckDB)

```bash
duckdb churn.db < sql/schemas/001_raw_staging.sql
duckdb churn.db < sql/schemas/002_clean_typed.sql
duckdb churn.db < sql/transformations/020_feature_engineering.sql

duckdb churn.db < sql/views/010_customer_360.sql
duckdb churn.db < sql/views/020_churn_metrics.sql
duckdb churn.db < sql/views/030_mrr_impact.sql
duckdb churn.db < sql/views/040_cohort_retention.sql
duckdb churn.db < sql/views/050_service_bundles.sql
duckdb churn.db < sql/views/060_revenue_leakage.sql
duckdb churn.db < sql/views/070_regional_churn.sql
```

### 4.4 Validation

```bash
# Row/column reconciliation
duckdb churn.db -c "SELECT COUNT(*) FROM analytics.clean_customers"          # 7043
duckdb churn.db -c "SELECT SUM(churn) FROM analytics.clean_customers"        # 1869
duckdb churn.db -c "SELECT SUM(customer_status='Joined') FROM analytics.clean_customers"  # 454
duckdb churn.db -c "SELECT * FROM v_churn_metrics WHERE segment='overall'"
duckdb churn.db -c "SELECT * FROM v_mrr_impact WHERE contract='(All contracts)' AND tenure_bin='(All tenure)'"
```

### 4.5 Notebooks (Stages 2 & 4)

```bash
jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_feature_prep.ipynb
jupyter nbconvert --to notebook --execute notebooks/03_cohort_analysis.ipynb
jupyter nbconvert --to notebook --execute notebooks/04_feature_importance.ipynb
```

---

## 5. Definition of done

A stage is complete when its validation criteria all pass and the outputs
reconcile against the canonical table `analytics.clean_customers` (see §4.4).
