from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"

QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

QUALITY_REPORT = QUALITY_DIR / "data_quality_report.csv"

REJECTED_RECORDS = QUALITY_DIR / "rejected_records.csv"


# --------------------------------------------------
# 2. Expected columns
# --------------------------------------------------

EXPECTED_COLUMNS = [
    "transaction_id",
    "reader_id",
    "reader_name",
    "age",
    "gender",
    "reader_type",
    "membership_date",
    "home_branch_id",
    "book_id",
    "isbn",
    "book_title",
    "author",
    "genre",
    "publication_year",
    "language",
    "format",
    "publisher",
    "branch_id",
    "branch_name",
    "city",
    "area",
    "library_type",
    "branch_capacity",
    "checkout_date",
    "due_date",
    "return_date",
    "transaction_status",
    "renewal_count",
    "reservation_flag",
    "reservation_count",
    "checkout_method",
    "fine_amount",
    "total_copies",
    "available_copies",
    "collection_status"
]


def validate_data():

    print("=" * 60)
    print("LIBRASIGHT - DATA VALIDATION")
    print("=" * 60)

    # Create quality directory if it doesn't exist
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Load raw data
    # --------------------------------------------------

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw CSV file not found: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    print(f"\nLoaded {len(df)} records.")

    quality_results = []

    # --------------------------------------------------
    # 1. STRUCTURAL VALIDATION
    # --------------------------------------------------

    print("\n--- Structural Validation ---")

    # Column count
    column_count_pass = len(df.columns) == len(EXPECTED_COLUMNS)

    quality_results.append({
        "category": "Structural",
        "check": "Expected column count",
        "invalid_count": 0 if column_count_pass else 1,
        "status": "PASS" if column_count_pass else "FAIL"
    })

    # Missing columns
    missing_columns = [
        col for col in EXPECTED_COLUMNS
        if col not in df.columns
    ]

    quality_results.append({
        "category": "Structural",
        "check": "Missing expected columns",
        "invalid_count": len(missing_columns),
        "status": "PASS" if len(missing_columns) == 0 else "FAIL"
    })

    # Duplicate records
    duplicate_count = df.duplicated().sum()

    quality_results.append({
        "category": "Structural",
        "check": "Duplicate records",
        "invalid_count": int(duplicate_count),
        "status": "PASS" if duplicate_count == 0 else "CHECK"
    })

    # Completely empty rows
    empty_rows = df.isna().all(axis=1).sum()

    quality_results.append({
        "category": "Structural",
        "check": "Completely empty records",
        "invalid_count": int(empty_rows),
        "status": "PASS" if empty_rows == 0 else "FAIL"
    })

    # --------------------------------------------------
    # 2. DATA TYPE VALIDATION
    # --------------------------------------------------

    print("\n--- Data Type Validation ---")

    numeric_columns = [
        "age",
        "publication_year",
        "branch_capacity",
        "renewal_count",
        "reservation_count",
        "fine_amount",
        "total_copies",
        "available_copies"
    ]

    for column in numeric_columns:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_count = (
            converted.isna() & df[column].notna()
        ).sum()

        quality_results.append({
            "category": "Data Type",
            "check": f"Numeric values in {column}",
            "invalid_count": int(invalid_count),
            "status": "PASS" if invalid_count == 0 else "FAIL"
        })

    # --------------------------------------------------
    # 3. DATE VALIDATION
    # --------------------------------------------------

    date_columns = [
        "membership_date",
        "checkout_date",
        "due_date",
        "return_date"
    ]

    for column in date_columns:

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_count = (
            converted.isna() & df[column].notna()
        ).sum()

        quality_results.append({
            "category": "Data Type",
            "check": f"Date values in {column}",
            "invalid_count": int(invalid_count),
            "status": "PASS" if invalid_count == 0 else "FAIL"
        })

    # --------------------------------------------------
    # 4. MISSING VALUE VALIDATION
    # --------------------------------------------------

    print("\n--- Missing Value Validation ---")

    for column in df.columns:

        missing_count = df[column].isna().sum()

        quality_results.append({
            "category": "Missing Values",
            "check": f"Missing values in {column}",
            "invalid_count": int(missing_count),
            "status": "PASS" if missing_count == 0 else "CHECK"
        })

    # --------------------------------------------------
    # Convert required columns for range checks
    # --------------------------------------------------

    age = pd.to_numeric(df["age"], errors="coerce")
    publication_year = pd.to_numeric(
        df["publication_year"],
        errors="coerce"
    )
    fine_amount = pd.to_numeric(
        df["fine_amount"],
        errors="coerce"
    )
    total_copies = pd.to_numeric(
        df["total_copies"],
        errors="coerce"
    )
    available_copies = pd.to_numeric(
        df["available_copies"],
        errors="coerce"
    )

    # --------------------------------------------------
    # 5. RANGE VALIDATION
    # --------------------------------------------------

    print("\n--- Range Validation ---")

    invalid_age = (
        age.notna() &
        ((age < 0) | (age > 120))
    )

    quality_results.append({
        "category": "Range",
        "check": "Age between 0 and 120",
        "invalid_count": int(invalid_age.sum()),
        "status": "PASS" if invalid_age.sum() == 0 else "FAIL"
    })

    invalid_publication_year = (
        publication_year.notna() &
        (
            (publication_year < 1000) |
            (publication_year > 2025)
        )
    )

    quality_results.append({
        "category": "Range",
        "check": "Valid publication year",
        "invalid_count": int(
            invalid_publication_year.sum()
        ),
        "status": (
            "PASS"
            if invalid_publication_year.sum() == 0
            else "FAIL"
        )
    })

    invalid_fine = (
        fine_amount.notna() &
        (fine_amount < 0)
    )

    quality_results.append({
        "category": "Range",
        "check": "Fine amount is non-negative",
        "invalid_count": int(invalid_fine.sum()),
        "status": "PASS" if invalid_fine.sum() == 0 else "FAIL"
    })

    invalid_total_copies = (
        total_copies.notna() &
        (total_copies < 0)
    )

    quality_results.append({
        "category": "Range",
        "check": "Total copies are non-negative",
        "invalid_count": int(
            invalid_total_copies.sum()
        ),
        "status": (
            "PASS"
            if invalid_total_copies.sum() == 0
            else "FAIL"
        )
    })

    invalid_available_copies = (
        available_copies.notna() &
        (available_copies < 0)
    )

    quality_results.append({
        "category": "Range",
        "check": "Available copies are non-negative",
        "invalid_count": int(
            invalid_available_copies.sum()
        ),
        "status": (
            "PASS"
            if invalid_available_copies.sum() == 0
            else "FAIL"
        )
    })

    # --------------------------------------------------
    # 6. LOGICAL VALIDATION
    # --------------------------------------------------

    print("\n--- Logical Validation ---")

    checkout = pd.to_datetime(
        df["checkout_date"],
        errors="coerce"
    )

    due = pd.to_datetime(
        df["due_date"],
        errors="coerce"
    )

    returned = pd.to_datetime(
        df["return_date"],
        errors="coerce"
    )

    invalid_due_date = (
        checkout.notna() &
        due.notna() &
        (due < checkout)
    )

    quality_results.append({
        "category": "Logical",
        "check": "Due date >= checkout date",
        "invalid_count": int(
            invalid_due_date.sum()
        ),
        "status": (
            "PASS"
            if invalid_due_date.sum() == 0
            else "FAIL"
        )
    })

    invalid_return_date = (
        checkout.notna() &
        returned.notna() &
        (returned < checkout)
    )

    quality_results.append({
        "category": "Logical",
        "check": "Return date >= checkout date",
        "invalid_count": int(
            invalid_return_date.sum()
        ),
        "status": (
            "PASS"
            if invalid_return_date.sum() == 0
            else "FAIL"
        )
    })

    invalid_copy_relationship = (
        total_copies.notna() &
        available_copies.notna() &
        (available_copies > total_copies)
    )

    quality_results.append({
        "category": "Logical",
        "check": "Available copies <= total copies",
        "invalid_count": int(
            invalid_copy_relationship.sum()
        ),
        "status": (
            "PASS"
            if invalid_copy_relationship.sum() == 0
            else "FAIL"
        )
    })

    # --------------------------------------------------
    # Save quality report
    # --------------------------------------------------

    quality_report = pd.DataFrame(quality_results)

    quality_report.to_csv(
        QUALITY_REPORT,
        index=False
    )

    # --------------------------------------------------
    # Collect rejected records
    # --------------------------------------------------

    rejected_mask = (
        invalid_age |
        invalid_publication_year |
        invalid_fine |
        invalid_total_copies |
        invalid_available_copies |
        invalid_due_date |
        invalid_return_date |
        invalid_copy_relationship
    )

    rejected_records = df[rejected_mask].copy()

    rejected_records.to_csv(
        REJECTED_RECORDS,
        index=False
    )

    # --------------------------------------------------
    # Print summary
    # --------------------------------------------------

    print("\nValidation completed.")

    print(
        f"Quality report saved to:\n{QUALITY_REPORT}"
    )

    print(
        f"\nRejected records saved to:\n{REJECTED_RECORDS}"
    )

    print(
        f"\nRejected records: "
        f"{len(rejected_records)}"
    )

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    validate_data()