# Data setup

The project uses the public **Maven Analytics Telecom Customer Churn** dataset
(7,043 customers, 38 source columns). The source files are not committed to
Git because they are third-party data.

Download the [Maven Analytics Telecom Customer Churn dataset](https://mavenanalytics.io/data-playground/telecom-customer-churn)
and place the main customer file at:

```text
data/raw/telecom_customer_churn.csv
```

The pipeline expects the original human-readable headers, including
`Customer ID`, `Tenure in Months`, `Monthly Charge`, and `Customer Status`.
It validates the complete 38-column contract before creating any output.

Run from the repository root:

```bash
python run_pipeline.py
```

Generated files:

```text
data/processed/clean_customers.csv
data/processed/churn.duckdb
```

Both are reproducible outputs and are intentionally ignored by Git. A small
synthetic dataset under `tests/fixtures/` is committed only for automated tests.
