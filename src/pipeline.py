"""
Orchestrates the entire ETL pipeline: Extract → Transform → Validate → Load.
Acts as the main entry point when running the full workflow.

How it fits the pipeline
- Combines all individual steps into a single executable script.
- Ensures clean execution order and consistent logging across stages.
- Cloud-ready: the Load step can optionally upload curated data to AWS S3.
"""

from src.extract import extract_sample
from src.transform import transform
from src.validate import validate_data
from src.load import load_to_curated
from src.config import CFG
from src.logging_config import setup_logging
from pathlib import Path


def run_pipeline():
    """Main ETL pipeline controller."""
    logger = setup_logging("pipeline")
    logger.info("Starting full ETL pipeline")

    # Step 1: Extract
    raw_path = CFG.raw_dir / "train.gz"
    sample_path = CFG.samples_dir / "train_sample.csv"
    logger.info("Step 1: Extracting sample data...")
    extract_sample(raw_path, sample_path, CFG.sample_rows)

    # Step 2: Transform
    staged_path = CFG.staged_dir / "train_transformed.csv"
    logger.info("Step 2: Transforming sample data...")
    transform(sample_path, staged_path)

    # Step 3: Validate
    logger.info("Step 3: Validating transformed data...")
    validate_data(staged_path)

    # Step 4: Load (with optional cloud upload)
    curated_path = CFG.curated_dir / "train_curated.parquet"
    logger.info("Step 4: Loading curated dataset...")
    load_to_curated(staged_path, curated_path, logger, upload_cloud=True)

    logger.info("✅ ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()