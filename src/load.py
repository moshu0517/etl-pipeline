"""
Handles the final Load step in the ETL pipeline.
Moves cleaned data from staged → curated layer and logs completion.

How it fits the pipeline
- Takes staged (transformed) data as input.
- Saves curated version (e.g., parquet or CSV) for downstream modeling.
- Optionally uploads curated data to AWS S3 (cloud-ready design).
"""

import pandas as pd
from pathlib import Path
from src.logging_config import setup_logging

# --- Optional AWS integration ---
try:
    import boto3
    from botocore.exceptions import NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


def upload_to_s3(local_path: Path, bucket_name="etl-demo-bucket", key_prefix="curated/", logger=None) -> None:
    """Optional AWS S3 upload step (safe to skip if no credentials)."""
    if not AWS_AVAILABLE:
        if logger:
            logger.warning("boto3 not installed — skipping S3 upload.")
        return

    try:
        s3 = boto3.client("s3")
        key = key_prefix + local_path.name
        s3.upload_file(str(local_path), bucket_name, key)
        if logger:
            logger.info(f"Uploaded {local_path.name} to s3://{bucket_name}/{key}")
    except NoCredentialsError:
        if logger:
            logger.warning("AWS credentials not found — skipping upload (demo mode).")
    except Exception as e:
        if logger:
            logger.error(f"S3 upload failed: {e}")


def load_to_curated(in_path: Path, out_path: Path, logger=None, upload_cloud: bool = True) -> None:
    """Load staged data into curated layer, log metadata, and optionally upload to cloud."""
    if logger is None:
        logger = setup_logging("load")

    logger.info(f"Loading {in_path.name} → {out_path.name}")

    # Load staged data
    df = pd.read_csv(in_path)

    # Save curated data
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved curated dataset to: {out_path} ({len(df):,} rows, {len(df.columns)} cols)")

    # Optional cloud upload
    if upload_cloud:
        upload_to_s3(out_path, logger=logger)