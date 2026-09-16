# Stage 4 — In-depth Analysis Findings

**Project:** Telecom Customer Churn (Maven Analytics) · **Date:** 2026-09-15
**Source data:** `data/processed/clean_customers.csv` (7,043 × 43) · `data/raw/telecom_zipcode_population.csv`
**Companion artifacts:** `notebooks/03_cohort_analysis.ipynb`, `notebooks/04_feature_importance.ipynb`, `reports/figures/stage4_*.png`

---

## 1. Executive summary

At end of fiscal Q2 2022, **1,869 of 6,589 existing customers (28.4%) churned**.
The analysis isolates *where* churn concentrates, *how much* it costs, and
*what* drives it:

| Finding | Headline number |
|---|---|
| **Revenue at risk (36-mo)** | **$4,935,119** (12-mo: $1,645,040; 24-mo: $3,290,080) |
| **Dominant revenue leak** | Month-to-Month = **86.6%** of MRR at risk ($118,803 / $137,087) |
| **Top churn driver** | Contract commitment — Month-to-Month churns at **68.0%** in year 1 vs 10.7% (One Year) and 0% (Two Year) |
| **Retention tipping point** | **~12 months** — churn velocity halves after year 1 (59.9% → 28.7%) |
| **Highest-risk tenure window** | **First 90 days** (597 churners = 31.9% of all churn) |
| **Model signal** | Logistic AUC **0.912** · RandomForest AUC **0.921** |
| **Network tech disparity** | Fiber Optic churn **42.1%** vs DSL 20.0% / Cable 27.5% |
| **Worst geography** | San Diego MSA — 4 of top-5 zips; city churn 66.5% |

The picture is consistent across every lens: **churn is an early-tenure,
Month-to-Month, Fiber-Optic problem concentrated in a handful of
San-Diego-area ZIP codes**, and the highest-ROI interventions are (1) converting
Month-to-Month customers to term contracts, (2) proactive support contact in
the first 90 days, and (3) a Fiber Optic price/service retune in the worst
markets.

---

## 2. Revenue leakage (12/24/36-month windows)

`revenue_at_risk(h) = Σ monthly_charge × h` over churned customers, for
h ∈ {12, 24, 36}. **This is an upper bound** — it assumes every churned dollar
is lost for the full horizon, with **no within-window churn probability and no
discounting**. The MRR-impact baseline reproduces the analytical SQL view
(`v_mrr_impact`) exactly: **Σ monthly_charge of churned = $137,086.65**.

### Grand total

| Horizon | Revenue at risk |
|---|---|
| 12 months | **$1,645,039.80** |
| 24 months | **$3,290,079.60** |
| 36 months | **$4,935,119.40** |

(Check: $137,086.65 × 12 / 24 / 36 — reconciles exactly.)

### By contract

| Contract | Churned | MRR impact | 12-mo | 24-mo | 36-mo | % of MRR |
|---|---:|---:|---:|---:|---:|---:|
| Month-to-Month | 1,655 | $118,802.90 | $1,425,634.80 | $2,851,269.60 | $4,276,904.40 | 86.6% |
| One Year | 166 | $14,118.45 | $169,421.40 | $338,842.80 | $508,264.20 | 10.3% |
| Two Year | 48 | $4,165.30 | $49,983.60 | $99,967.20 | $149,950.80 | 3.0% |
| **Total** | **1,869** | **$137,086.65** | **$1,645,039.80** | **$3,290,079.60** | **$4,935,119.40** | **100%** |

**Takeaway:** Month-to-Month customers account for **88.5% of churned
customers** and **86.6% of the MRR at risk**. Fixing Month-to-Month churn is
the single largest revenue opportunity in the portfolio.

### By contract × tenure cohort (MRR impact, $)

