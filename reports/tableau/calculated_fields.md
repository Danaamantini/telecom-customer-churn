# Tableau Calculated Fields

Exact field → formula mappings. All formulas reference the view columns defined
in `sql/views/` and the business rules in `reports/insights/data_dictionary.md`.

> Convention: `churn` (and its alias `is_churned`) are BOOLEAN (`TRUE` = churned).
> `churn_rate` / `retention_rate` columns in the aggregate views are 0–1 ratios;
> format them as **percentage (1 decimal)** in Tableau. Customer-level formulas
> below use `IIF([churn], 1, 0)` to count. Churn-rate denominators always
> **exclude `customer_status = 'Joined'`** — the aggregate views already do this;
> for customer-level calculations filter out `[is_joined]` or
> `[customer_status]='Joined'`.

## Current computed values (authoritative — Stage 4)

| Field | Computed value | Basis |
|-------|----------------|-------|
| Churn Rate % (overall, excl. Joined) | **28.37%** | 1,869 / 6,589 |
| Retention Rate | **71.63%** | 1 − 0.2837 |
| MRR Impact | **$137,086.65/mo** | Σ monthly_charge of churned |
| Annualized Revenue at Risk (12m) | **$1,645,039.80** | MRR × 12 |
| Revenue at Risk 24m | **$3,290,079.60** | MRR × 24 |
| Revenue at Risk 36m | **$4,935,119.40** | MRR × 36 |
| Month-to-Month churn / MRR | **51.69%** / **$118,802.90** (86.6% of risk) | H1 |
| One Year churn / MRR | 10.88% / $14,118.45 (10.3%) | H1 |
| Two Year churn / MRR | 2.58% / $4,165.30 (3.0%) | H1 |
| Fiber Optic churn | **42.13%** (Cable 27.52% / DSL 19.97% / No-internet 8.41%) | H2 |
| Mailed Check / Bank / Credit Card churn | 41.40% / 35.65% / 15.81% | H3 |
| All-three add-on bundle churn | **7.16%** vs none **35.29%** (4.9×) | H4 |
| Competitor churn (all-three vs none) | 3.51% vs 15.84% | H4 |
| Early tenure ≤ 12 mo | **59.87%** churn | H5 |
| Competitor category | **45.0%** of churn (841 / 1,869) | H6 |
| San Diego zips / city | 92122 **97.1%**, 92130 **95.2%**, 92109 **88.9%**; city **66.5%** | §5.2 |

---

## 1. Churn Rate %

**Customer-level** (from `v_customer_360`, excluding Joined):

```
SUM(IIF([is_joined], 0, IIF([churn], 1, 0))) / SUM(IIF([is_joined], 0, 1))
```

Equivalently (explicit `customer_status` guard):

```
SUM(IIF([customer_status] = 'Joined', 0, IIF([churn], 1, 0)))
/ SUM(IIF([customer_status] = 'Joined', 0, 1))
```

→ **28.37%** at the grand-total (all `customer_status != 'Joined'`).

**Pre-aggregated** (from `v_churn_metrics` / `v_cohort_retention` /
`v_churn_by_bundle_count` / `v_churn_by_addon_combo` / `v_churn_by_zip` /
`v_churn_by_city` / `v_churn_by_technology_region`): use the existing column
directly —

```
[churn_rate]
```

*(Format as percentage, 1 dp.)*

## 2. MRR Impact

```
SUM(IIF([churn], [monthly_charge], 0))
```

→ **$137,086.65** at the grand total.

- At the customer grain this is the total monthly recurring revenue lost to churn.
- Pre-aggregated equivalents already exist:
  - `[mrr_impact]` in `v_mrr_impact` (grand-total row = `(All contracts)` / `(All tenure)`);
  - `[mrr_impact]` in `v_revenue_leakage` / `v_revenue_leakage_by_contract` (churned only).

## 3. Annualized Revenue at Risk (12m)

```
[MRR Impact] * 12
```

or, using the pre-aggregated column:

```
[mrr_impact] * 12        -- equals [annualized_revenue_at_risk] in v_mrr_impact
```

→ **$1,645,039.80**.

## 4. Revenue at Risk 24m / 36m

Use the pre-computed columns from `v_revenue_leakage` /
`v_revenue_leakage_by_contract` (preferred):

```
[revenue_at_risk_24m]   -- = [mrr_impact] * 24  → $3,290,079.60
[revenue_at_risk_36m]   -- = [mrr_impact] * 36  → $4,935,119.40
```

Or recompute from MRR:

```
[MRR Impact] * 24
[MRR Impact] * 36
```

## 5. CLV (Customer Lifetime Value)

