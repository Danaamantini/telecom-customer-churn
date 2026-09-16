# Recommendations — Telecom Customer Churn (Closing Deliverable)

**Project:** Telecom Customer Churn (Maven Analytics) · **Date:** 2026-09-15
**Inputs:** `reports/insights/eda_findings.md` (Stage 2), `reports/insights/analysis_findings.md` (Stage 4)
**Companion:** `reports/tableau/*.md` (data sources, calculated fields, wireframes)

---

## 1. Executive summary

At end of fiscal Q2 2022, **1,869 of 6,589 existing customers (28.4%) churned**,
putting **$137,087/mo of MRR** — **$4.94M over a 36-month horizon** — at risk.
The loss is not diffuse: it is an **early-tenure, Month-to-Month, Fiber-Optic
problem concentrated in a handful of San-Diego-area ZIP codes**. Month-to-Month
customers alone account for **86.6%** of the revenue at risk (51.7% churn);
Fiber Optic churns at **42.1%** (2.1× DSL); **45% of all churn** is
competitor-driven; and customers who bundle Premium Tech Support × Online
Security × Device Protection churn at **7.2%** versus **35.3%** for those with
none. The highest-ROI moves are, in order: (1) convert Month-to-Month customers
to term contracts, (2) intercept churn in the first 90 days, and (3) retune
Fiber pricing/service in the worst markets. Each recommendation below is tied to
a validated hypothesis and a quantified metric.

### Headline KPIs