| Contract | 0-12 | 13-24 | 25-36 | 37-48 | 49-60 | 60+ |
|---|---:|---:|---:|---:|---:|---:|
| Month-to-Month | 67,104.05 | 21,427.30 | 13,218.70 | 9,044.50 | 5,684.45 | 2,323.90 |
| One Year | 652.80 | 1,101.35 | 1,701.75 | 2,819.60 | 4,034.40 | 3,808.55 |
| Two Year | 0.00 | 0.00 | 49.25 | 334.90 | 863.05 | 2,918.10 |

Month-to-Month MRR at risk is **overwhelmingly early-tenure** (57% sits in the
0-12 cohort), whereas One/Two-Year leakage drifts to later tenure (late-term
price/competitor churn). See `reports/figures/stage4_revenue_leakage.png`.

---

## 3. Retention drivers

### 3.1 Feature importance (modeled)

**Methodology** (`notebooks/04_feature_importance.ipynb`): 37 leakage-free
features — numeric, boolean, and one-hot (`offer`, `payment_method`,
`contract`, `gender`) — trained on existing customers (n = 6,589, 28.4%
positive). Excluded: `customer_id`, `customer_status`, `churn`,
`churn_category`, `churn_reason`, and `total_revenue` (r = 0.97 with
`total_charges`). `internet_type` is represented by `is_fiber` +
`internet_service` to avoid perfect collinearity.

| Model | Holdout ROC-AUC |
|---|---|
| LogisticRegression (`class_weight='balanced'`) | **0.9122** |
| RandomForestClassifier (n=300, balanced) | **0.9206** |

Top features by **|logistic coefficient|** (standardized features):

| Rank | Feature | \|coef\| |
|---|---:|---:|
| 1 | tenure_months | 1.651 |
| 2 | num_referrals | 1.589 |
| 3 | total_charges | 0.970 |
| 4 | married | 0.829 |
| 5 | num_dependents | 0.650 |
| 6 | contract_commitment | 0.623 |
| 7 | monthly_charge | 0.503 |
| 8 | contract_Two Year | 0.467 |
| 9 | contract_One Year | 0.261 |
| 10 | offer_Offer A | 0.249 |
| 11 | offer_Offer D | 0.221 |
| 12 | phone_service | 0.210 |
| 13 | age | 0.196 |
| 14 | online_security | 0.193 |
| 15 | premium_tech_support | 0.180 |

Top features by **RandomForest feature_importances_**:

| Rank | Feature | Importance |
|---|---:|---:|
| 1 | contract_commitment | 0.121 |
| 2 | tenure_months | 0.118 |
| 3 | total_charges | 0.085 |
| 4 | num_referrals | 0.079 |
| 5 | monthly_charge | 0.070 |
| 6 | total_long_distance_charges | 0.061 |
| 7 | contract_Two Year | 0.060 |
| 8 | age | 0.052 |
| 9 | avg_monthly_gb_download | 0.044 |
| 10 | avg_monthly_long_distance_charges | 0.041 |
| 11 | num_dependents | 0.036 |
| 12 | bundle_count | 0.024 |
| 13 | is_fiber | 0.024 |
| 14 | contract_One Year | 0.016 |
| 15 | payment_method_Credit Card | 0.014 |

**Interpretation (with honesty about mechanism):** `tenure_months` and
`total_charges` top both lists, but they are largely *mechanical* —
`total_charges` is lifetime spend that grows with tenure, and tenure is the
single strongest churn signal (churn is front-loaded). The **actionable**
drivers are:

1. **`contract_commitment`** — the #1 tree feature and #6 logistic feature.
   Term contracts are the strongest protective signal in the dataset.
2. **`num_referrals`** — strong inverse churn proxy (advocacy ⇒ loyalty),
   second by logistic coefficient.
3. **`monthly_charge`** — higher price ⇒ higher churn (price sensitivity).
4. **`married` / `num_dependents` / `age`** — stable-life-stage proxies
   protective against churn.
5. **`premium_tech_support` / `online_security` / `bundle_count`** — retention
   add-ons with a real (if secondary) protective effect.

### 3.2 Add-on bundles (behavioral retention)

