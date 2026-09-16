# data/raw/ — Raw dataset landing zone

This directory is **gitignored** (see repo-root `.gitignore`): raw data files
are **never** committed to version control. Only the `.gitkeep` placeholder is
tracked so the directory survives a fresh clone.

## Staged files (flat canonical names)

| File | Role |
|------|------|
| `telecom_customer_churn.csv` | Main dataset — 7,043 rows × 38 columns (customer-level churn snapshot) |
| `telecom_zipcode_population.csv` | Zip Code → Population join table (1,671 zip codes) for regional enrichment |
| `telecom_data_dictionary.csv` | Upstream field-level data dictionary (table, field, description) |

The three files are staged under `data/raw/` directly (not in the original
`Telecom+Customer+Churn/` subfolder) at these exact flat paths:

```
data/raw/telecom_customer_churn.csv
data/raw/telecom_zipcode_population.csv
data/raw/telecom_data_dictionary.csv
```

These are the exact paths `src/data/config.py` (`RAW_CSV_PATH`,
`ZIPCODE_POPULATION_PATH`, `DATA_DICTIONARY_PATH`) and
`sql/schemas/001_raw_staging.sql` / `sql/transformations/010_type_casting.sql`
expect.

## Rules

- Raw files are **immutable** — never edit them in place.
- All downstream artifacts are written to `data/interim/` and
  `data/processed/`, never back into `data/raw/`.
- If the source file uses a different name, either rename it to the canonical
  filename above or update `RAW_CSV_FILENAME` (and siblings) in
  `src/data/config.py`.
