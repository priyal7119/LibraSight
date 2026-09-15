Data Flow — LibraSight

This document describes the step-by-step data flow in LibraSight, referencing the repository files that implement each stage.

1. Raw source

- File: `data/raw/library_raw_data.csv` — original CSV source containing transaction-level records.

2. Ingestion

- Implemented in `ingestion/ingest.py`.
- Reads the raw CSV into a pandas DataFrame, checks column counts and names against `EXPECTED_COLUMNS`, and returns the DataFrame for downstream tasks.

3. Validation

- Implemented in `validation/validate.py`.
- Performs structural checks (column count, missing columns, duplicates), data-type checks (numeric columns), date parsing and range checks, logical checks (due/return vs checkout), and writes `data/quality/data_quality_report.csv` and `data/quality/rejected_records.csv`.

4. Cleaning & Transformation

- Implemented in `transformation/clean_transform.py`.
- Loads `data/raw/library_raw_data.csv` and `data/quality/rejected_records.csv`, removes rejected and duplicate rows, standardizes text and date formats, converts numeric types, enforces range checks, and writes `data/processed/library_clean.parquet` (PyArrow, Spark-compatible timestamps).

5. PyArrow Parquet

- Output: `data/processed/library_clean.parquet` — canonical cleaned dataset used by Spark and the PostgreSQL loader.

6. PySpark processing

- Implemented in `spark/jobs/library_spark_job.py`.
- Reads the cleaned Parquet, computes analytics (book, genre, reader, branch, collection, yearly/monthly trends, status), prints summaries, and writes analytical Parquet outputs under `spark/output/`.

7. PostgreSQL loading

- Implemented in `database/load_data.py`.
- Uses the cleaned Parquet to create dimension tables and the central `fact_library_transaction` table following a star schema. Writes verification output and enforces uniqueness of `transaction_id` in the fact table.

8. Serving and BI

- FastAPI (`backend/app/`) exposes endpoints (e.g. `/dashboard/summary`) that query the star schema for dashboards.
- React frontend (`frontend/`) consumes the API for the interactive dashboard.
- Power BI (`powerbi/LibraSight.pbix`) and PDF reports are produced from the star schema and report endpoints.
