# Customer churn — final analysis

## Executive summary

The snapshot contains 7,043 customers: 4,720 stayed, 1,869 churned, and 454
recently joined. Excluding the acquisition cohort, observed churn is **28.4%**.
Churn is concentrated among Month-to-Month customers, Fiber Optic customers,
early-tenure accounts, and customers paying by mailed check.

The monthly charges attached to churned customers total **$137,086.65**. The
annualized figure of approximately **$1.65M** is a simple run-rate (`MRR × 12`),
not a discounted revenue forecast.

## Main findings

### Contract

Month-to-Month customers show a 51.7% churn rate, compared with 10.9% for One
Year and 2.6% for Two Year contracts. Contract choice is strongly associated
with churn, but customers self-select into contracts; the gap is not a causal
estimate of converting an account.

### Internet service

Fiber Optic customers show 42.1% churn, compared with 27.5% for Cable and 20.0%
for DSL. This motivates investigation of Fiber pricing, delivered service, and
local market competition.

### Customer tenure

Churn is highest among newer customers. Because this is a cross-sectional
snapshot rather than customer-level event history, the result is described as
“churn by tenure group,” not a survival or cohort-retention curve.

### Churn reasons

Competitor-related reasons represent 45% of churn. Better devices and better
offers are the most common specific competitor reasons, supporting targeted
offer testing rather than a blanket discount.

### Recurring revenue

Churned accounts carry $137,086.65 in observed monthly charges. Negative
monthly-charge records are retained because they appear to represent credits;
the pipeline reports rather than silently removes them.

## Recommended experiments

1. Test a targeted One Year migration offer for high-risk Month-to-Month
   customers against a holdout group.
2. Investigate Fiber price and service quality in high-churn markets before
   changing the full product.
3. Test structured onboarding contacts during the first 90 days.
4. Test competitor offer matching only for customers showing relevant risk
   signals.

Primary outcomes should be churn and retained monthly revenue. Each experiment
needs a control group so the incremental effect can be separated from customer
self-selection.

## Limitations

- The data is a single historical snapshot, not a longitudinal event table.
- Associations between services, contracts, and churn are not causal effects.
- The annualized revenue metric assumes the observed churned MRR persists for
  twelve months and is not an NPV calculation.
- Support interactions, network quality, marketing cost, and gross margin are
  absent.
- The logistic model uses random cross-validation on the same snapshot and
  therefore does not estimate future-quarter performance.
