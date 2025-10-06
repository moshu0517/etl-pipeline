"""
Handles the Extract part of the ETL.
I just want a clean way to pull raw data (like train.gz) and save a small sample.
This keeps me from loading 1GB+ every time I test transformations.

How it fits the pipeline
- Reads raw data from /data/raw.
- Saves a lightweight sample to /data/samples.
- Used in early dev or debugging before running full-scale jobs.
"""

import pandas as pd
from pathlib import Path
from src.config import CFG
from src.io_utils import ensure_parent_dir


def extract_sample(input_path: Path, output_path: Path, n_rows: int = None) -> None:
    """
    Read a .gz file partially and save a smaller CSV sample.
    Keeps the rest of the pipeline lightweight during dev.
    """
    print(f"📦 Reading from: {input_path}")
    ensure_parent_dir(output_path)

    # Read in chunks to avoid memory issues
    df = pd.read_csv(input_path, compression='gzip', nrows=n_rows)
    print(f"✅ Loaded {len(df):,} rows, {df.shape[1]} columns")

    df.to_csv(output_path, index=False)
    print(f"💾 Saved sample to: {output_path}")


if __name__ == "__main__":
    CFG.ensure_dirs()

    # Define source and target paths
    input_path = CFG.train_gz
    output_path = CFG.samples_dir / "train_sample.csv"

    extract_sample(input_path, output_path, CFG.sample_rows)
    
if __name__ == "__main__":
    # Extract train sample
    input_path = CFG.train_gz
    output_path = CFG.samples_dir / "train_sample.csv"
    extract_sample(input_path, output_path, CFG.sample_rows)

    # Extract test sample (optional but recommended)
    input_path = CFG.test_gz
    output_path = CFG.samples_dir / "test_sample.csv"
    extract_sample(input_path, output_path, CFG.sample_rows)
    