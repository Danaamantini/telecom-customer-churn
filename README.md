# Telecom Customer Churn — Analytics Portfolio

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tableau](https://img.shields.io/badge/Tableau-E97627?logo=tableau&logoColor=white)](https://public.tableau.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

End-to-end **customer churn analysis** for a California telecom provider
(7,043 residential customers, end of Q2 2022). The project runs from raw CSV
ingestion through SQL transformation, exploratory analysis, and churn modeling,
and finishes with four executive **Tableau dashboards**.

> **Live dashboard:** *(Tableau Public link — coming soon)*
>
> <!-- Uncomment once the demo GIF is recorded:
> ![Demo](reports/demo.gif)
> -->

## Key findings

| KPI | Value |
|-----|-------|
| Overall churn rate | **28.4%** (1,869 of 6,589 existing customers) |
| MRR at risk | **$137,087 / month** |
| Annualized revenue at risk | **$1.65M** (12m) · **$3.29M** (24m) · **$4.94M** (36m) |
| Churn by contract | Month-to-Month **51.7%** · One-Year 10.9% · Two-Year 2.6% |
| Churn by internet type | Fiber Optic **42.1%** · Cable 27.5% · DSL 20.0% |
| Churn by payment method | Mailed Check **41.4%** · Credit Card 15.8% |
| Retention driver | 3 add-ons (security + backup + device protection) → **7.2%** vs none 35.3% |
| Top churn category | **Competitor** — 45% of all churn |
| Model (5-fold CV ROC-AUC) | Random Forest **0.927** · Logistic Regression **0.914** |

## Dashboards (Tableau)

Four interactive dashboards, specified in `reports/tableau/`:

1. **Churn Overview** — churn rate by contract, internet type, payment method, tenure, and offer.
2. **Revenue at Risk** — dollar impact across 12/24/36-month horizons, by contract.
3. **Retention Drivers** — add-on bundling, feature importance, and early-tenure stickiness.
4. **Regional & Infrastructure** — ZIP-level choropleth plus fiber-vs-other hotspots.

## Architecture

```
data/raw/  ──►  data/interim/  ──►  data/processed/  ──►  sql/views/  ──►  Tableau
 (CSV)         (typed/clean)        (feature-engineered)   (BI marts)      (dashboards)
```

- **Ingestion & validation** — `src/data/` (Python): lossless staging, type coercion, and validation.
- **SQL layering** — `sql/schemas/`, `sql/transformations/`, `sql/views/` (DuckDB), all reading from the canonical table `analytics.clean_customers`.
- **Modeling** — `notebooks/04_feature_importance.ipynb`: 5-fold stratified CV (RF + LR) plus permutation importance.

## Repository structure

```
├── notebooks/          # 01_eda → 05_storytelling (executed)
├── sql/
│   ├── schemas/        # canonical DDL
│   ├── transformations/# type casting + feature engineering
│   └── views/          # 11 analytical BI views
├── src/                # reusable Python (config, ingestion, validation, io)
├── tests/              # pytest suite (18 tests)
├── reports/
│   ├── insights/       # data dictionary, findings, recommendations
│   ├── figures/        # saved charts (PNG)
│   └── tableau/        # data sources, calculated fields, dashboards, .twb
└── PIPELINE.md         # full reproduction walkthrough
```

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then follow `PIPELINE.md` for the full end-to-end reproduction (ingestion →
SQL layering → validation → notebooks). Data files are **not** committed (see
`.gitignore`); the dataset is the public **Maven Analytics "Telecom Customer
Churn"** playground dataset.

## License

MIT — see [LICENSE](LICENSE).
