# Transformation

Transformation prepares a clean, analysis-ready Parquet file used by Spark and the PostgreSQL loader.

Implemented in: `transformation/clean_transform.py`

Key steps

- Load raw CSV and `data/quality/rejected_records.csv`.
- Remove rejected records and exact duplicate rows.
- Remove duplicate `transaction_id` rows keeping the first occurrence (deterministic choice).
- Convert numeric columns to appropriate numeric types (`age`, `publication_year`, `branch_capacity`, `renewal_count`, `reservation_count`, `fine_amount`, `total_copies`, `available_copies`).
- Parse and normalize dates (`membership_date`, `checkout_date`, `due_date`, `return_date`).
- Clean and trim text columns.
- Standardize categorical values (e.g., `gender`, `reservation_flag`).
- Enforce final quality checks (no duplicate transaction IDs, valid age/publication year, non-negative numeric values, date logical checks).
- Prepare timestamp units compatible with Spark (`.dt.as_unit("us")`) to ensure Parquet compatibility.

Output

- `data/processed/library_clean.parquet` — clean, Spark-friendly Parquet file (PyArrow engine, microsecond timestamps).

Notes

- The transformation step will raise an error if critical validation issues remain (e.g. duplicate transaction IDs). Do not modify transformation logic unless necessary; it is part of the working pipeline.
