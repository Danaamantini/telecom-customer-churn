# Executive Dashboard Wireframes

Four dashboards. Each lists KPIs (with the real Stage-4 target values), chart
types, layout (12-column grid), data sources, and drill-down hierarchy.

**Color/accessibility note:** use a single accent for churn (e.g. `#D64550` red),
a neutral blue for revenue, and a colorblind-safe diverging palette
(`#2C7BB6` → `#FFFFBF` → `#D7191C`) for lift/heatmaps. Churn-positive is always
"bad" (red) and retained/healthy always "good" (blue/green) so semantics don't
flip between charts. Reference line at the overall churn rate **28.4%** on every
churn-rate chart.

---

## (a) Churn Overview

**Purpose:** executive pulse on overall churn and its top drivers.
**Data sources:** `v_churn_metrics` (primary), `v_customer_360` (drill-down).

**KPI band (row 1 — 4 tiles):**

| KPI | Target value | Formula | Source |
|-----|--------------|---------|--------|
| Total Customers (existing) | **6,589** | `COUNT([customer_id])` filtered `[is_joined]=FALSE` | v_customer_360 |
| Churned Customers | **1,869** | `SUM(IIF([churn],1,0))` | v_customer_360 |
| Churn Rate % | **28.4%** | `SUM(IIF([churn],1,0)) / COUNT([customer_id])` (excl. Joined) | v_customer_360 |
| Avg Monthly Charge | ~$63.60 | `AVG([monthly_charge])` | v_customer_360 |

**Charts (row 2+):**

| # | Chart | Axes | Data / target values |
|---|-------|------|----------------------|
| 1 | Horizontal bar — churn rate by contract | y=contract, x=churn_rate | Month-to-Month **51.7%** · One Year 10.9% · Two Year 2.6% (highlight M2M) |
| 2 | Bar — churn rate by internet type | x=segment_value, y=churn_rate | Fiber **42.1%** · Cable 27.5% · DSL 20.0% · No-internet 8.4% |
| 3 | Bar — churn rate by payment method | x=segment_value, y=churn_rate | Mailed Check **41.4%** · Bank Withdrawal 35.7% · Credit Card 15.8% |
| 4 | Bar/line — churn rate by tenure bin | x=segment_value (ordered), y=churn_rate | ≤12mo **59.9%** → 60+ 6.6% (tenure curve, descending) |
| 5 | Bar — churn rate by offer | x=segment_value, y=churn_rate | None vs Offer A–E (Offer E flagged: 67.6%) |
| 6 | Bar — Fiber vs Non-Fiber | x=segment_value, y=churn_rate | Fiber 42.1% vs Non-Fiber 17.3% |

**Layout:**

```
┌────────────────────────────────────────────────────────────────────┐
│ Total Customers │ Churned │ Churn Rate % │ Avg Monthly Charge      │  (KPI row)
├───────────────────────────────┬────────────────────────────────────┤
│ Churn by Contract (bar)       │ Churn by Internet Type (bar)      │
│                               ├────────────────────────────────────┤
│                               │ Churn by Payment Method (bar)     │
├───────────────────────────────┼────────────────────────────────────┤
│ Churn by Tenure Bin (line)    │ Churn by Offer / is_fiber (bars)  │
└───────────────────────────────┴────────────────────────────────────┘
```

**Drill-down hierarchy:** segment bar → filter `v_customer_360` on that
attribute (contract / internet_type / payment_method / tenure_bin) → customer
list with `monthly_charge`, `tenure_months`, `churn`.

---

## (b) Revenue at Risk

**Purpose:** quantify the *dollar* impact of churn, not just the rate.
**Data sources:** `v_revenue_leakage` + `v_revenue_leakage_by_contract`
(primary, 12/24/36-mo), `v_mrr_impact` (12-mo annualized), `v_customer_360`
(drill-down).

**KPI band (row 1 — 4 tiles):**

