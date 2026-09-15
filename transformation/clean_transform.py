import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.readers import get_raw_file, read_input_file

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_FILE = get_raw_file()

REJECTED_FILE = os.path.join(
    BASE_DIR,
    "data",
    "quality",
    "rejected_records.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "library_clean.parquet"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

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


# ============================================================
# HELPER FUNCTION
# ============================================================

def parse_dates(series):
    """
    Convert dates into pandas datetime format.

    Supports:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD-MM-YYYY
    - DD-Mon-YYYY
    """

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y"
    ]

    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    for fmt in formats:
        mask = result.isna() & series.notna()

        if mask.any():
            parsed = pd.to_datetime(
                series[mask],
                format=fmt,
                errors="coerce"
            )

            result.loc[mask] = parsed

    return result


# ============================================================
# MAIN TRANSFORMATION
# ============================================================

def main():

    print("=" * 70)
    print("LIBRASIGHT - DATA CLEANING & TRANSFORMATION")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. CHECK INPUT FILE
    # --------------------------------------------------------

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(
            f"Raw data file not found:\n{RAW_FILE}"
        )

    if not os.path.exists(REJECTED_FILE):
        raise FileNotFoundError(
            f"Rejected records file not found:\n{REJECTED_FILE}"
        )

    # --------------------------------------------------------
    # 2. LOAD RAW DATA
    # --------------------------------------------------------

    print("\n[1] Loading raw data...")

    df = read_input_file(RAW_FILE)

    original_count = len(df)

    print(f"Original records: {original_count}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------------
    # 3. CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    print("\n[2] Checking required columns...")

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("All required columns are present.")

    # --------------------------------------------------------
    # 4. LOAD REJECTED RECORDS
    # --------------------------------------------------------

    print("\n[3] Loading rejected records...")

    rejected_df = pd.read_csv(REJECTED_FILE)

    if "transaction_id" not in rejected_df.columns:
        raise ValueError(
            "rejected_records.csv does not contain transaction_id."
        )

    rejected_ids = set(
        rejected_df["transaction_id"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    print(f"Rejected transaction IDs: {len(rejected_ids)}")

    # --------------------------------------------------------
    # 5. REMOVE INVALID RECORDS
    # --------------------------------------------------------

    print("\n[4] Removing invalid records...")

    before_invalid_removal = len(df)

    df["transaction_id"] = (
        df["transaction_id"]
        .astype("string")
        .str.strip()
    )

    df = df[
        ~df["transaction_id"].isin(rejected_ids)
    ].copy()

    invalid_records_removed = (
        before_invalid_removal - len(df)
    )

    print(
        f"Invalid records removed: "
        f"{invalid_records_removed}"
    )

    # --------------------------------------------------------
    # 6. REMOVE COMPLETELY DUPLICATE ROWS
    # --------------------------------------------------------

    print("\n[5] Removing exact duplicate rows...")

    before_exact_duplicates = len(df)

    df = df.drop_duplicates(
        keep="first"
    ).copy()

    exact_duplicates_removed = (
        before_exact_duplicates - len(df)
    )

    print(
        f"Exact duplicate records removed: "
        f"{exact_duplicates_removed}"
    )

    # --------------------------------------------------------
    # 7. REMOVE DUPLICATE TRANSACTION IDs
    # --------------------------------------------------------
    #
    # transaction_id is the business identifier of a library
    # transaction.
    #
    # Therefore, one transaction_id should correspond to only
    # one fact record.
    #
    # The current dataset contains these duplicate IDs:
    #
    # TXN0122
    # TXN0263
    # TXN0311
    # TXN0363
    # TXN0382
    #
    # They differ only in checkout_method.
    #
    # We keep the FIRST occurrence so that the cleaning process
    # is deterministic and does not randomly choose records.
    # --------------------------------------------------------

    print("\n[6] Checking duplicate transaction IDs...")

    before_transaction_duplicates = len(df)

    duplicate_transaction_ids = (
        df.loc[
            df["transaction_id"].duplicated(keep=False),
            "transaction_id"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        f"Duplicate transaction IDs found: "
        f"{len(duplicate_transaction_ids)}"
    )

    if duplicate_transaction_ids:

        print("\nDuplicate transaction IDs:")

        for transaction_id in duplicate_transaction_ids:
            print(f"  - {transaction_id}")

    df = df.drop_duplicates(
        subset=["transaction_id"],
        keep="first"
    ).copy()

    transaction_duplicates_removed = (
        before_transaction_duplicates - len(df)
    )

    print(
        f"\nDuplicate transaction records removed: "
        f"{transaction_duplicates_removed}"
    )

    # --------------------------------------------------------
    # 8. CONVERT NUMERIC COLUMNS
    # --------------------------------------------------------

    print("\n[7] Converting numeric columns...")

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

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # 9. CONVERT DATE COLUMNS
    # --------------------------------------------------------

    print("\n[8] Converting date columns...")

    date_columns = [
        "membership_date",
        "checkout_date",
        "due_date",
        "return_date"
    ]

    for column in date_columns:

        df[column] = parse_dates(
            df[column]
        )

    # --------------------------------------------------------
    # 10. CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    print("\n[9] Cleaning text columns...")

    text_columns = [
        "transaction_id",
        "reader_id",
        "reader_name",
        "gender",
        "reader_type",
        "home_branch_id",
        "book_id",
        "isbn",
        "book_title",
        "author",
        "genre",
        "language",
        "format",
        "publisher",
        "branch_id",
        "branch_name",
        "city",
        "area",
        "library_type",
        "transaction_status",
        "reservation_flag",
        "checkout_method",
        "collection_status"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------------
    # 11. STANDARDIZE GENDER VALUES
    # --------------------------------------------------------

    print("\n[10] Standardizing gender values...")

    if "gender" in df.columns:

        gender_mapping = {
            "M": "Male",
            "F": "Female",
            "male": "Male",
            "female": "Female"
        }

        df["gender"] = (
            df["gender"]
            .replace(gender_mapping)
        )

    # --------------------------------------------------------
    # 12. STANDARDIZE RESERVATION FLAG
    # --------------------------------------------------------

    print("\n[11] Standardizing reservation flag...")

    if "reservation_flag" in df.columns:

        df["reservation_flag"] = (
            df["reservation_flag"]
            .str.title()
        )

    # --------------------------------------------------------
    # 13. SORT DATA
    # --------------------------------------------------------

    print("\n[12] Sorting data...")

    df = df.sort_values(
        by=["transaction_id"]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # 14. FINAL DATA QUALITY CHECK
    # --------------------------------------------------------

    print("\n[13] Performing final quality checks...")

    # Duplicate transaction IDs
    duplicate_transaction_count = (
        df["transaction_id"]
        .duplicated()
        .sum()
    )

    # Invalid age
    invalid_age_count = (
        (
            (df["age"] < 0)
            | (df["age"] > 120)
        )
        & df["age"].notna()
    ).sum()

    # Invalid publication year
    invalid_publication_year_count = (
        (
            (df["publication_year"] < 1000)
            | (df["publication_year"] > 2025)
        )
        & df["publication_year"].notna()
    ).sum()

    # Negative fine
    negative_fine_count = (
        (
            df["fine_amount"] < 0
        )
        & df["fine_amount"].notna()
    ).sum()

    # Negative total copies
    negative_total_copies_count = (
        (
            df["total_copies"] < 0
        )
        & df["total_copies"].notna()
    ).sum()

    # Negative available copies
    negative_available_copies_count = (
        (
            df["available_copies"] < 0
        )
        & df["available_copies"].notna()
    ).sum()

    # Available copies greater than total copies
    available_greater_than_total_count = (
        (
            df["available_copies"]
            > df["total_copies"]
        )
        & df["available_copies"].notna()
        & df["total_copies"].notna()
    ).sum()

    # Due date before checkout date
    invalid_due_date_count = (
        (
            df["due_date"]
            < df["checkout_date"]
        )
        & df["due_date"].notna()
        & df["checkout_date"].notna()
    ).sum()

    # Return date before checkout date
    invalid_return_date_count = (
        (
            df["return_date"]
            < df["checkout_date"]
        )
        & df["return_date"].notna()
        & df["checkout_date"].notna()
    ).sum()

    print(
        f"Duplicate transaction IDs: "
        f"{duplicate_transaction_count}"
    )

    print(
        f"Invalid age values: "
        f"{invalid_age_count}"
    )

    print(
        f"Invalid publication years: "
        f"{invalid_publication_year_count}"
    )

    print(
        f"Negative fines: "
        f"{negative_fine_count}"
    )

    print(
        f"Negative total copies: "
        f"{negative_total_copies_count}"
    )

    print(
        f"Negative available copies: "
        f"{negative_available_copies_count}"
    )

    print(
        f"Available copies > total copies: "
        f"{available_greater_than_total_count}"
    )

    print(
        f"Invalid due dates: "
        f"{invalid_due_date_count}"
    )

    print(
        f"Invalid return dates: "
        f"{invalid_return_date_count}"
    )

    # --------------------------------------------------------
    # 15. STOP IF FINAL DATA IS STILL INVALID
    # --------------------------------------------------------

    if duplicate_transaction_count > 0:
        raise ValueError(
            "Duplicate transaction IDs still exist."
        )

    if invalid_age_count > 0:
        raise ValueError(
            "Invalid age values still exist."
        )

    if invalid_publication_year_count > 0:
        raise ValueError(
            "Invalid publication year values still exist."
        )

    if negative_fine_count > 0:
        raise ValueError(
            "Negative fine values still exist."
        )

    if negative_total_copies_count > 0:
        raise ValueError(
            "Negative total copies still exist."
        )

    if negative_available_copies_count > 0:
        raise ValueError(
            "Negative available copies still exist."
        )

    if available_greater_than_total_count > 0:
        raise ValueError(
            "Available copies cannot be greater than total copies."
        )

    if invalid_due_date_count > 0:
        raise ValueError(
            "Invalid due dates still exist."
        )

    if invalid_return_date_count > 0:
        raise ValueError(
            "Invalid return dates still exist."
        )

    # --------------------------------------------------------
    # 16. CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    print("\n[14] Creating output directory...")

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 17. PREPARE DATE COLUMNS FOR SPARK-COMPATIBLE PARQUET
    # --------------------------------------------------------

    print("\n[15] Preparing date columns for Spark-compatible Parquet...")

    date_columns = [
        "membership_date",
        "checkout_date",
        "due_date",
        "return_date"
    ]

    for column in date_columns:

        if column in df.columns:

            # Ensure the column is datetime64[us] to avoid Spark
            # rejecting Parquet TIMESTAMP(NANOS,false) values.
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            ).dt.as_unit("us")

    # --------------------------------------------------------
    # 18. SAVE CLEAN PARQUET
    # --------------------------------------------------------

    print("\n[16] Saving clean Parquet...")
    print("\nFinal schema before Parquet export:")

    print(df.dtypes)

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
        coerce_timestamps="us"
    )

    print(
        f"Clean Parquet saved successfully:\n"
        f"{OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # 19. FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TRANSFORMATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        f"Original records: "
        f"{original_count}"
    )

    print(
        f"Invalid records removed: "
        f"{invalid_records_removed}"
    )

    print(
        f"Exact duplicate records removed: "
        f"{exact_duplicates_removed}"
    )

    print(
        f"Duplicate transaction records removed: "
        f"{transaction_duplicates_removed}"
    )

    print(
        f"Final cleaned records: "
        f"{len(df)}"
    )

    print(
        f"Unique transaction IDs: "
        f"{df['transaction_id'].nunique()}"
    )

    print(
        f"Duplicate transaction IDs remaining: "
        f"{df['transaction_id'].duplicated().sum()}"
    )

    print(
        f"\nOutput file:\n{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()