"""
Performs data validation after the Transform step.
Ensures data quality before loading to curated layer.

How it fits the pipeline
- Runs right after transform.py finishes writing staged data.
- Checks schema consistency, missing values, and type integrity.
- Logs detailed summary for debugging and audit trail.
"""

import pandas as pd
from pathlib import Path
import argparse
from src.config import CFG
from src.logging_config import setup_logging

logger = setup_logging("validate")


def validate_data(in_path: Path) -> None:
    """Run basic data quality checks on the staged dataset."""
    logger.info(f"🔍 Validating dataset: {in_path.name}")

    # 1. Load the transformed file
    df = pd.read_csv(in_path) if in_path.suffix == ".csv" else pd.read_parquet(in_path)
    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")

    # 2. Basic schema checks
    expected_cols = ["id", "click", "hour", "banner_pos"]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        logger.warning(f"⚠️ Missing columns: {missing_cols}")
    else:
        logger.info("✅ Schema check passed — all key columns present")

    # 3. Null value summary
    null_counts = df.isnull().sum()
    null_report = null_counts[null_counts > 0]
    if not null_report.empty:
        logger.warning(f"⚠️ Found null values:\n{null_report}")
    else:
        logger.info("✅ No nulls found")

    # 4. Type checks (simple version)
    for col in ["id", "click"]:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"⚠️ Column {col} is not numeric")

    # 5. Optional sanity check: unique IDs
    if "id" in df.columns:
        dup_ids = df["id"].duplicated().sum()
        if dup_ids > 0:
            logger.warning(f"⚠️ Found {dup_ids} duplicated IDs")
        else:
            logger.info("✅ All IDs unique")

    logger.info("🏁 Validation completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run validation checks on staged data")
    parser.add_argument("--in", dest="input", required=True, help="Path to staged CSV or Parquet file")
    args = parser.parse_args()

    input_path = Path(args.input)
    validate_data(input_path)