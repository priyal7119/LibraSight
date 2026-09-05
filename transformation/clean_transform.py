from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "library_clean.parquet"


def clean_data():

    print("=" * 60)
    print("LIBRASIGHT - CLEANING AND TRANSFORMATION")
    print("=" * 60)

    # Create output directory
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # Load raw data
    # --------------------------------------------------

    df = pd.read_csv(RAW_FILE)

    print(f"\nOriginal records: {len(df)}")

    # --------------------------------------------------
    # 1. Remove whitespace from column names
    # --------------------------------------------------

    df.columns = df.columns.str.strip()

    # --------------------------------------------------
    # 2. Remove leading/trailing whitespace
    # --------------------------------------------------

    text_columns = df.select_dtypes(
        include="object"
    ).columns

    for column in text_columns:
        df[column] = df[column].apply(
            lambda value:
            value.strip()
            if isinstance(value, str)
            else value
        )

    # --------------------------------------------------
    # 3. Standardize categorical values
    # --------------------------------------------------

    categorical_columns = [
        "gender",
        "reader_type",
        "genre",
        "language",
        "format",
        "library_type",
        "transaction_status",
        "reservation_flag",
        "checkout_method",
        "collection_status"
    ]

    for column in categorical_columns:
        if column in df.columns:
            df[column] = df[column].apply(
                lambda value:
                value.title()
                if isinstance(value, str)
                else value
            )

    # --------------------------------------------------
    # 4. Standardize dates
    # --------------------------------------------------

    date_columns = [
        "membership_date",
        "checkout_date",
        "due_date",
        "return_date"
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 5. Convert numeric columns
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 6. Remove exact duplicate rows
    # --------------------------------------------------

    before_duplicates = len(df)

    df = df.drop_duplicates()

    duplicates_removed = (
        before_duplicates - len(df)
    )

    print(
        f"Duplicate records removed: "
        f"{duplicates_removed}"
    )

    # --------------------------------------------------
    # 7. Remove invalid range values
    # --------------------------------------------------

    invalid_age = (
        df["age"].notna() &
        (
            (df["age"] < 0) |
            (df["age"] > 120)
        )
    )

    invalid_publication_year = (
        df["publication_year"].notna() &
        (
            (df["publication_year"] < 1000) |
            (df["publication_year"] > 2025)
        )
    )

    invalid_fine = (
        df["fine_amount"].notna() &
        (df["fine_amount"] < 0)
    )

    invalid_total_copies = (
        df["total_copies"].notna() &
        (df["total_copies"] < 0)
    )

    invalid_available_copies = (
        df["available_copies"].notna() &
        (df["available_copies"] < 0)
    )

    # --------------------------------------------------
    # 8. Remove invalid logical records
    # --------------------------------------------------

    invalid_due_date = (
        df["checkout_date"].notna() &
        df["due_date"].notna() &
        (df["due_date"] < df["checkout_date"])
    )

    invalid_return_date = (
        df["checkout_date"].notna() &
        df["return_date"].notna() &
        (df["return_date"] < df["checkout_date"])
    )

    invalid_copy_relationship = (
        df["total_copies"].notna() &
        df["available_copies"].notna() &
        (
            df["available_copies"] >
            df["total_copies"]
        )
    )

    invalid_records = (
        invalid_age |
        invalid_publication_year |
        invalid_fine |
        invalid_total_copies |
        invalid_available_copies |
        invalid_due_date |
        invalid_return_date |
        invalid_copy_relationship
    )

    invalid_count = invalid_records.sum()

    df = df[~invalid_records].copy()

    print(
        f"Invalid records removed: "
        f"{invalid_count}"
    )

    # --------------------------------------------------
    # 9. Handle missing values
    # --------------------------------------------------

    # Text fields:
    # keep unknown values explicit instead of
    # leaving them as NaN.

    text_fill_columns = [
        "reader_name",
        "gender",
        "language",
        "publisher",
        "area"
    ]

    for column in text_fill_columns:
        if column in df.columns:
            df[column] = df[column].fillna(
                "Unknown"
            )

    # Numeric age:
    # retain missingness rather than inventing
    # an age value.

    # Return date:
    # missing return dates are allowed because
    # active/overdue transactions may not yet
    # have been returned.

    # --------------------------------------------------
    # 10. Standardize missing categorical values
    # --------------------------------------------------

    categorical_fill_columns = [
        "reader_type",
        "genre",
        "format",
        "transaction_status",
        "reservation_flag",
        "checkout_method",
        "collection_status"
    ]

    for column in categorical_fill_columns:
        if column in df.columns:
            df[column] = df[column].fillna(
                "Unknown"
            )

    # --------------------------------------------------
    # 11. Save cleaned DataFrame as Parquet
    # --------------------------------------------------

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    print(
        f"\nCleaned records: {len(df)}"
    )

    print(
        f"\nClean Parquet file saved to:\n"
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 60)
    print("CLEANING AND TRANSFORMATION COMPLETED")
    print("=" * 60)

    return df


if __name__ == "__main__":
    clean_data()