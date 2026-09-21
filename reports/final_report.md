# Customer churn — final analysis

## Executive summary

The snapshot contains 7,043 customers: 4,720 stayed, 1,869 churned, and 454
recently joined. Excluding the acquisition cohort, observed churn is **28.4%**.
The churned customers account for **$137,086.65 in monthly revenue**, equal to
**32.0%** of the monthly revenue associated with existing customers.

The largest decision signal is not simply the size of the Month-to-Month base.
Month-to-Month and committed contracts have similar existing-customer counts
(3,202 versus 3,387), but Month-to-Month accounts for 1,655 churns versus 214
for One Year and Two Year combined.

## Main findings

### Contract risk

Month-to-Month customers have a 51.7% churn rate, compared with 10.9% for One
Year and 2.6% for Two Year. The committed-contract rate is 6.3% when One Year
and Two Year are combined. Month-to-Month customers represent 48.6% of the
existing base but 88.6% of all churned customers.

Contract choice is associated with churn, but customers self-select into
contracts. The comparison does not estimate the causal effect of converting an
account to a longer commitment.

### Revenue exposure

Existing customers account for $428,487.25 in monthly revenue. Churned accounts
account for $137,086.65. The annualized $1.65M figure is only a simple run-rate
(`monthly revenue × 12`), not profit, margin, net present value, or a forecast.

Customers with monthly charges of at least $90.40 contribute $55,400.55, or
40.4%, of the monthly revenue associated with churn. This identifies a revenue
protection population; it does not imply that higher charges cause churn.

### Priority segment

The most actionable concentration is Fiber Optic, Month-to-Month, and tenure
from 4 through 24 months. Among 807 existing customers in this intersection,
496 churned. The resulting churn rate is 61.5%, and the churned customers carry
$42,417.50 in monthly revenue.

Within this segment, competitor reasons account for 239 churns (48.2%).
Dissatisfaction and attitude are grouped as service experience and account for
175 churns (35.3%). Price accounts for 43 (8.7%), and all remaining categories
account for 39 (7.9%). Competition and service experience therefore explain
83.5% of reported churn in the priority segment.

### Secondary geographic diagnostic

ZIP3 `921` has 287 existing customers and 188 churns, a 65.5% churn rate.
Competitor reasons account for 153 of those churns, and 147 mention an offer.
This is a localized competitor-offer signal. Geography remains secondary in
the dashboard because ZIP areas can proxy for market conditions, product mix,
or service differences and are not causal explanations by themselves.

## Recommended retention tests

### 1. Redesign Offer E

Offer E has 426 churns among 630 existing customers, a 67.6% observed churn
rate. The current non-churned population contains 379 customers and $17,553.85
in monthly revenue. Test a redesigned offer against a comparable holdout group.

### 2. Protect high-value Month-to-Month customers

There are 291 `Stayed` Month-to-Month customers with monthly charges of at
least $90.40. They represent $28,814.85 in current monthly revenue. Test a
targeted protection treatment rather than applying a blanket discount.

### 3. Test proactive Fiber support

The combination of Fiber Optic, Month-to-Month, tenure from 4 through 24
months, and no premium tech support appears among 438 prior churns. There are
253 matching `Stayed` customers with $20,388.05 in monthly revenue. Test a
proactive support intervention with treatment and control groups.

The three action cohorts overlap. They are separate experiment candidates, not
additive customer or revenue totals.

## Limitations

- The data is a single historical snapshot, not a longitudinal event table.
- Associations between services, contracts, location, and churn are not causal
  effects.
- Reported churn reasons exist only for churned customers and may reflect
  customer or agent categorization.
- Monthly revenue is not profit; costs, margin, discounts, and intervention
  expense are absent.
- The annualized figure assumes the observed monthly amount persists for twelve
  months and is not an NPV calculation.
- Support interactions, network-quality measures, marketing cost, and gross
  margin are absent.
- The logistic model uses random cross-validation on the same snapshot and does
  not estimate future-quarter performance.
