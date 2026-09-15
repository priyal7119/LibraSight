# PostgreSQL Loading

PostgreSQL loading is implemented in `database/load_data.py`. This script reads `data/processed/library_clean.parquet` and populates the star-schema tables in the following dependency order:

1. `dim_date`
2. `dim_reader`
3. `dim_book`
4. `dim_branch`
5. `fact_library_transaction`

Loader behavior

- Each dimension load truncates the target table (`TRUNCATE TABLE <dim> CASCADE;`) and inserts distinct records derived from the cleaned Parquet.
- The loader builds lookup dictionaries from the newly loaded dimension tables to map natural keys (e.g. `reader_id`, `book_id`, `branch_id`, `full_date`) to surrogate keys used in the fact table.
- The fact loader converts checkout timestamps into `date_key` and validates that every natural key maps to an existing surrogate key; if a mapping is missing the loader raises an error.
- After loading, `verify_warehouse()` prints counts per table and verifies that `transaction_id` values are unique in the fact table.

Expected row counts (previously verified; confirm with your database before relying on them):

- `dim_date`                    404
- `dim_reader`                  159
- `dim_book`                     94
- `dim_branch`                   10
- `fact_library_transaction`    480

Unique transactions = 480

Notes

- Do not modify the loader unless absolutely necessary. The loader intentionally enforces strict referential integrity and uniqueness checks to preserve analytical correctness.
