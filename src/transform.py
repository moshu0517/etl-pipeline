"""
Handles all data transformation steps in the ETL pipeline.
Cleans, parses, and enriches raw samples before loading to staged layer.

How it fits the pipeline
- Runs after extract.py creates sample CSVs.
- Parses date/time, adds features, removes duplicates.
- Saves cleaned data as parquet files to /data/staged.
"""

import pandas as pd
from pathlib import Path
import argparse
from src.config import CFG
from src.logging_config import setup_logging

# set up logger once — consistent across modules
logger = setup_logging("transform")


def transform(in_path: Path, out_path: Path) -> None:
    """Main transformation logic: read -> clean -> enrich -> save."""
    logger.info(f"🚀 Transforming {in_path.name} -> {out_path.name}")

    # 1. Load dataset
    df = pd.read_csv(in_path)
    logger.info(f"Loaded {len(df):,} rows and {len(df.columns)} columns")

    # 2. Parse hour and create time-related features
    if "hour" in df.columns:
        df["hour"] = pd.to_datetime(df["hour"], errors="coerce")
        df["hour_of_day"] = df["hour"].dt.hour.fillna(-1).astype(int)
        df["weekday"] = df["hour"].dt.weekday.fillna(-1).astype(int)

    # 3. Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"Removed {before - len(df):,} duplicate rows")

    # 4. Save the cleaned data to parquet
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    logger.info(f"✅ Saved cleaned file to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run data transformation step")
    parser.add_argument("--in", dest="input", required=True, help="Input CSV file")
    parser.add_argument("--out", dest="output", required=True, help="Output parquet file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    transform(input_path, output_path)