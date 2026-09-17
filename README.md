# Telecom Customer Churn Analysis

[![tests](https://github.com/Danaamantini/telecom-customer-churn/actions/workflows/tests.yml/badge.svg)](https://github.com/Danaamantini/telecom-customer-churn/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/SQL-DuckDB-FFF000)](https://duckdb.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Reproducible analysis of customer churn for a fictional California telecom
provider. The project uses Python for data preparation, SQL for business
metrics, Tableau for presentation, and one interpretable logistic-regression
exercise.

## Business question

Which customer segments are most associated with churn, how much recurring
revenue is attached to churned customers, and which retention actions should be
tested first?

## Key findings

Results below are reconciled against the complete 7,043-row source dataset:

| Metric | Result |
|---|---:|
| Existing customers | 6,589 |
| Churned customers | 1,869 |
| Overall churn rate | 28.4% |
| Monthly recurring revenue associated with churn | $137,086.65 |
| Annualized run-rate | $1.65M |
| Month-to-Month churn rate | 51.7% |
| Fiber Optic churn rate | 42.1% |
| Leading churn category | Competitor (45% of churn) |

These are observational associations, not causal effects. Recommendations
should be validated through controlled retention experiments.

## Reproduce the project

Requires Python 3.12 or newer.

```bash
git clone https://github.com/Danaamantini/telecom-customer-churn.git
cd telecom-customer-churn
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Download the public-domain [Maven Analytics Telecom Customer Churn dataset](https://mavenanalytics.io/data-playground/telecom-customer-churn)
and place the main customer CSV at:

```text
data/raw/telecom_customer_churn.csv
```

Then run:

```bash
python run_pipeline.py
pytest -q
```

The pipeline validates the source, creates the 43-column customer table,
exports `data/processed/clean_customers.csv`, builds
`data/processed/churn.duckdb`, and creates the documented SQL views.

Execute the analysis notebooks after the pipeline:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb --output /tmp/01_eda.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_business_analysis.ipynb --output /tmp/02_business_analysis.ipynb
jupyter nbconvert --to notebook --execute notebooks/03_logistic_model.ipynb --output /tmp/03_logistic_model.ipynb
```

## Project structure

```text
data/         source-data instructions and generated outputs
notebooks/    EDA, business analysis, and optional logistic model
src/          canonical preparation and validation pipeline
sql/          KPIs, churn segments, and revenue analysis
tests/        synthetic fixture plus unit/integration tests
reports/      final written analysis and generated figures
dashboard/    Tableau workbook and connection instructions
```

## Method

1. Validate the original 38-column customer file.
2. Convert numeric and Yes/No fields without dropping rows.
3. Create five transparent features: churn, tenure group, contract commitment,
   bundle count, and Fiber flag.
4. Exclude `Joined` customers from churn-rate denominators.
5. Calculate business KPIs and segment comparisons in DuckDB SQL.
6. Treat the logistic model as an explanatory exercise, not a production
   forecast.

See [reports/final_report.md](reports/final_report.md) for findings and
limitations, [reports/data_dictionary.md](reports/data_dictionary.md) for the
data contract, and [dashboard/README.md](dashboard/README.md) for Tableau setup.

## Reproducibility safeguards

- one canonical Python transformation path;
- exact dependency versions;
- fixed validation totals for the full dataset;
- synthetic test data committed to the repository;
- Python and SQL integration tests;
- automated notebook execution in GitHub Actions;
- generated data excluded from version control.

## License

Project code is MIT licensed. The source dataset is listed by Maven Analytics
as public domain and originates from IBM Cognos Analytics.
