# Ingestion

Source raw dataset

- `data/raw/library_raw_data.csv` — the authoritative CSV containing transaction-level records used by the pipeline. Do not modify this file.

Ingestion implementation

- File: `ingestion/ingest.py`
- The ingestion code reads the CSV into a pandas DataFrame and performs basic structural checks:
  - Verifies the file exists
  - Confirms the number of columns matches `EXPECTED_COLUMNS`
  - Ensures column names match the expected set
  - Prints row/column counts and a preview of the data

Ingestion output

- Returns a pandas DataFrame for downstream validation.
- No files are written by the ingestion step; the canonical cleaned dataset is produced by the transformation step and saved to `data/processed/library_clean.parquet`.
