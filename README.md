# Avazu CTR Prediction: Production-Grade ETL Pipeline

## About This Project

This project demonstrates how I approach building production-ready ETL pipelines. Having worked with data pipelines in production environments, I wanted to create something that shows the complete workflow—from raw compressed data to clean, validated datasets ready for analysis.

The Avazu Click-Through Rate dataset is a good fit for this demonstration because it's large enough to present real engineering challenges (1.12 GB compressed, over 40 million ad click records) but manageable enough to run on a standard laptop. The focus here is on showing solid engineering practices: modular code structure, proper validation gates, comprehensive logging, and a design that works locally but scales to cloud deployment.

This implementation prioritizes the kind of patterns I've found valuable in real work—clear separation of concerns, reproducible outputs, and code that's straightforward to debug and maintain.

## Repository Structure

```
ETL-Pipeline/
├── data/
│   ├── raw/            # Original compressed files (train.gz, test.gz)
│   ├── samples/        # Lightweight CSV samples for development
│   ├── staged/         # Cleaned and transformed data
│   └── curated/        # Final production-ready Parquet files
│
├── src/
│   ├── config.py           # Centralized configuration
│   ├── logging_config.py   # Logging setup
│   ├── extract.py          # Sampling from compressed source
│   ├── transform.py        # Cleaning and feature engineering
│   ├── validate.py         # Data quality checks
│   ├── load.py             # Parquet conversion and S3 upload
│   └── pipeline.py         # Full ETL orchestration
│
├── requirements.txt
└── README.md
```

The data directory follows a staged architecture pattern—raw data moves through samples, staged, and curated layers, with validation gates between each stage. This makes it easy to inspect data quality at any point and pinpoint where issues arise.

## Getting the Data

The raw dataset files are too large for GitHub (train.gz is 1.12 GB, test.gz is 123 MB). Download them from Google Drive and place them in the `data/raw/` directory:

- **train.gz**: https://drive.google.com/file/d/1icfLa-cmrYVX5fzFVYyMCOukPzy-5cS2/view?usp=drive_link
- **test.gz**: https://drive.google.com/file/d/1_z-xdB9ujYVrVjBF8VjlPDBdSHzn63Yp/view?usp=drive_link

## How the Pipeline Works

The ETL process breaks down into four stages. Each stage can run independently during development, but they're designed to work together as a complete pipeline for production use.

### Stage 1: Extract

The extract stage creates a manageable sample from the full dataset. Working with 40+ million rows during development is impractical—loading the full dataset takes significant time and memory. Instead, this stage reads directly from the compressed gzip file and samples a configurable subset of rows.

By default, it pulls 10,000 rows, which I've found strikes a good balance between being representative of the full dataset and staying lightweight for fast iteration. The sampling is random, which works well for this use case. For production systems where temporal patterns matter, you'd want stratified sampling across time periods, but simple random sampling is sufficient for demonstrating the pipeline workflow.

```bash
python -m src.extract
```

This creates `data/samples/train_sample.csv` (approximately 1.5 MB), ready for the transform stage.

### Stage 2: Transform

The transform stage is where most of the data quality work happens. Raw ad click data comes with the usual issues—inconsistent formatting, duplicates, missing values in unexpected places. This stage standardizes everything and engineers features that will be useful downstream.

Key transformations include parsing timestamp strings into proper datetime objects, extracting temporal features like hour of day and day of week, normalizing categorical variables, and removing exact duplicates. I also filter out rows with invalid or suspicious values rather than passing questionable data downstream.

```bash
python -m src.transform
```

This reads `data/samples/train_sample.csv` and outputs `data/staged/train_transformed.csv`. The transformed file is typically smaller (around 342 KB) because the cleaning process removes noise and duplicates. In production, you'd want to track what percentage of data gets filtered out over time—a sudden spike could indicate upstream data quality problems.

### Stage 3: Validate

The validation stage acts as a quality gate before data moves into the curated layer. It checks three critical areas: schema consistency (do column names and types match what we expect?), completeness (are there unexpected null values?), and uniqueness (are ID fields actually unique?).

```bash
python -m src.validate
```

This might seem like overkill for a portfolio project, but I've seen too many cases where silent data quality issues caused problems later. Better to catch schema drift or data corruption at this stage than discover it when you're debugging model performance. The validation logic is simple now—mostly type checking and assertions—but the structure makes it easy to add more sophisticated checks later, like distribution tests or anomaly detection.

### Stage 4: Load

The load stage converts the validated CSV data into Parquet format and optionally uploads to S3. Parquet makes sense here because it's columnar (faster for analytical queries), handles compression natively, and preserves data types. For this dataset, the compression ratio is roughly 3.8x—the 1.5 MB CSV sample becomes a 391 KB Parquet file.

