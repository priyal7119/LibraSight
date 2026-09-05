from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"


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


# --------------------------------------------------
# 3. Ingestion function
# --------------------------------------------------

def load_raw_data():
    print("=" * 60)
    print("LIBRASIGHT - DATA INGESTION")
    print("=" * 60)

    # Check whether the CSV file exists
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw CSV file not found at: {RAW_FILE}"
        )

    print(f"\nRaw file found:")
    print(RAW_FILE)

    # Read CSV using Pandas
    df = pd.read_csv(RAW_FILE)

    print("\nCSV loaded successfully.")

    # --------------------------------------------------
    # Check row and column count
    # --------------------------------------------------

    print(f"\nNumber of rows    : {df.shape[0]}")
    print(f"Number of columns : {df.shape[1]}")

    # --------------------------------------------------
    # Check expected number of columns
    # --------------------------------------------------

    if len(df.columns) != len(EXPECTED_COLUMNS):
        raise ValueError(
            f"Expected {len(EXPECTED_COLUMNS)} columns, "
            f"but found {len(df.columns)} columns."
        )

    print(
        f"\nColumn count check: PASS "
        f"({len(df.columns)} columns found)"
    )

    # --------------------------------------------------
    # Check column names
    # --------------------------------------------------

    actual_columns = list(df.columns)

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        raise ValueError(
            f"Missing expected columns: {missing_columns}"
        )

    if unexpected_columns:
        raise ValueError(
            f"Unexpected columns found: {unexpected_columns}"
        )

    print("Column name check: PASS")

    # --------------------------------------------------
    # Display data types
    # --------------------------------------------------

    print("\nData types:")
    print(df.dtypes)

    # --------------------------------------------------
    # Display first five records
    # --------------------------------------------------

    print("\nFirst five records:")
    print(df.head())

    print("\n" + "=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)

    return df


# --------------------------------------------------
# 4. Run ingestion
# --------------------------------------------------

if __name__ == "__main__":
    df = load_raw_data()
    