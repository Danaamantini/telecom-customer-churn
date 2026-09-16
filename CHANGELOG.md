# Changelog

All notable changes to this project are documented here, grouped by work phase
and type (`feat` / `fix` / `docs` / `chore`). Entries are appended newest-first
under the relevant phase.

The format follows the repo's atomic-commit convention
`<type>(<NNN>): <summary>`, where `<NNN>` maps to the numbered work phase.

## Unreleased

### Phase 6 — Hardening & Final Deliverables

- **test (006)** — Add 18-unit-test `pytest` suite covering `src/` (`config`,
  `io`, `ingestion` coercion, `validation`); all pass.
- **feat (006)** — Harden the churn model with 5-fold stratified CV (RF AUC
  0.9267 ± 0.0052; LR 0.9135 ± 0.0048) + permutation importance
  (`reports/insights/model_validation.md`).
- **feat (006)** — Generate a valid Tableau workbook starter
  (`reports/tableau/telecom_churn_dashboard.twb`; 4 dashboards, 7 calculated
  fields).

### Phases 2–5 — Analysis & Storytelling (complete)

- **feat (002)** — EDA: hygiene profile, distributions, correlations, and
  descriptive test of 6 hypotheses (overall churn 28.4%; M2M 51.7%; Fiber
  42.1%; all-three add-on bundle 7.2% vs none 35.3%; ≤12-mo 59.9%; competitor
  45%). `reports/insights/eda_findings.md` + 8 figures + executed notebook.
- **feat (003)** — Materialize `data/interim/` + `data/processed/`; validate
  `analytics.clean_customers` (7,043 × 43) end-to-end.
- **feat (004)** — In-depth analysis: revenue leakage (12/24/36-mo =
  $1.65M/$3.29M/$4.94M; M2M 86.6%), feature importance (RF AUC 0.921), cohort
  retention + risk matrix, tipping point (~12 mo), regional disparities (San
  Diego hotspot). `analysis_findings.md` + 6 figures + 2 notebooks +
  `sql/views/060_revenue_leakage.sql` + `070_regional_churn.sql`.
- **docs (005)** — Finalize Tableau specs (data sources, calculated fields, 4
  dashboard wireframes) and author `reports/insights/recommendations.md` (6
  recommendations tied to validated hypotheses).

### Phase 1 — Setup, Ingestion & Project Blueprint

- **feat** — Scaffold the enterprise directory layout (`data/`, `notebooks/`,
  `sql/`, `reports/`, `src/`) with `.gitkeep` placeholders and `.gitignore`
  rules that keep raw/interim/processed data, `.venv/`, `__pycache__/`, `*.log`,
  and `.env` out of version control.
- **feat** — Define the canonical 38-column schema (`analytics.clean_customers`)
  with `sql/schemas/` DDL, boolean/empty-cell coercion (no silent data loss),
  `sql/transformations/` DML (feature engineering), and `sql/views/` BI
  templates.
- **docs** — Author the extended analytical questions
  (`reports/insights/analytical_questions.md`) and the project blueprint
  documentation (`PIPELINE.md`, `REPO_TOUR.md`).
- **docs** — Add the 5-phase project roadmap and scaffolding (`001`–`005`).
- **chore** — Add `requirements.txt` and starter `src/` modules
  (`src/data/`, `src/utils/`).

### Schema correction (phase 1)

- **fix** — Correct the schema from the initially assumed 21-column IBM Telco
  schema to the real Maven Analytics **38-column** dataset (California
  geography, churn category/reason, referrals, offers, revenue detail). Target
  is `customer_status` (`Churned`/`Stayed`/`Joined`), not a binary flag.
- **feat** — Stage the raw CSV (`data/raw/telecom_customer_churn.csv`, 7,043
  rows × 38 cols) plus `telecom_zipcode_population.csv` and
  `telecom_data_dictionary.csv`; validate the full SQL chain end-to-end
  (churn = 1,869; Joined = 454; MRR impact = $137,086.65/mo).
- **feat** — Enable regional analysis via `city`/`zip_code`/`latitude`/
  `longitude` + zip-code population join.
