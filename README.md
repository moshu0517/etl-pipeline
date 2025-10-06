# Avazu CTR — Local-first, Cloud-ready ETL Pipeline

This project builds a **production-style ETL pipeline** for the Avazu Click-Through Rate dataset.  
It demonstrates the full data engineering workflow — **Extract → Transform → Validate → Load (ETL)** — implemented in Python.

The pipeline is designed to:
- Run fully locally with reproducible outputs.
- Be cloud-ready — capable of uploading curated data to AWS S3 (optional, no cost required).
- Showcase clean modular structure, logging, and data quality validation.

*Author: Moshu Huang*  
*If you share or fork this project, please credit the author and link back to this repository.*

## 📁 Repository Structure

The project follows a **modular, production-style** layout:

```text
ETL-Pipeline/
├── data/
│   ├── raw/            # Original compressed data (.gz)
│   ├── samples/        # Small sample CSVs for quick testing
│   ├── staged/         # Cleaned + transformed intermediate files
│   └── curated/        # Final curated Parquet files (optionally uploaded to S3)
│
├── src/
│   ├── config.py           # Path configs & runtime parameters
│   ├── logging_config.py   # Centralized logging setup
│   ├── extract.py          # Reads raw.gz → sample CSV
│   ├── transform.py        # Cleans + features → staged CSV
│   ├── validate.py         # Schema/nulls/ID checks
│   ├── load.py             # Writes curated parquet (+ optional S3 upload)
│   └── pipeline.py         # Orchestrates ETL: Extract→Transform→Validate→Load
│
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
└── .gitignore              # Ignore large/raw artifacts