`premium_tech_support` more than halves churn: **15.5%** with support vs
**34.0%** without (overall existing-customer population). The support effect is
**not uniform across tenure** — it only materializes after ~7 months (see §4).

---

## 4. Early-tenure friction & the support-touch tipping point

**Limitation (stated explicitly):** the dataset has **no support-ticket
column**. Proxies are used: (a) the `premium_tech_support` subscription flag,
and (b) `churn_reason ∈ {'Attitude of support person', 'Attitude of service
provider'}` — **314 churned customers (16.8% of churn)** cite an attitude of
the support person or service provider as their reason.

### 4.1 Churn velocity by early-tenure bucket

| Tenure bucket | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| 0-3 mo | 597 | 597 | **100.0%** |
| 4-6 mo | 419 | 187 | 44.6% |
| 7-12 mo | 716 | 253 | 35.3% |
| 13-24 mo | 1,024 | 294 | 28.7% |
| 25-36 mo | 832 | 180 | 21.6% |
| 37+ mo | 3,001 | 358 | 11.9% |

### 4.2 Support effect across tenure (premium_tech_support)

| Tenure bucket | w/o support | w/ support | Δ (pp) |
|---|---:|---:|---:|
| 0-3 mo | 100.0% | 100.0% | 0.0 |
| 4-6 mo | 44.7% | 44.3% | −0.4 |
| 7-12 mo | 36.7% | 29.1% | **−7.5** |
| 13-24 mo | 30.1% | 23.6% | **−6.5** |
| 25-36 mo | 24.7% | 14.5% | **−10.1** |
| 37+ mo | 14.2% | 8.9% | **−5.3** |

### 4.3 The tipping point — numeric threshold

- **Highest-velocity window = the first 90 days.** 597 customers (31.9% of all
  churn) leave within 3 months. This is the `≤90 days` support-touch window:
  a proactive onboarding/health-check touch in the first quarter targets the
  single densest block of churn.
- **Retention stabilizes at ~12 months.** After the first year, churn velocity
  falls below the overall average (28.4%) and monotonically declines to ~12%
  beyond 37 months. The steepest drop is the first-year boundary (59.9% →
  28.7%).
- **Premium-tech-support is only protective after ~7 months** — it has zero
  effect in the first 6 months (customers churn before support can act), and
  the largest effect (−10.1 pp) appears at 25-36 months. This implies the
  *timing* of the support offer matters: selling premium support to a brand-new
  customer does not reduce churn; it pays off for established accounts.

---

## 5. Infrastructure & regional disparities

### 5.1 By network technology

| internet_type | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| Fiber Optic | 2,934 | 1,236 | **42.1%** |
| Cable | 774 | 213 | 27.5% |
| DSL | 1,537 | 307 | 20.0% |

Fiber Optic — the fastest-growing, highest-priced tier — churns at **2.1× the
DSL rate** and **1.5× the Cable rate**. This supports the price/service-mismatch
hypothesis for Fiber.

### 5.2 Geography (zip population join, 100% of 1,626 customer zips covered)

**Top 5 high-churn ZIP codes (n ≥ 20):**

| ZIP | City | Customers | Churned | Churn rate |
|---|---|---:|---:|---:|
| 92122 | San Diego | 34 | 33 | **97.1%** |
| 92130 | San Diego | 21 | 20 | **95.2%** |
| 92109 | San Diego | 27 | 24 | **88.9%** |
| 92117 | San Diego | 34 | 30 | **88.2%** |
| 92126 | San Diego | 32 | 28 | **87.5%** |

**Top 5 high-churn cities (n ≥ 20):**

| City | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| San Diego | 278 | 185 | **66.5%** |
| Fallbrook | 41 | 26 | 63.4% |
| Temecula | 36 | 22 | 61.1% |
| Santa Rosa | 21 | 11 | 52.4% |
| Modesto | 26 | 12 | 46.2% |

