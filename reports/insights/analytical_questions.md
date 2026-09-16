# Extended Business & Analytical Questions

Stage 1 — Problem Definition & KPI Scoping.

These questions go **beyond the Maven Analytics default prompts** (which typically
cover descriptive churn rate, a couple of univariate drivers, and a "build a
model" ask). They are framed around *dollar impact, retention economics, and
operational leverage* so the analysis produces recommendations a business can act
on — not just charts.

Every formula below maps to a definition in the data dictionary
(`reports/insights/data_dictionary.md`). Features named here exist in the canonical
schema (`analytics.clean_customers`, 38 base + 5 engineered columns) and in the BI
layer (`sql/views/`).

> **Target & cohort note:** churn is the engineered boolean
> `churn = (customer_status = 'Churned')`. `customer_status` has three values:
> `Churned` (1,869), `Stayed` (4,720), `Joined` (454). `Joined` is a distinct
> **acquisition cohort**, not churn; it is excluded from all churn-rate
> denominators.

---

## 1. CLV & Revenue Leakage

**Business framing**
Churn is not a flat rate — it is a *dollar* problem. A high-value customer on a
Two-year contract who leaves is far more damaging than a low-ARPU
Month-to-month customer who leaves. We need to quantify, per churn cohort, the
exact **monetary loss** and how it compounds over 12/24/36-month windows, broken
out by contract type.

**Exact metric / formula**

| Metric | Formula |
|--------|---------|
| MRR impact of churn (cohort) | `Σ monthly_charge` over churned customers in the cohort |
| Annualized revenue at risk | `MRR impact × 12` |
| N-month cumulative loss (contract c) | `MRR impact(c) × N`, for `N ∈ {12, 24, 36}` |
| CLV | `ARPU × gross margin × (1 / churn rate)` |
| Expected lifetime (months) | `1 / churn rate` |

> `gross margin` is **not** in the dataset. Use a documented placeholder
> (default `0.50`) and flag it as a finance-sourced assumption before sign-off.
> The contract-level churn rate (and thus `1 / churn rate`) is computed over
> **existing** customers only (`customer_status != 'Joined'`).

**Required features**
`monthly_charge`, `total_revenue`, `contract`, `contract_commitment`
(engineered), `tenure_months`, `tenure_bin` (engineered), `customer_status`,
`churn` (engineered boolean), `is_joined` (in `v_customer_360`).

**Analytical method**
1. Segment churned customers by `contract` and by tenure window (`tenure_bin`).
2. Compute `MRR impact` = Σ `monthly_charge` per cohort (view `030_mrr_impact`,
   already annualized ×12).
3. Extend to 12/24/36-month cumulative loss per contract.
4. Compute cohort CLV (`monthly_charge`-weighted) and compare it against the
   realized loss to quantify **value destroyed** per cohort.
5. Deliverable: a revenue-at-risk waterfall by contract type.

---

## 2. Behavioral Retention Drivers

**Business framing**
Which *bundled add-ons* actually keep customers? Telecom operators bundle
Premium Tech Support, Online Security, and Device Protection, but the retention
value of each combination is rarely isolated. Identify the add-on combinations
with the strongest **inverse** relationship to churn — i.e., which bundles are
"sticky".

**Exact metric / formula**

| Metric | Formula |
|--------|---------|
| Churn rate (bundle b) | `churned(b) / total(b)` |
| Lift / relative churn | `churn_rate(bundle) / churn_rate(baseline)` |
| Retention rate | `1 − churn_rate` |

Baseline = overall churn rate (or churn rate of the "no add-ons" group). A
combination is a retention driver when its relative churn is meaningfully < 1.

**Required features**
`premium_tech_support`, `online_security`, `device_protection_plan` (BOOLEAN;
empty = no internet coerced to FALSE), `internet_service`, `internet_type`,
`churn` (boolean), `bundle_count` (engineered count of the **8** internet add-ons,
range 0–8), `churn_category` (to isolate `Competitor`-driven churn).

**Analytical method**
1. Enumerate all 8 combinations of the three add-ons
   (`premium_tech_support × online_security × device_protection_plan`) and compute
   churn rate per combination (view `050_service_bundles`).
2. Also compute churn by `bundle_count` (0–8) to test the "more bundles → lower
   churn" monotonicity (same view).
3. Compare each combination against the "none" group and the overall baseline;
   compute relative lift and a churn-rate ranking.
4. Isolate on `churn_category = 'Competitor'` to test whether bundles specifically
   *defend against competitor poaching* vs. other churn causes.
5. Deliverable: a combination heatmap + lift table, with a competitor-churn subset.

---

## 3. Early Tenure Friction Points

**Business framing**
Do Month-to-Month customers in their first 12 months churn disproportionately?
If yes, is there a **tipping point** — a tenure threshold beyond which retention
stabilizes? This informs proactive intervention (e.g., save offers, onboarding
check-ins) targeted at the earliest, riskiest months.

**Exact metric / formula**

| Metric | Formula |
|--------|---------|
| Early-tenure churn rate | `churned(tenure_bin) / total(tenure_bin)` for the `0-12` bin |
| Churn velocity | `churned / tenure_months` (time-to-churn intensity) |
| Tipping point | tenure threshold `t` where `churn_rate(tenure > t)` stabilizes relative to `churn_rate(tenure ≤ t)` |

**Required features**
`tenure_months`, `tenure_bin` (engineered), `contract`, `contract_commitment`,
`premium_tech_support`, `payment_method`, `churn` (boolean), `churn_reason`.

> **Data gap (stated honestly):** the dataset has **no support-ticket count
> column**. Proxy support-experience friction using `premium_tech_support`
> subscription (has support) and `churn_reason = 'Attitude of support person'`
> (a support-experience complaint) as the two available signals. Flag this proxy
> assumption explicitly; do not overstate it as measured "touches".

**Analytical method**
1. Restrict to `tenure_bin = '0-12'` and compare churn across
   `contract` (Month-to-Month vs term).
2. Build a "friction proxy" (has `premium_tech_support` and/or
   `churn_reason = 'Attitude of support person'`) and compare early-tenure churn
   across those flags.
3. Scan tenure in monthly buckets for the threshold where churn velocity drops
   (the tipping point); cross-reference with `contract_commitment`.
4. Deliverable: churn-velocity curve by tenure with a marked tipping point.

---

## 4. Infrastructure & Regional Disparities

**Business framing**
Do churn spikes cluster by *network technology* (Fiber vs DSL vs Cable) **and** by
*geography*? Fiber typically carries higher price and higher expectations; DSL is
legacy; Cable sits between. Understanding technology-driven churn — and *where*
it concentrates — tells us where network upgrades or price/service realignment
will pay off.

**Exact metric / formula**

| Metric | Formula |
|--------|---------|
| Churn rate by tech | `churned(tech) / total(tech)`, tech ∈ {Fiber Optic, DSL, Cable, (No internet)} |
| MRR impact by tech | `Σ monthly_charge` of churned, grouped by `internet_type` |
| Regional churn rate | `churned(zip) / total(zip)`, grouped by `zip_code` / `city` |
| Population-normalized churn | `churned(zip) / population(zip)` (join `telecom_zipcode_population.csv`) |

**Required features**
`internet_type` (Fiber Optic 3,035 / DSL 1,652 / Cable 830 / NULL 1,526),
`is_fiber` (engineered boolean), `monthly_charge`, `churn` (boolean),
`zip_code`, `city`, `latitude`, `longitude` — plus the secondary data source
`telecom_zipcode_population.csv` (`Zip Code` → `Population`).

> **Note:** unlike the IBM Telco dataset, this Maven dataset **does** ship
> geography (`city`, `zip_code`, `latitude`, `longitude`) and a separate
> zipcode-population lookup. Regional analysis is now **possible** — the prior
> "no geographic column" blocker no longer applies.

**Analytical method**
1. Compute churn rate and MRR impact by `internet_type` (views `020_churn_metrics`,
   `030_mrr_impact`).
2. Test the Fiber-vs-DSL-vs-Cable churn-rate difference (two-proportion z-test)
   with effect size (relative lift).
3. Cross with `contract` and `monthly_charge` to separate *technology* effect
   from *price* effect (Fiber is pricier; is it the fiber or the price?).
4. Aggregate churn rate by `zip_code` / `city` and join
   `telecom_zipcode_population.csv` to produce a population-aware choropleth
   (view/dashboard "Regional & Infrastructure").
5. Deliverable: tech-churn comparison + price/tech decomposition + regional map.

---

## Cross-cutting notes

- **CAC / LTV:CAC** cannot be computed from this dataset: `CAC = total S&M
  spend / new customers acquired`, and neither S&M spend nor a *new customer*
  acquisition event is present. Treat `CAC` and `LTV:CAC` as **parameterized,
  external-input metrics** (Tableau parameters), not derivable columns.
- **Churn is a point-in-time snapshot** (end of fiscal Q2 2022), not
  longitudinal. All retention/velocity statements are cohort snapshots, not
  survival analysis (survival needs event timestamps). `Joined` (454) is an
  acquisition cohort and must be excluded from churn-rate denominators.
- Every numeric definition here is mirrored in `sql/views/` and
  `reports/tableau/calculated_fields.md` so BI output reconciles with the
  business definitions.
