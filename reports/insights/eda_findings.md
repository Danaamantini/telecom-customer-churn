# EDA Findings — Telecom Customer Churn (Stage 2)

**Status:** complete
**Input:** `data/processed/clean_customers.csv` (7,043 rows × 43 columns)
**Scope:** read-only profiling, distribution, correlation, and descriptive
hypothesis testing. No rows dropped; no data modified.

> **Churn-rate convention.** `customer_status = 'Joined'` (454 rows) is an
> acquisition cohort, **not** churn. Every churn rate below is computed over the
> **existing-customer denominator** `Churned + Stayed = 1,869 + 4,720 = 6,589`,
> unless explicitly noted.

---

## 1. Dataset summary

| Metric | Value |
|---|---|
| Rows | 7,043 |
| Columns | 43 |
| `Churned` | 1,869 |
| `Stayed` | 4,720 |
| `Joined` | 454 |
| Duplicated rows | 0 |
| Duplicated `customer_id` | 0 |
| **Overall churn rate (excl. Joined)** | **28.37%** (1,869 / 6,589) |

- Class balance is healthy for modeling: 28.4% churn vs 71.6% stay in the
  existing-customer population (roughly 1 : 2.5), no resampling required for
  descriptive work.
- No duplicate rows and `customer_id` is a unique primary key (grain confirmed).

---

## 2. Missing-value profile

Null counts per column (only non-zero shown; **all other 39 columns are fully
populated**):

| Column | Nulls | Share | Explanation |
|---|---|---|---|
| `offer` | 0 | — | `'None'` is a **literal string** (3,877 rows = "no offer accepted"), a valid level, not missing |
| `churn_category` | 5,174 | 73.5% | empty for non-churned (4,720 Stayed + 454 Joined) |
| `churn_reason` | 5,174 | 73.5% | empty for non-churned |
| `internet_type` | 1,526 | 21.7% | empty for no-internet rows |

> **Note on the expected "≈1,526 / ≈682" missing counts.** The no-internet /
> no-phone add-on columns were already coerced during ingestion (`001`) per the
> canonical contract: the 8 internet add-ons and `multiple_lines` are **booleans
> coerced to FALSE** (not NULL), and `avg_monthly_gb_download` /
> `avg_monthly_long_distance_charges` are **coerced to 0** (not NULL) for the
> 1,526 no-internet and 682 no-phone rows respectively. Verified:
> `internet_service == False` → 1,526 rows; `avg_monthly_gb_download == 0` →
> 1,526; `phone_service == False` → 682; `avg_monthly_long_distance_charges == 0`
> → 682. So only the four **string** columns above retain NULLs in the clean
> table.

Missing-data mechanism assessment:
- `internet_type` / `churn_category` / `churn_reason` nulls are **structural
  (MNAR by construction)** — they are conditionally empty by definition, not
  randomly missing. They should remain NULL (or explicit sentinels) rather than
  be imputed.
- `offer` has **0 true nulls**: the value `'None'` (3,877 rows) literally means
  "no offer accepted" and is a valid category. (Caution: `pandas.read_csv` with
  default settings coerces the string `'None'` to NaN — read with `na_values=[]`
  to preserve it.)

---

## 3. Distribution & skewness

| Column | mean | median | std | skew | min | max |
|---|---|---|---|---|---|---|
| `age` | 46.51 | 46.0 | 16.75 | 0.16 | 19 | 80 |
| `tenure_months` | 32.39 | 29.0 | 24.54 | 0.24 | 1 | 72 |
| `monthly_charge` | 63.60 | 70.05 | 31.20 | −0.28 | −10.00 | 118.75 |
| `total_charges` | 2,280.38 | 1,394.55 | 2,266.22 | 0.96 | 18.80 | 8,684.80 |
| `total_revenue` | 3,034.38 | 2,108.64 | 2,865.21 | 0.92 | 21.36 | 11,979.34 |
| `num_referrals` | 1.95 | 0.0 | 3.00 | 1.45 | 0 | 11 |
| `num_dependents` | 0.47 | 0.0 | 0.96 | 2.11 | 0 | 9 |

Notable observations:
- `monthly_charge` is the only feature with a **negative tail** (min −10; 120
  values — see §4) and is otherwise right-capped at 118.75 with a median of 70.
- `total_charges` and `total_revenue` are **strongly right-skewed** (skew ≈
  0.92–0.96) and highly correlated (r = 0.97) — expected, since both accumulate
  over tenure (`total_charges` r = 0.83 with `tenure_months`).