| KPI | Target value | Formula | Source |
|-----|--------------|---------|--------|
| MRR Impact | **$137,087/mo** | `SUM([mrr_impact])` grand-total row (`(All contracts)`/`(All tenure)`) | v_revenue_leakage |
| Annualized Revenue at Risk (12m) | **$1,645,040** | `SUM([revenue_at_risk_12m])` grand-total row | v_revenue_leakage |
| Revenue at Risk (36m) | **$4,935,119** | `SUM([revenue_at_risk_36m])` grand-total row | v_revenue_leakage |
| M2M share of MRR risk | **86.6%** | `[mrr_impact] / { FIXED : SUM([mrr_impact]) }` for contract = Month-to-Month | v_revenue_leakage_by_contract |

**Charts:**

| # | Chart | Axes | Notes / target values |
|---|-------|------|----------------------|
| 1 | Waterfall / bar — revenue at risk by horizon | step = 12m / 24m / 36m | **$1,645,040** → **$3,290,080** → **$4,935,119** |
| 2 | Bar — revenue at risk (36m) by contract | x=contract, y=revenue_at_risk_36m | Month-to-Month **$4,276,904** (86.6%) · One Year $508,264 · Two Year $149,951 |
| 3 | Stacked bar — MRR impact by contract × tenure | x=tenure_bin, color=contract | M2M 0-12 cohort = $67,104 (57% of M2M risk is early-tenure) |
| 4 | Bar — revenue at risk (12m) by internet type | x=internet_type | Fiber premium visibility |

**Layout:**

```
┌────────────────────────────────────────────────────────────────────┐
│ MRR Impact │ Rev at Risk 12m │ Rev at Risk 36m │ M2M Share (86.6%) │
├───────────────────────────────────────────────┬────────────────────┤
│ Waterfall: Rev at Risk 12/24/36m              │ Rev at Risk 36m by│
│ ($1.6M / $3.3M / $4.9M)                       │ Internet Type      │
├───────────────────────────────────────────────┼────────────────────┤
│ MRR Impact by Contract x Tenure (stacked bar) │ Rev at Risk 36m by│
│                                               │ Contract (bar)     │
└───────────────────────────────────────────────┴────────────────────┘
```

**Drill-down:** waterfall segment → `v_customer_360` filtered on that contract →
list churned customers sorted by `monthly_charge` desc (largest loss first).

---

## (c) Retention Drivers

**Purpose:** show what keeps customers — add-on bundling, feature importance, and
early-tenure stickiness.
**Data sources:** `v_churn_by_addon_combo`, `v_churn_by_bundle_count`,
`v_cohort_retention` (primary); `v_customer_360` (drill-down); feature-importance
figures come from `notebooks/04_feature_importance.ipynb` (static).

**KPI band (row 1 — 4 tiles):**

| KPI | Target value | Formula | Source |
|-----|--------------|---------|--------|
| Overall Retention Rate | **71.6%** | `1 - [Churn Rate %]` | v_customer_360 |
| All-three bundle churn | **7.2%** vs none 35.3% | `[churn_rate]` where `combo_label` = all-three / `(no add-ons)` | v_churn_by_addon_combo |
| Competitor churn (bundled vs none) | **3.5%** vs 15.8% | `[churn_rate]` × competitor share by combo | v_churn_by_addon_combo |
| Model AUC (LR / RF) | **0.912** / **0.921** | static reference | notebook 04 |

**Charts:**

| # | Chart | Axes | Notes / target values |
|---|-------|------|----------------------|
| 1 | Heatmap — churn by add-on combo | rows=TechSupport/OnlineSecurity, cols=DeviceProtection | all-three **7.2%** vs none **35.3%** (4.9× reduction); mark lowest-churn cell |
| 2 | Bar — churn rate by bundle count | x=bundle_count, y=churn_rate | internet customers: more add-ons → lower churn (8 add-ons ≈ 4.9%) |
| 3 | Bar — feature importance (top 5) | x=importance, y=feature | tenure_months, num_referrals, total_charges, contract_commitment, monthly_charge |
| 4 | Funnel / line — early-tenure churn | x=tenure bucket, y=churn | first 90 days = **31.9%** of all churn; ≤12mo 59.9%; tipping point ~12 mo |

**Layout:**

