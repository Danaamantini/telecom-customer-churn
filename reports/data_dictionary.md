# Data dictionary

The source grain is one row per customer. The raw file contains 38 fields;
the pipeline appends five transparent analytical fields.

## Source field groups

| Group | Fields | Notes |
|---|---|---|
| Identity | `customer_id` | Unique customer key |
| Demographics | `gender`, `age`, `married`, `num_dependents` | Customer profile |
| Geography | `city`, `zip_code`, `latitude`, `longitude` | California location |
| Relationship | `num_referrals`, `tenure_months`, `offer` | Tenure and acquisition |
| Phone | `phone_service`, `avg_monthly_long_distance_charges`, `multiple_lines` | Empty service values become zero/false |
| Internet | `internet_service`, `internet_type`, `avg_monthly_gb_download` | `internet_type` remains null without internet |
| Add-ons | security, backup, protection, support, streaming and unlimited-data flags | Yes/No converted to boolean |
| Billing | `contract`, `paperless_billing`, `payment_method` | Commercial relationship |
| Revenue | `monthly_charge` and six accumulated charge/revenue fields | Negative monthly charges are retained |
| Outcome | `customer_status`, `churn_category`, `churn_reason` | Reasons are null for non-churned customers |

The exact raw-header mapping is versioned in `src/config.py` and is the
machine-readable source of truth.

## Engineered fields

| Field | Type | Definition |
|---|---|---|
| `churn` | boolean | `customer_status == 'Churned'` |
| `tenure_group` | string | `0-12`, `13-24`, `25-36`, `37-48`, `49-60`, `61+` months |
| `contract_commitment` | integer | Month-to-Month=0, One Year=1, Two Year=2 |
| `bundle_count` | integer | Count of eight subscribed internet add-ons, from 0 to 8 |
| `is_fiber` | boolean | Internet type is Fiber Optic |

`Joined` customers are retained in the dataset but excluded from churn-rate
denominators because they form a distinct acquisition cohort.