- `num_referrals` and `num_dependents` are zero-inflated (median 0, skew > 1.4).
- IQR outlier scan: `total_revenue` has 21 values above the upper fence
  (genuine high-value customers, not errors — max 11,979 is plausible lifetime
  revenue). `monthly_charge`, `total_charges`, `tenure_months`, `age` have **no**
  IQR outliers beyond the 120 negative charges (the negative tail sits above the
  −58.63 lower fence, so it is *not* an IQR outlier even though it is anomalous
  in sign).

---

## 4. Negative `monthly_charge` investigation

| Metric | Value |
|---|---|
| Count | **120** (1.70% of rows) |
| Range | **−10.00 to −1.00** |
| Mean | −5.42 |
| Values | strictly integers {−10, −9, …, −1} |
| By status | Stayed 84 · Churned 30 · Joined 6 |
| By contract | Month-to-Month 61 · One Year 30 · Two Year 29 |
| Tenure span | 1–72 months (full range) |
| Internet | 94 with internet · 26 without |

**Judgment: billing credits, not data errors.** Evidence:
1. All 120 values are small, integer, single-digit credits (−1 to −10), with no
   implausible magnitude (no −9,999 sentinel, no missing-sign on a large bill).
2. They are **uniformly distributed across all statuses, contract types, and the
   full tenure range** — inconsistent with a systematic coding error (which
   would cluster in one segment or one value).
3. Their churn rate (26.3%) is close to the overall 28.4% — i.e., these are
   ordinary customers, not a distinct broken cohort.

**Recommendation:** do **not** drop. Flag for `003`/`004`: for MRR/CLV
calculations, floor `monthly_charge` at 0 (or net against a credit line) so a
credit month does not produce negative revenue; keep the rows in churn analyses.

---

## 5. Correlations

### 5a. Point-biserial — numeric features vs `churn` (bool)

| Feature | r_pb |
|---|---|
| `contract_commitment` (0/1/2) | **−0.435** |
| `tenure_months` | **−0.353** |
| `num_referrals` | −0.287 |
| `total_long_distance_charges` | −0.224 |
| `total_revenue` | −0.223 |
| `num_dependents` | −0.219 |
| `total_charges` | −0.199 |
| `monthly_charge` | +0.188 |
| `age` | +0.116 |
| `avg_monthly_gb_download` | +0.049 |
| `bundle_count` | −0.026 |
| `avg_monthly_long_distance_charges` | +0.008 |
| `total_refunds` | −0.034 |
| `total_extra_data_charges` | +0.007 |

Strongest drivers are **contract commitment** (more commitment → far less churn)
and **tenure** (longer tenure → less churn). `monthly_charge` is the only
positive-revenue correlate (+0.19: higher bills churn more). `bundle_count` alone
is near-zero because the relationship is non-monotonic (see §6.4).

### 5b. Cramér's V — categorical features vs `churn`

| Feature | V | chi² | n |
|---|---|---|---|
| `contract` | **0.453** | 1,445 | 7,043 |
| `offer` | 0.393 | 489 | 3,166 |
| `tenure_bin` | 0.352 | 874 | 7,043 |
| `internet_service` | 0.228 | 366 | 7,043 |
| `payment_method` | 0.219 | 338 | 7,043 |
| `internet_type` | 0.217 | 259 | 5,517 |
| `paperless_billing` | 0.192 | 259 | 7,043 |
| `married` | 0.150 | 159 | 7,043 |
| `multiple_lines` | 0.040 | 11 | 7,043 |
| `phone_service` | 0.012 | 1 | 7,043 |
| `gender` | 0.009 | 0.5 | 7,043 |

`contract` is by far the dominant categorical association (V = 0.45), followed by
`offer` (V = 0.39). `gender` and `phone_service` show **no** association with
churn (V ≈ 0.01, p > 0.3). All other associations are statistically significant
(p < 0.001) given N = 7,043; effect sizes (V) are the meaningful signal, and
they rank contract / offer / tenure / internet well above demographics.

### 5c. Correlation matrix (heatmap — `reports/figures/correlation_heatmap.png`)

Multicollinearity highlights:
- `total_revenue` ↔ `total_charges` r = **0.97** (redundant — keep one in
  predictive models).
