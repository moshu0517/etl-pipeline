# create_structure.py (final version)
"""
Bootstraps the entire ETL pipeline folder layout.
Creates standard directories and placeholder files — including README.md.

How it fits the pipeline
- Run once to initialize the project.
- Keeps repo layout consistent and reproducible.
"""

from pathlib import Path

folders = [
    "src",
    "data/raw",
    "data/samples",
    "data/staged",
    "data/curated",
    "tests"
]

files = [
    "src/__init__.py",
    "src/io_utils.py",
    "src/extract.py",
    "src/transform.py",
    "src/validate.py",
    "src/load.py",
    "src/pipeline.py",
    "tests/test_validate.py",
    ".gitignore",
    "requirements.txt",
    ".env.example",
    "README.md" 
]

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

for file in files:
    Path(file).touch(exist_ok=True)

print("✅ Project structure created successfully!")