# Data Dictionary — Telecom Customer Churn

Maven Analytics "Telecom Customer Churn" dataset. Grain: one row per customer
(`customer_id`). Churn is a point-in-time snapshot at the end of fiscal Q2 2022
(not longitudinal). **38 columns**, 7,043 rows.

> **Schema note:** this is the real **38-column** Maven Analytics schema, NOT
> the 21-column IBM Telco schema. The churn target is `customer_status`
> (`Churned` / `Stayed` / `Joined`); a derived boolean `churn` is engineered
> downstream.

## Canonical schema (38 columns)

| # | Column | Canonical dtype | Raw header | Meaning | Allowed values / notes |
|---|--------|-----------------|-----------|---------|------------------------|
| 1 | `customer_id` | VARCHAR | `Customer ID` | Unique customer identifier | Primary key / grain of analysis |
| 2 | `gender` | VARCHAR | `Gender` | Customer gender | `Male`, `Female` |
| 3 | `age` | INTEGER | `Age` | Age in years at end of Q2 2022 | 19–80 |
| 4 | `married` | BOOLEAN | `Married` | Married flag | `Yes`→TRUE else FALSE |
| 5 | `num_dependents` | INTEGER | `Number of Dependents` | Count of dependents at home | 0–9 |
| 6 | `city` | VARCHAR | `City` | City of primary residence (California) | enables regional analysis |
| 7 | `zip_code` | INTEGER | `Zip Code` | Zip code of primary residence | joins to zipcode population |
| 8 | `latitude` | DOUBLE | `Latitude` | Latitude of residence | enables geo clustering |
| 9 | `longitude` | DOUBLE | `Longitude` | Longitude of residence | enables geo clustering |
| 10 | `num_referrals` | INTEGER | `Number of Referrals` | Referrals made to date | 0–11; advocacy proxy |
| 11 | `tenure_months` | INTEGER | `Tenure in Months` | Months with company | 1–72 (no `0` tenure) |
| 12 | `offer` | VARCHAR | `Offer` | Last marketing offer accepted | `None`, `Offer A`–`Offer E` (keep `None` literal) |
| 13 | `phone_service` | BOOLEAN | `Phone Service` | Subscribes to home phone | `Yes`→TRUE else FALSE |
| 14 | `avg_monthly_long_distance_charges` | DOUBLE | `Avg Monthly Long Distance Charges` | Avg monthly long-distance charges | empty→`0.0`; 0 if no phone |
| 15 | `multiple_lines` | BOOLEAN | `Multiple Lines` | Multiple phone lines | `Yes`→TRUE else FALSE; empty→FALSE |
| 16 | `internet_service` | BOOLEAN | `Internet Service` | Subscribes to internet | `Yes`→TRUE else FALSE |
| 17 | `internet_type` | VARCHAR | `Internet Type` | Internet connection type | `DSL`, `Fiber Optic`, `Cable`; empty→NULL |
| 18 | `avg_monthly_gb_download` | INTEGER | `Avg Monthly GB Download` | Avg monthly download volume (GB) | empty→`0`; 0 if no internet |
| 19 | `online_security` | BOOLEAN | `Online Security` | Online security add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 20 | `online_backup` | BOOLEAN | `Online Backup` | Online backup add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 21 | `device_protection_plan` | BOOLEAN | `Device Protection Plan` | Device protection add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 22 | `premium_tech_support` | BOOLEAN | `Premium Tech Support` | Premium tech support add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 23 | `streaming_tv` | BOOLEAN | `Streaming TV` | Streaming TV add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 24 | `streaming_movies` | BOOLEAN | `Streaming Movies` | Streaming movies add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 25 | `streaming_music` | BOOLEAN | `Streaming Music` | Streaming music add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 26 | `unlimited_data` | BOOLEAN | `Unlimited Data` | Unlimited data add-on | `Yes`→TRUE else FALSE; empty→FALSE |
| 27 | `contract` | VARCHAR | `Contract` | Contract term | `Month-to-Month`, `One Year`, `Two Year` |
| 28 | `paperless_billing` | BOOLEAN | `Paperless Billing` | Paperless billing enabled | `Yes`→TRUE else FALSE |
| 29 | `payment_method` | VARCHAR | `Payment Method` | How the bill is paid | `Bank Withdrawal`, `Credit Card`, `Mailed Check` |
| 30 | `monthly_charge` | DOUBLE | `Monthly Charge` | Recurring monthly charge (USD) | −10.00 … 118.75; **120 negative values — kept & flagged for EDA** |
| 31 | `total_charges` | DOUBLE | `Total Charges` | Lifetime charges to date (USD) | — |
| 32 | `total_refunds` | DOUBLE | `Total Refunds` | Total refunds (USD) | — |
| 33 | `total_extra_data_charges` | INTEGER | `Total Extra Data Charges` | Overage data charges (USD) | — |
| 34 | `total_long_distance_charges` | DOUBLE | `Total Long Distance Charges` | Long-distance charges (USD) | — |
| 35 | `total_revenue` | DOUBLE | `Total Revenue` | `total_charges − refunds + extra data + long distance` | company revenue from customer |
| 36 | `customer_status` | VARCHAR | `Customer Status` | Status at end of quarter | `Churned` (1,869), `Stayed` (4,720), `Joined` (454) |
| 37 | `churn_category` | VARCHAR | `Churn Category` | High-level churn reason category | `Competitor`, `Dissatisfaction`, `Attitude`, `Price`, `Other`; empty→NULL |
| 38 | `churn_reason` | VARCHAR | `Churn Reason` | Specific churn reason (free text) | empty→NULL |