```
┌────────────────────────────────────────────────────────────────────┐
│ Retention 71.6% │ All-three 7.2% │ Competitor 3.5% │ AUC 0.921      │
├───────────────────────────────────────────────┬────────────────────┤
│ Heatmap: Churn by Add-on Combo                │ Churn by Bundle    │
│ (TechSupport/OnlineSec x DeviceProtection)    │ Count (bar)        │
├───────────────────────────────────────────────┼────────────────────┤
│ Feature Importance (bar, top-5)               │ Early-Tenure Funnel│
│                                               │ (first 90d / ≤12mo)│
└───────────────────────────────────────────────┴────────────────────┘
```

**Drill-down:** combo heatmap cell → `v_customer_360` filtered on the three
add-on flags (`premium_tech_support`, `online_security`,
`device_protection_plan`) → customer detail.

---

## (d) Regional & Infrastructure

**Purpose:** locate churn geographically and by network technology to prioritize
network upgrades / field intervention.
**Data sources:** `v_churn_by_zip` + `v_churn_by_city` +
`v_churn_by_technology_region` (primary, already population-joined),
`v_customer_360` (scatter/drill-down), `v_churn_metrics` (tech churn reference).

**KPI band (row 1 — 4 tiles):**

| KPI | Target value | Formula | Source |
|-----|--------------|---------|--------|
| Highest-churn Zip | **92122 @ 97.1%** | `ATTR([zip_code])` where `churn_rate` = MAX | v_churn_by_zip |
| San Diego city churn | **66.5%** | `[churn_rate]` where `city` = 'San Diego' | v_churn_by_city |
| Fiber Churn Rate | **42.1%** | `[churn_rate]` where `segment='internet_type'` and `segment_value='Fiber Optic'` | v_churn_metrics |
| Churn per 1000 residents | live | `(SUM(IIF([churn],1,0)) / MAX([Population])) * 1000` | v_customer_360 + population |

**Charts:**

| # | Chart | Axes | Notes / target values |
|---|-------|------|----------------------|
| 1 | Filled map (choropleth) — churn by zip | geocoded `zip_code` / `latitude`,`longitude`; color=`churn_rate` | San Diego hotspot: 92122 **97.1%** · 92130 **95.2%** · 92109 **88.9%**; shade by churn, opacity by `population` |
| 2 | Bar — churn rate by internet type | x=internet_type, y=churn_rate | Fiber **42.1%** vs DSL 20.0% / Cable 27.5% |
| 3 | Bar — churn by top cities | x=city, y=churn_rate | San Diego **66.5%** · Fallbrook 63.4% · Temecula 61.1% |
| 4 | Heatmap — churn by internet_type × top-10 cities | x=city, y=internet_type, color=churn_rate | `v_churn_by_technology_region` cross-tab |

**Layout:**

```
┌────────────────────────────────────────────────────────────────────┐
│ Highest Zip 92122 │ SD City 66.5% │ Fiber 42.1% │ Churn/1000 res   │
├───────────────────────────────────────────────┬────────────────────┤
│ Choropleth: Churn by Zip Code (filled map)    │ Churn by Internet  │
│ (color = regional churn, opacity = population)│ Type (bar)         │
├───────────────────────────────────────────────┼────────────────────┤
│ Churn by Top Cities (bar)                     │ Tech x Region      │
│                                               │ Heatmap            │
└───────────────────────────────────────────────┴────────────────────┘
```

**Drill-down:** map region/zip → `v_customer_360` filtered on `zip_code`/`city` →
customer list with `internet_type`, `contract`, `monthly_charge`, `churn`.

---

## Global dashboard controls

- **Filters:** contract, internet_type, payment_method, tenure_bin (apply to all
  four dashboards from `v_customer_360`).
- **Parameters:** Gross Margin (default 0.50), Total S&M Spend, New Customers
  Acquired — drive CLV / CAC / LTV:CAC tiles.
- **Reference lines:** Churn Rate at the overall **28.4%**; LTV:CAC at `3`.
- **Accessibility:** ≥ 3:1 contrast, red/green never the only discriminator
  (always pair color with labels/values), and text labels on every chart.
  Preserve `zip_code` as a string so leading zeros are not dropped on the map.
