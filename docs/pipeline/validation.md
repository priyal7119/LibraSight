# Validation

Validation is implemented in `validation/validate.py` and produces a quality report and a rejected-records CSV used by the transformation step.

Checks performed (implemented in code)

- Structural checks
  - Expected column count
  - Missing expected columns
  - Duplicate records
  - Completely empty rows
- Data type checks
  - Numeric columns converted and checked: `age`, `publication_year`, `branch_capacity`, `renewal_count`, `reservation_count`, `fine_amount`, `total_copies`, `available_copies`
- Date parsing and validation
  - `membership_date`, `checkout_date`, `due_date`, `return_date` are parsed using supported formats (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, DD-MMM-YYYY)
  - Invalid date values are reported
- Missing value checks
  - Missing counts are computed for every column and reported
- Range checks
  - `age` must be between 0 and 120
  - `publication_year` must be between 1000 and 2025
  - `fine_amount`, `total_copies`, `available_copies` must be non-negative
- Logical checks
  - `due_date >= checkout_date`
  - `return_date >= checkout_date`
  - `available_copies <= total_copies`

Outputs

- `data/quality/data_quality_report.csv` — structured summary of checks and counts
- `data/quality/rejected_records.csv` — subset of raw rows that failed critical checks (these records are removed during transformation)

Notes

- The validation code determines which records are rejected; the transformation step uses the rejected-records file to remove invalid rows deterministically.