Formula: `monthly_charge × gross margin × (1 / contract churn rate)`
(per-customer ARPU is the customer's own `monthly_charge` at snapshot).

```
-- Gross Margin is a parameter (default 0.50)
-- Contract churn rate is a FIXED LOD over contract (existing customers only):
[Contract Churn Rate] =
    { FIXED [contract] :
        SUM(IIF([is_joined], 0, IIF([churn], 1, 0)))
        / SUM(IIF([is_joined], 0, 1)) }

CLV = [monthly_charge] * [Gross Margin] * (1 / [Contract Churn Rate])
```

- **Pre-computed option (preferred):** `v_customer_360` already carries
  `[clv_estimate]` = `monthly_charge * 0.50 * (1 / contract_churn_rate)` using
  the contract-level churn rate (over non-Joined customers). Recompute in
  Tableau only when `[Gross Margin]` must be interactively changed.
- Contract churn rates used: Month-to-Month 0.5169, One Year 0.1088, Two Year
  0.0258 → expected lifetime 1.93 / 9.19 / 38.76 (see `expected_lifetime_months`).

## 6. CAC (Customer Acquisition Cost)

Formula: `total S&M spend / new customers acquired`. **Not derivable** from the
dataset — both inputs are external.

```
CAC = [Total S&M Spend] / [New Customers Acquired]
```

- `[Total S&M Spend]` and `[New Customers Acquired]` are Tableau **parameters**
  supplied by finance. Default both to a placeholder (`0` or blank) so CAC is
  `NULL` until provided.

## 7. LTV:CAC Ratio

```
[CLV] / [CAC]
```

- Healthy benchmark: **≥ 3:1**; below 1 signals unsustainable acquisition spend.
- Add a reference line at `3` on any LTV:CAC chart.

## 8. Retention Rate

```
1 - [Churn Rate %]
```

→ **71.63%** overall.

or, from `v_cohort_retention`, use `[retention_rate]` directly.

## 9. Churn Lift / Relative Churn (retention-driver analysis)

```
[churn_rate] / [Baseline Churn Rate]
```

where `[Baseline Churn Rate]` is the overall churn rate (the `overall` row in
`v_churn_metrics`), used as a FIXED LOD:

```
{ FIXED : SUM(IIF([segment]='overall', [churn_rate], 0)) }
```

A combination is a retention driver when `Churn Lift < 1`.

## 10. Churn by Category

From `v_customer_360`, group by `churn_category` (Competitor / Dissatisfaction /
Attitude / Price / Other; NULL for non-churned):

```
Churned by Category = SUM(IIF([churn], 1, 0))
```

Share of churn (churned only, n = 1,869):

| Category | Count | Share |
|---|---:|---:|
| Competitor | 841 | **45.0%** |
| Dissatisfaction | 321 | 17.2% |
| Attitude | 314 | 16.8% |
| Price | 211 | 11.3% |
| Other | 182 | 9.7% |

- `churn_category` is only populated for churned rows; use it as the dimension
  and `SUM(IIF([churn],1,0))` as the measure (NULL category = not churned).

## 11. Churn by Reason

From `v_customer_360`, group by `churn_reason` (free text; NULL for non-churned):

```
Churned by Reason = SUM(IIF([churn], 1, 0))
```

Top reasons (churned only):

| Reason | Count |
|---|---:|
| Competitor had better devices | 313 |
| Competitor made better offer | 311 |
| Attitude of support person | 220 |
| Don't know | 130 |
| Competitor offered more data | 117 |
| Competitor offered higher download speeds | 100 |
| Attitude of service provider | 94 |
| Price too high | 78 |

- `churn_reason` is free text — surface the top reasons as a sorted bar on
  churned counts, optionally filtered to `churn_category='Competitor'`.

## 12. Regional Churn Rate (per zip / city)

**Pre-aggregated (preferred):** `v_churn_by_zip` / `v_churn_by_city` already
carry `[churn_rate]` with an `n ≥ 20` small-sample guard. Use directly:

```
[churn_rate]     -- v_churn_by_zip (one row per zip) / v_churn_by_city
```

**Customer-level** (from `v_customer_360`, map workbook, joined to
`zipcode_population` on `zip_code`):

```
Regional Churn Rate = SUM(IIF([churn], 1, 0)) / COUNT([customer_id])
```

Population-normalized (choropleth shading):

```
Churn per 1000 residents = (SUM(IIF([churn], 1, 0)) / MAX([Population])) * 1000
```

- `[Population]` comes from `telecom_zipcode_population.csv`; `MAX` avoids
  fan-out when multiple customers share a zip.
- Reference values: 92122 → 97.1%, 92130 → 95.2%, 92109 → 88.9%; city San Diego
  → 66.5%, Fallbrook → 63.4%, Temecula → 61.1%.

## Formatting & validation checklist

| Field | Type | Format |
|-------|------|--------|
| Churn Rate % | number | % (1 dp) |
| Retention Rate | number | % (1 dp) |
| MRR Impact | number | currency ($, 0 dp) |
| Annualized Revenue at Risk | number | currency ($, 0 dp) |
| Revenue at Risk 24m / 36m | number | currency ($, 0 dp) |
| ARPU / CLV / CAC | number | currency ($, 0 dp) |
| LTV:CAC | number | number (1 dp) + reference line at 3 |
| Churn per 1000 residents | number | number (1 dp) |
| customer_id | dimension | — |
| churn / is_churned / is_joined / is_fiber | boolean | discrete |
| churn_category / churn_reason | dimension | — |