- `total_charges` ↔ `tenure_months` r = 0.83; `total_revenue` ↔ `tenure_months`
  r = 0.85.
- `bundle_count` ↔ `monthly_charge` r = 0.73 and ↔ `total_charges` r = 0.71
  (bundling and spend track together).
- `age` ↔ `avg_monthly_gb_download` r = −0.38 (younger users download more).

---

## 6. Hypothesis results

### H1 — Month-to-month contracts drive the highest churn — **SUPPORTED**

| Contract | n (excl. Joined) | Churned | Churn rate |
|---|---|---|---|
| Month-to-Month | 3,202 | 1,655 | **51.69%** |
| One Year | 1,526 | 166 | 10.88% |
| Two Year | 1,861 | 48 | 2.58% |

Month-to-month churn is **~5×** the one-year rate and **~20×** the two-year rate,
and accounts for 1,655 / 1,869 = **88.6% of all churn**. `contract` is the
single strongest churn correlate in the dataset (V = 0.45; point-biserial of
`contract_commitment` = −0.435).

### H2 — Fiber Optic customers churn more than DSL/Cable — **SUPPORTED**

| Internet type | n | Churned | Churn rate |
|---|---|---|---|
| **Fiber Optic** | 2,934 | 1,236 | **42.13%** |
| Cable | 774 | 213 | 27.52% |
| DSL | 1,537 | 307 | 19.97% |
| No internet | 1,344 | 113 | 8.41% |

Fiber churn (42.1%) is the highest of all technology types — **1.5×** Cable and
**2.1×** DSL. `is_fiber` churn is 42.13% vs 17.32% for non-fiber. This is
consistent with a price/service mismatch on Fiber, but note the ordering
(Cable > DSL) means the story is *Fiber stands out*, not a clean
"fiber-vs-everything" dichotomy.

### H3 — Mailed-check payers churn more — **PARTIALLY SUPPORTED**

| Payment method | n | Churned | Churn rate |
|---|---|---|---|
| **Mailed Check** | 343 | 142 | **41.40%** |
| Bank Withdrawal | 3,728 | 1,329 | 35.65% |
| Credit Card | 2,518 | 398 | 15.81% |

Mailed check **is** the highest-churn method (41.4%), supporting the billing-
friction idea — but the margin over Bank Withdrawal (35.7%) is modest (+5.7 pp),
while Credit Card is dramatically lower (15.8%). The cleaner signal is that
**Credit Card autopay is the lowest-churn method**; the friction penalty is
concentrated in Mailed Check and (surprisingly) Bank Withdrawal.

### H4 — Bundled add-ons reduce churn (incl. competitor churn) — **SUPPORTED**

| Add-on | ON (n) | ON churn | OFF (n) | OFF churn |
|---|---|---|---|---|
| `premium_tech_support` | 1,997 | **15.52%** | 4,592 | 33.95% |
| `online_security` | 1,973 | **14.95%** | 4,616 | 34.10% |
| `device_protection_plan` | 2,390 | **22.80%** | 4,199 | 31.53% |
| **All three combined** | 712 | **7.16%** | 2,910 (none) | 35.29% |

Each add-on halves churn, and holding **all three** together drives churn down to
**7.16%** vs **35.29%** for customers with none of the three — a **4.9×
reduction**. Critically for retention strategy, the three-add-on bundle also
collapses **competitor-driven churn**: 3.51% competitor churn (all three) vs
15.84% (none).

> **Caveat on `bundle_count` (0–8).** The aggregate relationship is
> non-monotonic: 0 add-ons = 10.7% churn, **1 add-on = 59.2%** (the peak), then
> declining monotonically to 8 add-ons = 4.9%. The "0 bundle" group is dominated
> by no-internet customers (who rarely churn, 8.4%), which masks the true
> gradient. For internet customers the pattern is clear: **more add-ons → less
> churn** once ≥ 1 is present. Use the specific add-on flags (above), not the raw
> count, in modeling.

### H5 — Early-tenure churn velocity (≤ 12 months) — **SUPPORTED**

| Tenure bucket | n | Churned | Churn rate |
|---|---|---|---|
| **0–12** | 1,732 | 1,037 | **59.87%** |
| 13–24 | 1,024 | 294 | 28.71% |
| 25–36 | 832 | 180 | 21.63% |
| 37–48 | 762 | 145 | 19.03% |
| 49–60 | 832 | 120 | 14.42% |
| 60+ | 1,407 | 93 | 6.61% |