```bash
python -m src.load \
  --in data/staged/train_transformed.csv \
  --out data/curated/train_curated.parquet
```

The S3 upload is designed to be truly optional. The code checks for boto3 and AWS credentials at runtime and gracefully skips the upload if they're not available. This keeps the pipeline runnable locally without any cloud dependencies.

If you want to enable S3 upload:

```bash
pip install boto3
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
export S3_BUCKET=your-bucket
export S3_PREFIX=avazu/curated
```

### Running the Full Pipeline

The pipeline module chains all four stages together with unified error handling and logging:

```bash
python -m src.pipeline
```

The log output shows clear progress through each stage:

```
2025-10-05 19:04:08 | INFO | Starting full ETL pipeline
2025-10-05 19:04:08 | INFO | Step 1: Extracting sample data...
2025-10-05 19:04:08 | INFO | Loaded 10,000 rows, 24 columns
2025-10-05 19:04:08 | INFO | Step 2: Transforming sample data...
2025-10-05 19:04:08 | INFO | Loaded 10000 rows, 24 cols
2025-10-05 19:04:08 | INFO | After drop duplicates: 10000 rows
2025-10-05 19:04:08 | INFO | Step 3: Validating transformed data...
2025-10-05 19:04:08 | INFO | Schema check passed — all key columns present
2025-10-05 19:04:08 | INFO | No nulls found
2025-10-05 19:04:08 | INFO | All IDs unique
2025-10-05 19:04:08 | INFO | Step 4: Loading curated dataset...
2025-10-05 19:04:09 | INFO | Saved curated dataset (10,000 rows, 36 cols)
2025-10-05 19:04:09 | INFO | ✅ ETL pipeline completed successfully
```

The orchestration is straightforward—sequential function calls with proper error handling. For a single-machine pipeline this is sufficient and easier to debug than more complex frameworks. If you needed formal workflow management, the modular design would integrate cleanly with tools like Airflow or Prefect.

## Technical Decisions

A few choices worth explaining:

**Why sampling instead of processing the full dataset?** The full 1.12 GB file is too large for comfortable local development on a standard laptop. Sampling gives fast iteration cycles with representative data. In production, I'd use chunked processing or a distributed framework like Spark, but that would add complexity that isn't needed for demonstrating the core ETL pattern.

**Why CSV as an intermediate format?** Parquet would be more efficient, but CSV files are human-readable and easy to inspect when debugging. For a portfolio project where someone might want to examine intermediate outputs, the readability matters more than the I/O overhead. In production at scale, you'd use Parquet throughout.

**Why separate validation from transformation?** Keeping them separate makes debugging easier—you can tell immediately whether an issue is in the transformation logic or the validation criteria. It also means you can evolve validation rules independently without touching transformation code.

**What about incremental processing?** This pipeline processes full snapshots. For production with daily refreshes, you'd add incremental logic—tracking which records have been processed and handling late-arriving data. The current architecture could support that with modifications to the extract and load stages, but I prioritized showing clean full-refresh logic first.

## Performance Notes

Processing 10,000 rows takes a few seconds end-to-end on a standard laptop. The bulk of the time goes to the transform stage, particularly pandas operations on categorical columns. For larger datasets, you'd want to consider Polars (which handles large DataFrames more efficiently) or Dask for out-of-core processing.

The Parquet compression achieves approximately 3.8x reduction compared to CSV—a 1.5 MB sample becomes 391 KB. The compression ratio improves with larger datasets due to better dictionary encoding of repeated categorical values.

## Installation and Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/moshu0517/ETL-Pipeline.git
cd ETL-Pipeline
pip install -r requirements.txt
```

Download the raw data files (links above) and place them in `data/raw/`. Then run:

```bash
python -m src.pipeline
```

For first-time users, I recommend running each stage individually to understand the data flow before executing the full pipeline.

## Future Enhancements

This implementation covers the core ETL workflow, but there are natural extensions:

**Incremental processing** would make this efficient for daily refreshes. The current design processes full datasets, but adding delta logic wouldn't require major refactoring—mostly changes to the extract and load stages to handle timestamps and append operations.

**Data quality metrics** could track validation results over time. Right now validation is pass/fail, but logging metrics like null percentages, duplicate counts, and schema changes would help detect gradual data quality degradation.

**Parallel processing** would speed up the transform stage for larger datasets. Using Dask or multiprocessing to parallelize transformations across chunks would be straightforward given the modular design.

**Schema evolution support** would handle backward-compatible changes gracefully. Production systems need to handle new columns being added or types changing without breaking existing pipelines.

The architecture is flexible enough to accommodate these additions without major rewrites.

## Author

**Moshu Huang**  
Data Scientist | Duke University  
GitHub: [@moshu0517](https://github.com/moshu0517)

---

*If you find this project useful, please give it a star and feel free to use it as a reference for your own ETL implementations.*