"""Command-line entry point for the complete project pipeline."""

import argparse
from pathlib import Path

from src.config import DATABASE_PATH, PROCESSED_DATA_PATH, RAW_DATA_PATH
from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the churn analysis dataset and DuckDB views.")
    parser.add_argument("--raw", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--processed", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument("--database", type=Path, default=DATABASE_PATH)
    parser.add_argument(
        "--no-reference-checks",
        action="store_true",
        help="Skip full-dataset row and KPI checks (intended for synthetic test data).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_pipeline(
        raw_path=args.raw,
        processed_path=args.processed,
        database_path=args.database,
        strict_reference_checks=not args.no_reference_checks,
    )
    processed = result["processed"]
    print(f"✓ Raw data loaded: {result['raw']['rows']:,} rows × {result['raw']['columns']} columns")
    print(f"✓ Clean dataset created: {processed['rows']:,} rows × {processed['columns']} columns")
    print(f"✓ Churned customers: {processed['churned']:,}")
    print(f"✓ Joined customers: {processed['joined']:,}")
    print(f"✓ Overall churn rate: {processed['churn_rate']:.2%}")
    print(f"✓ Clean CSV exported to {result['output_path']}")
    print("✓ DuckDB database and analytical views created")


if __name__ == "__main__":
    main()