- ≤ 12 months: **59.87%** churn vs **17.13%** for tenure > 12 months.
- The ≤ 12-month cohort is only 26.3% of existing customers (1,732 / 6,589) but
  produces **55.5% of all churn** (1,037 / 1,869).
- Churn rate falls monotonically and steeply with tenure, stabilizing below ~19%
  after 36 months (the **retention "tipping point"** is ~36 months).

### H6 — Competitor churn is dominant; device/offer reasons lead — **SUPPORTED**

Churn category (1,869 churned customers):

| Category | Count | Share of churn |
|---|---|---|
| **Competitor** | 841 | **45.0%** |
| Dissatisfaction | 321 | 17.2% |
| Attitude | 314 | 16.8% |
| Price | 211 | 11.3% |
| Other | 182 | 9.7% |

Top churn reasons (churned only):

| Reason | Count |
|---|---|
| **Competitor had better devices** | 313 |
| **Competitor made better offer** | 311 |
| Attitude of support person | 220 |
| Don't know | 130 |
| Competitor offered more data | 117 |
| Competitor offered higher download speeds | 100 |
| Attitude of service provider | 94 |
| Price too high | 78 |

Competitor is the dominant category at **45%**, and the top-two reasons are the
two competitor device/offer reasons. The four competitor reasons together sum to
841 (= the full Competitor category), confirming internal consistency.

---

## 7. Key insights & recommended next steps

1. **Contract is the #1 lever.** 88.6% of churn comes from month-to-month
   customers (51.7% churn rate). Moving M2M customers to even a one-year
   commitment would capture the largest single retention win. *(Feeds Stage 4
   revenue-leakage modeling at 12/24/36-month windows.)*
2. **Fiber is a churn hotspot (42%).** Investigate the price/service mismatch:
   Fiber churn is 2× DSL — a strong candidate for targeted retention offers or
   pricing review.
3. **Bundle Premium Tech Support × Online Security × Device Protection.** The
   three-add-on combination cuts churn ~5× and nearly erases competitor churn
   (3.5% vs 15.8%). This is the clearest actionable retention intervention.
4. **Attack the first 12 months.** 55% of churn happens within the first year;
   retention stabilizes after ~36 months. Design an onboarding/early-tenure
   playbook (proactive support, first-year offers) targeting the 0–12 month
   cohort.
5. **Competitor churn (45%) is the main "why."** Root cause is device/offer
   superiority — address via device refresh programs and matching competitor
   offers (offers A/B show low churn; offer E shows 67.6% churn, worth a deep
   dive).
6. **Additional signals for Stage 4:** paperless billing is *positively*
   associated with churn (35.2% vs 17.9% — likely a proxy for new/digital-first
   customers, not a cause); unmarried customers churn more (36.7% vs 20.2%);
   `offer = E` has a 67.6% churn rate (a possible adverse-selection / retention-
   offer flag). Drop `gender` and `phone_service` from churn models (no
   association).
7. **Hygiene to carry forward:** floor the 120 credit rows (`monthly_charge`
   < 0) at 0 for revenue math; keep `total_revenue` OR `total_charges` (r = 0.97)
   in any single model; treat `offer = 'None'` as an explicit "no offer" level (do not drop).

---

## 8. Figures generated (`reports/figures/`)

| File | Content |
|---|---|
| `churn_by_contract.png` | H1 — churn rate by contract type |
| `churn_by_internet_type.png` | H2 — churn rate by internet type |
| `churn_by_tenure_bin.png` | H5 — churn rate by tenure bucket (line) |
| `correlation_heatmap.png` | Numeric feature correlation matrix |
| `monthly_charge_dist.png` | Histogram with negative tail highlighted |
| `churn_by_payment_method.png` | H3 — churn rate by payment method |
| `churn_category.png` | H6 — churn category counts (churned only) |
| `top_churn_reasons.png` | H6 — top churn reasons (churned only) |

---

## 9. Validation checklist

- [x] Missing-value profile table produced for every column.
- [x] Distribution & skewness summary for numeric features.
- [x] Correlation matrix + categorical-vs-churn association table.
- [x] Each Stage-1 hypothesis answered descriptively (H1–H6, with counts/rates).
- [x] `notebooks/01_eda.ipynb` contains executable code (verified against the
      same input under a local `PYTHONPATH`).
- [x] Findings written here + 8 figures saved to `reports/figures/`.
