# src/config.py
"""
Why this module exists
----------------------
Single source of truth for paths and a few knobs. No business logic here.
Keeps the rest of the code clean and free from hard-coded relative paths.

How it fits the pipeline
- Extract: tells us where raw gz lives and where to drop sample parquet.
- Transform: where to read staged/sample and write curated outputs.
- Load: destination folder (local now; can be swapped to cloud later).

Rule of thumb: if another module needs a path or small constant, import from here.
"""

from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Config:
    # project root = repo root (this file is in src/, so parents[1])
    project_root: Path = Path(__file__).resolve().parents[1]

    # data layout
    data_dir: Path = project_root / "data"
    raw_dir: Path = data_dir / "raw"
    samples_dir: Path = data_dir / "samples"
    staged_dir: Path = data_dir / "staged"
    curated_dir: Path = data_dir / "curated"

    # default raw file names (can be overridden by CLI later)
    train_gz: Path = raw_dir / "train.gz"
    test_gz: Path = raw_dir / "test.gz"

    # small sample size for local dev; use env to tweak without code edits
    sample_rows: int = int(os.getenv("SAMPLE_ROWS", "10000"))

    def ensure_dirs(self) -> None:
        """Create the standard data folders if they don't exist. Cheap and safe."""
        for p in (self.raw_dir, self.samples_dir, self.staged_dir, self.curated_dir):
            p.mkdir(parents=True, exist_ok=True)

# Public, importable config instance
CFG = Config()