| KPI | Value |
|---|---|
| **Overall churn rate** (excl. Joined) | **28.4%** (1,869 / 6,589) |
| **Revenue at risk** (36-mo upper bound) | **$4,935,119** ($137,087 MRR/mo) |
| **Month-to-Month share of risk** | **86.6%** (churn 51.7%) |
| **Fiber Optic churn** (vs DSL) | **42.1%** (2.1× DSL's 20.0%) |

---

## 2. Recommendations (each tied to a validated hypothesis)

### 2.1 Convert Month-to-Month → term contracts
**Hypothesis:** H1 (Month-to-month contracts drive the highest churn) — *SUPPORTED*.

- **Finding / metric:** Month-to-Month churn **51.69%** vs One Year 10.88% vs
  Two Year 2.58%. Month-to-Month = **88.5% of churned customers** (1,655/1,869)
  and **86.6% of MRR at risk** ($118,802.90/mo → **$4,276,904 over 36 months**).
- **Quantified opportunity:** moving even part of the M2M base toward One-Year's
  churn rate (51.7% → ~11%) would capture the largest single revenue block in the
  portfolio. Every 1 pp of M2M churn reduced ≈ **$2.3K/mo** in recovered MRR
  ($118,802.90 / 51.69 pp).
- **Recommended action:** launch a targeted **migration/win-back offer** — a
  discounted One-Year term (or device credit) for high-risk M2M customers, led by
  early-tenure (< 12 mo) accounts where 57% of the M2M MRR risk sits.
- **Target owner:** VP, Retention / Commercial.
- **Success metric:** reduce M2M churn from 51.7% to **< 20%** in 2 quarters;
  convert ≥ 15% of the M2M base to term; recover ≥ **$500K** of the 36-mo at-risk
  revenue.

### 2.2 Fix the Fiber Optic value gap
**Hypothesis:** H2 (Fiber Optic customers churn more than DSL/Cable) — *SUPPORTED*.

- **Finding / metric:** Fiber Optic churn **42.13%** vs Cable 27.52% / DSL
  19.97% / No-internet 8.41% — a **2.1×** gap over DSL on 2,934 accounts.
- **Quantified opportunity:** ~**$4.1K/mo per percentage-point** of Fiber churn
  reduction across 2,934 accounts (Stage 4). Closing Fiber to Cable's level
  (42.1% → 27.5%, ~14.6 pp) is worth ~**$60K/mo**.
- **Recommended action:** run a **Fiber price/throughput review** in the worst
  markets — reprice the premium tier or match delivered speeds to advertised,
  and pair with a retention offer (device/throughput upgrade) for Fiber accounts
  flagged high-risk.
- **Target owner:** Head of Product / Network.
- **Success metric:** reduce Fiber churn to **≤ 27.5%** within 2 quarters;
  recover **$4.1K × Δpp /mo** in MRR.

### 2.3 Bundle Premium Tech Support × Online Security × Device Protection
**Hypothesis:** H4 (Bundled add-ons reduce churn, incl. competitor churn) — *SUPPORTED*.

- **Finding / metric:** all-three bundle churn **7.16%** vs none **35.29%** — a
  **4.9×** reduction. Competitor churn collapses from **15.84%** (none) to
  **3.51%** (all three). Caveat: the support effect only materializes **after
  ~7 months** (largest at 25–36 mo: −10.1 pp).
- **Quantified opportunity:** lifting all-three attach rate toward a wider base
  cuts churn (and the single biggest "why" — competitor churn) for the most
  valuable, service-heavy accounts.
- **Recommended action:** promo-bundle the three add-ons as a single "loyalty"
  SKU, **re-sequenced to established accounts (7+ months tenure)** rather than
  brand-new signups (where the effect is zero).
- **Target owner:** Marketing / Product (pricing & packaging).
- **Success metric:** sustain bundled-customer churn **< 10%**; hold competitor
  churn among bundled customers **< 5%**; increase all-three attach rate.

### 2.4 First-90-day onboarding / retention playbook
**Hypothesis:** H5 (Early-tenure churn velocity ≤ 12 months) — *SUPPORTED*.

- **Finding / metric:** the first **90 days = 31.9% of all churn** (597
  churners); ≤ 12 months churn **59.87%** vs 17.13% for > 12 months; retention
  stabilizes at the **~12-month** tipping point.
- **Quantified opportunity:** 597 customers leave within 3 months — the single
  densest churn block. (Note: the "100% churn" in the 0–3 mo bucket is partly
  definitional — see §4 limitations.)
- **Recommended action:** ship a **day-30/60/90 onboarding playbook** — proactive
  health-check touches, first-quarter term offers, and support hand-off for
  at-risk signups.
- **Target owner:** Customer Success / Onboarding.
- **Success metric:** cut first-90-day churn by **30%**; reduce the 0–12 mo
  cohort churn from 59.9% to **< 40%**.

### 2.5 Regional strike team for San Diego
**Hypothesis:** Infrastructure & regional disparity (Stage 4 §5.2) — *SUPPORTED*.

- **Finding / metric:** San Diego is the worst city (**66.5%** churn, 185/278);
  top-5 zips are all San Diego — 92122 **97.1%**, 92130 **95.2%**, 92109
  **88.9%** — a Fiber-heavy urban cluster.
- **Quantified opportunity:** churn is geographically concentrated, not diffuse;
  a field push in one MSA attacks the single densest churn cluster.
- **Recommended action:** stand up a **San-Diego field-marketing + field-service
  strike team** (Fiber-centric), with localized retention offers and network
  triage in the >85%-churn zips.
- **Target owner:** Regional GM / Field Operations.
- **Success metric:** reduce San Diego city churn from 66.5% toward the 28.4%
  overall; bring the top-5 zips below **50%**.

### 2.6 Competitor-response program
**Hypothesis:** H6 (Competitor churn is dominant; device/offer reasons lead) — *SUPPORTED*.

- **Finding / metric:** Competitor = **45.0% of all churn** (841/1,869); top
  reasons are "Competitor had better devices" (**313**) and "Competitor made
  better offer" (**311**), plus more-data (117) and higher-speed (100) reasons.
- **Quantified opportunity:** 841 customers left for a competitor — the largest
  single churn category and the most directly addressable via device/offer
  parity.
- **Recommended action:** launch a **device-refresh program** and **competitor
  offer-matching** playbook (targeted at offer `E` accounts flagged at 67.6%
  churn, and Fiber/urban markets), plus proactive "we'll match it" retention
  messaging.
- **Target owner:** CMO / Retention Marketing.
- **Success metric:** reduce competitor share of churn from 45% to **< 35%**;
  cut device/offer reason counts by **20%**.

---

## 3. Measurement & next steps

- **Complete the LTV:CAC equation.** Gather the two missing finance inputs —
  **total S&M spend** and **new customers acquired** — to compute CAC and
  LTV:CAC, and validate against the healthy **≥ 3:1** benchmark. Confirm the
  default **0.50 gross margin** with finance.
- **Model refresh cadence.** Retrain the churn model (LR AUC 0.912 / RF AUC
  0.921) each **quarter** as new snapshots land; re-run feature importance to
  track whether `contract_commitment`, `tenure_months`, and `num_referrals`
  remain the top drivers.
- **A/B test plan.** Run controlled experiments (holdout vs treatment) on each
  intervention: (a) M2M → One-Year migration offer, (b) Fiber price/throughput
  retune, (c) three-add-on bundle promo (established accounts), (d) day-30/60/90
  onboarding touches. Primary metric = **churn**; secondary = **MRR retained**,
  with 2-quarter readouts.
- **Instrumentation gap.** The dataset has **no support-ticket column** — begin
  capturing ticket/contact data so the "support experience" proxies
  (`premium_tech_support`, attitude-related `churn_reason`) can be replaced by
  real interaction signals.

## 4. Limitations

1. **Revenue-at-risk is an upper bound.** It assumes every churned dollar is lost
   for the full 12/24/36-month horizon with no within-window churn probability
   and no discounting. Treat as a ceiling, not NPV.
2. **Churn is a point-in-time snapshot** (end of Q2 2022), not longitudinal.
   Cohort retention is cross-sectional, not a true survival curve.
3. **The 0–3-month "100% churn" is partly definitional** — `Stayed` customers
   have `tenure_months ≥ 4`, so every *existing* customer with ≤ 3 months tenure
   is, by construction, churned. The first-90-day window is still the densest
   block, but the 100% figure is not a measured hazard.
4. **No support-ticket column** — support-touch findings rely on proxy flags.
5. **`tenure_months` / `total_charges` dominate feature importance** partly for
   mechanical reasons; actionable drivers are the behavioral features (contract,
   referrals, price, support, add-ons).
6. **CLV/CAC not fully computable** without external finance inputs (gross margin
   default 0.50; CAC external).
7. **120 negative `monthly_charge` values** (billing credits) are retained; they
   marginally depress MRR impact and are documented, not dropped.