## Coercion rules (no silent data loss)

Applied in `src/data/ingestion.py::coerce_types` (Pandas) and
`sql/schemas/002_clean_typed.sql` / `sql/transformations/010_type_casting.sql`
(DuckDB):

- **BOOLEAN** (`'Yes'`→TRUE, else FALSE, empty→FALSE): `married`,
  `phone_service`, `multiple_lines`, `internet_service`, `online_security`,
  `online_backup`, `device_protection_plan`, `premium_tech_support`,
  `streaming_tv`, `streaming_movies`, `streaming_music`, `unlimited_data`,
  `paperless_billing`.
- **`internet_type`**: keep `DSL` / `Fiber Optic` / `Cable`; empty → NULL.
- **`avg_monthly_gb_download`**: empty → `0` (INTEGER).
- **`avg_monthly_long_distance_charges`**: empty → `0.0` (DOUBLE).
- **`churn_category` / `churn_reason`**: empty → NULL.
- **`offer`**: keep the `'None'` literal (do not null it).
- **`monthly_charge`**: keep as-is. The 120 negative values (likely refunds /
  credits) are **flagged for EDA — never dropped, never imputed**.

### Null profile (raw, pre-coercion)

| Group | Columns | Empty count |
|-------|---------|-------------|
| No internet service | `internet_type`, `avg_monthly_gb_download`, 8 internet add-ons | 1,526 |
| No phone service | `avg_monthly_long_distance_charges`, `multiple_lines` | 682 |
| Non-churned rows | `churn_category`, `churn_reason` | 5,174 |

All other 24 columns are fully populated.

## Geographic fields & zipcode population join

Unlike the IBM Telco dataset, this schema ships **California geography**:

- `city`, `zip_code`, `latitude`, `longitude` locate each customer's primary
  residence — enabling regional churn analysis and geo clustering.
- `data/raw/telecom_zipcode_population.csv` (`Zip Code` → `Population`) joins
  on `zip_code` to enrich per-zip population context (1,671 zip codes).

## Derived / engineered features

Produced in `sql/transformations/020_feature_engineering.sql`; the canonical
final table is **`analytics.clean_customers`** (38 base + 5 engineered = 43
columns), the single source of truth for all `sql/views/*`.

| Feature | Dtype | Definition |
|---------|-------|-----------|
| `churn` | BOOLEAN | `customer_status = 'Churned'` |
| `tenure_bin` | VARCHAR | `tenure_months` bucket: `0-12`, `13-24`, `25-36`, `37-48`, `49-60`, `60+` |
| `contract_commitment` | INTEGER | `Month-to-Month`→0, `One Year`→1, `Two Year`→2 |
| `bundle_count` | INTEGER | Count of the 8 internet add-ons = TRUE (range 0–8) |
| `is_fiber` | BOOLEAN | `internet_type = 'Fiber Optic'` |

> `bundle_count` counts only the 8 internet add-ons where value = TRUE
> (`online_security`, `online_backup`, `device_protection_plan`,
> `premium_tech_support`, `streaming_tv`, `streaming_movies`, `streaming_music`,
> `unlimited_data`). No-internet rows have all 8 = FALSE → `bundle_count = 0`.
>
> `is_fiber` is `COALESCE(internet_type = 'Fiber Optic', FALSE)` — a no-internet
> row (`internet_type` NULL) is explicitly FALSE, never NULL.

## Key metrics

- **Churn rate** = `churned / total` × 100 (excluding `Joined` for
  existing-customer analyses).
- **MRR impact of churn** = `Σ monthly_charge of churned`; annualized × 12.
- **CLV** = `ARPU × gross margin (0.50 default) × (1 / contract churn rate)`.
- **LTV:CAC** healthy ≥ 3:1 (CAC is an external finance input).