The five worst ZIPs are **all in San Diego** (a Fiber-heavy urban market), and
San Diego is the worst city (66.5% churn vs 28.4% overall). Churn is not
geographically diffuse — it clusters in a small number of urban Fiber markets.

---

## 6. Assumptions & limitations

1. **Revenue-at-risk is an upper bound.** It assumes each churned dollar is lost
   for the full 12/24/36-month horizon with no within-window churn probability
   and no discounting; real economic loss is lower. State this on any
   dashboard quoting these figures.
2. **Churn is a point-in-time snapshot** (end of Q2 2022), not longitudinal
   events. "Cohort retention" is *cross-sectional retention by tenure cohort*,
   not a true survival curve over time.
3. **The 0-3-month "100% churn" is partly a classification artifact.** In this
   dataset, `Stayed` customers have `tenure_months ≥ 4`; active customers with
   1-3 months tenure are labeled `Joined` (454 rows, excluded), so every
   *existing* customer with ≤ 3 months tenure is, by construction, churned. The
   first-90-day window is still the densest churn block, but the 100% figure is
   definitional, not a measured hazard.
4. **No support-ticket column.** The support-touch analysis relies on
   `premium_tech_support` and attitude-related `churn_reason` proxies.
5. **`tenure_months` / `total_charges` dominate importance** for partly
   mechanical reasons (tenure is front-loaded churn; total spend grows with
   tenure). Actionable drivers are read from the *behavioral* features
   (contract, referrals, price, support, add-ons).
6. **CLV/CAC not fully computable** — gross margin (0.50) and CAC are external
   inputs, per the domain contract; this report therefore focuses on
   revenue-at-risk rather than full LTV:CAC.
7. **120 negative `monthly_charge` values** are retained (flagged in EDA as
   credits/refunds); they depress MRR impact marginally and are documented, not
   silently dropped.

---

## 7. Recommended actions (each tied to a quantified opportunity)

| # | Recommendation | Quantified opportunity |
|---|---|---|
| 1 | **Convert Month-to-Month → term contract** (targeted early-tenure offer/win-back). | Month-to-Month = **86.6% of MRR at risk** ($118.8K/mo, $4.28M over 36-mo). Cutting its year-1 churn rate toward One-Year's (68% → ~11%) would save the largest single revenue block. |
| 2 | **Proactive support touch in the first 90 days.** | 597 churners leave in ≤ 3 months (31.9% of all churn); onboarding health-checks at day 30/60/90 target the densest churn window. |
| 3 | **Fiber Optic price/service retune.** | Fiber churn 42.1% vs 20.0% DSL — a 2.1× gap worth ~$4.1K/mo per percentage-point of Fiber churn reduced across 2,934 accounts. |
| 4 | **Geo-targeted retention in San Diego MSA.** | San Diego city churn 66.5% (185/278); 5 worst zips all San Diego. A field-marketing + field-service push here attacks the single densest churn cluster. |
| 5 | **Sell premium support to established (7+ mo) accounts, not new ones.** | Premium support cuts churn −5 to −10 pp **only after 7 months**; largest effect (−10.1 pp) at 25-36 mo. Re-sequence the upsell to established Fiber/urban accounts. |
| 6 | **Leverage referrals as a retention lever.** | `num_referrals` is the #2 logistic driver (coef 1.589); referral programs correlate with the most loyal, lowest-churn segment. |

---

## Figures

All in `reports/figures/` (new Stage-4, prefixed `stage4_`):

- `stage4_revenue_leakage.png` — 12/24/36-mo revenue at risk by tenure cohort × contract (stacked).
- `stage4_risk_matrix_heatmap.png` — churn rate (%) contract × tenure_bin (3×6).
- `stage4_retention_curve.png` — % retained by tenure cohort.
- `stage4_feature_importance.png` — top-15 logistic \|coef\| and RF importance side-by-side.
- `stage4_churn_by_zip.png` — top-5 high-churn ZIPs and cities.
- `stage4_tipping_point.png` — churn velocity + premium-tech-support overlay.
