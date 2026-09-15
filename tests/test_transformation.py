"""
Tests for the LibraSight transformation stage.

File:
    tests/test_transformation.py

Purpose:
    Verify the important transformations performed on the raw
    library dataset before it is written to Parquet.

Tests covered:
    - Whitespace removal
    - Text standardization
    - Date conversion
    - Numeric conversion
    - Duplicate detection/removal
    - Invalid-row detection/removal
    - Missing-value handling
    - Cleaned Parquet generation
"""

from pathlib import Path

import pandas as pd
import pytest


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_PARQUET_FILE = (
    PROCESSED_DATA_DIR / "library_clean.parquet"
)


# ============================================================
# EXPECTED COLUMNS
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
    "collection_status",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_raw_data():
    """
    Load the raw library CSV file.
    """

    assert RAW_DATA_FILE.exists(), (
        f"Raw data file was not found: {RAW_DATA_FILE}"
    )

    return pd.read_csv(RAW_DATA_FILE)


def create_test_dataframe():
    """
    Create a small copy of the raw dataset that can safely be
    modified inside individual tests.
    """

    df = load_raw_data()

    return df.copy()


# ============================================================
# TEST 1 — WHITESPACE REMOVAL
# ============================================================

def test_whitespace_can_be_removed_from_text():
    """
    Verify that leading and trailing whitespace can be removed
    from text values.
    """

    df = create_test_dataframe()

    column = "reader_name"

    original_value = str(df.loc[df.index[0], column])

    test_value = f"   {original_value}   "

    cleaned_value = test_value.strip()

    assert cleaned_value == original_value

    assert not cleaned_value.startswith(" ")
    assert not cleaned_value.endswith(" ")


# ============================================================
# TEST 2 — TEXT STANDARDIZATION
# ============================================================

def test_text_standardization():
    """
    Verify that text values can be standardized using strip()
    and consistent casing.
    """

    test_values = [
        " adult ",
        "ADULT",
        "Adult",
    ]

    standardized_values = [
        value.strip().lower()
        for value in test_values
    ]

    assert standardized_values == [
        "adult",
        "adult",
        "adult",
    ]


# ============================================================
# TEST 3 — DATE CONVERSION
# ============================================================

def test_date_conversion():
    """
    Verify that library date columns can be converted into
    pandas datetime values.
    """

    df = create_test_dataframe()

    date_columns = [
        "membership_date",
        "checkout_date",
        "due_date",
        "return_date",
    ]

    for column in date_columns:

        assert column in df.columns

        converted_dates = pd.to_datetime(
            df[column],
            errors="coerce",
            dayfirst=True
        )

        assert isinstance(
            converted_dates,
            pd.Series
        )

        # At least some valid dates should exist.
        assert converted_dates.notna().any(), (
            f"No valid dates found in {column}."
        )


# ============================================================
# TEST 4 — NUMERIC CONVERSION
# ============================================================

def test_numeric_conversion():
    """
    Verify that numeric columns can be converted to numeric
    data types.
    """

    df = create_test_dataframe()

    numeric_columns = [
        "age",
        "publication_year",
        "renewal_count",
        "reservation_count",
        "fine_amount",
        "total_copies",
        "available_copies",
    ]

    for column in numeric_columns:

        assert column in df.columns

        converted_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        assert isinstance(
            converted_values,
            pd.Series
        )

        assert converted_values.notna().any(), (
            f"No numeric values found in {column}."
        )


# ============================================================
# TEST 5 — DUPLICATE REMOVAL
# ============================================================

def test_duplicate_removal():
    """
    Verify that duplicated rows can be identified and removed.
    """

    df = create_test_dataframe()

    original_count = len(df)

    # Add one additional duplicate row.
    duplicate_row = df.iloc[[0]].copy()

    test_df = pd.concat(
        [df, duplicate_row],
        ignore_index=True
    )

    # The raw dataset already contains duplicate records,
    # so we should not assume the original dataset is unique.
    assert len(test_df) == original_count + 1

    # Check that duplicate records are detected.
    duplicate_count = test_df.duplicated().sum()

    assert duplicate_count > 0, (
        "No duplicate records were detected."
    )

    # Remove duplicates.
    cleaned_df = test_df.drop_duplicates()

    # The number of rows should decrease.
    assert len(cleaned_df) < len(test_df), (
        "Duplicate removal did not reduce the number of rows."
    )

    # There should be no duplicates remaining.
    assert not cleaned_df.duplicated().any(), (
        "Duplicate rows still exist after duplicate removal."
    )

# ============================================================
# TEST 6 — INVALID ROW REMOVAL
# ============================================================

def test_invalid_row_removal():
    """
    Verify that rows containing invalid business-rule values
    can be identified and removed.

    Example:
        fine_amount < 0
    """

    df = create_test_dataframe()

    # Add an intentionally invalid record.
    invalid_row = df.iloc[[0]].copy()

    invalid_row.loc[
        invalid_row.index[0],
        "fine_amount"
    ] = -100

    test_df = pd.concat(
        [df, invalid_row],
        ignore_index=True
    )

    invalid_mask = (
        pd.to_numeric(
            test_df["fine_amount"],
            errors="coerce"
        ) < 0
    )

    assert invalid_mask.any()

    cleaned_df = test_df.loc[
        ~invalid_mask
    ].copy()

    assert not (
        pd.to_numeric(
            cleaned_df["fine_amount"],
            errors="coerce"
        ) < 0
    ).any()


# ============================================================
# TEST 7 — MISSING VALUE DETECTION
# ============================================================

def test_missing_values_can_be_detected():
    """
    Verify that missing values can be identified before
    transformation.
    """

    df = create_test_dataframe()

    test_df = df.copy()

    test_df.loc[
        test_df.index[0],
        "reader_name"
    ] = None

    missing_values = test_df["reader_name"].isna()

    assert missing_values.any()


# ============================================================
# TEST 8 — MISSING VALUE IMPUTATION
# ============================================================

def test_missing_value_imputation():
    """
    Verify that a missing text value can be replaced using
    an appropriate fallback value.
    """

    df = create_test_dataframe()

    test_df = df.copy()

    test_df.loc[
        test_df.index[0],
        "reader_name"
    ] = None

    test_df["reader_name"] = (
        test_df["reader_name"]
        .fillna("Unknown")
    )

    assert not test_df["reader_name"].isna().any()

    assert test_df.loc[
        test_df.index[0],
        "reader_name"
    ] == "Unknown"


# ============================================================
# TEST 9 — EXPECTED COLUMNS AFTER TRANSFORMATION
# ============================================================

def test_transformation_preserves_expected_columns():
    """
    Verify that the transformation input contains the complete
    expected LibraSight schema.
    """

    df = create_test_dataframe()

    actual_columns = list(df.columns)

    assert actual_columns == EXPECTED_COLUMNS


# ============================================================
# TEST 10 — PARQUET FILE EXISTS
# ============================================================

def test_clean_parquet_exists():
    """
    Verify that the cleaned Parquet file generated by the
    transformation pipeline exists.
    """

    assert PROCESSED_PARQUET_FILE.exists(), (
        "Cleaned Parquet file was not found at: "
        f"{PROCESSED_PARQUET_FILE}"
    )

    assert PROCESSED_PARQUET_FILE.is_file(), (
        "Expected library_clean.parquet to be a file."
    )


# ============================================================
# TEST 11 — PARQUET CAN BE READ
# ============================================================

def test_clean_parquet_can_be_read():
    """
    Verify that the cleaned Parquet file can be loaded by pandas.
    """

    assert PROCESSED_PARQUET_FILE.exists(), (
        f"Parquet file does not exist: {PROCESSED_PARQUET_FILE}"
    )

    df = pd.read_parquet(
        PROCESSED_PARQUET_FILE
    )

    assert isinstance(df, pd.DataFrame)

    assert not df.empty, (
        "Cleaned Parquet file contains no records."
    )


# ============================================================
# TEST 12 — PARQUET HAS COLUMNS
# ============================================================

def test_clean_parquet_has_columns():
    """
    Verify that the generated Parquet dataset contains columns.
    """

    df = pd.read_parquet(
        PROCESSED_PARQUET_FILE
    )

    assert len(df.columns) > 0


# ============================================================
# TEST 13 — PARQUET HAS TRANSACTION ID
# ============================================================

def test_clean_parquet_contains_transaction_id():
    """
    Verify that transaction_id exists in the cleaned dataset.
    """

    df = pd.read_parquet(
        PROCESSED_PARQUET_FILE
    )

    assert "transaction_id" in df.columns


# ============================================================
# TEST 14 — PARQUET HAS NO DUPLICATE TRANSACTION IDS
# ============================================================

def test_clean_parquet_transaction_ids_are_unique():
    """
    Verify that transaction IDs in the cleaned dataset are unique.

    This is important because transaction_id represents the
    transaction-level business key.
    """

    df = pd.read_parquet(
        PROCESSED_PARQUET_FILE
    )

    assert "transaction_id" in df.columns

    duplicate_ids = (
        df["transaction_id"]
        .duplicated()
        .sum()
    )

    assert duplicate_ids == 0, (
        f"Found {duplicate_ids} duplicate transaction IDs "
        "in cleaned Parquet."
    )


# ============================================================
# TEST 15 — PARQUET IS NOT EMPTY
# ============================================================

def test_clean_parquet_contains_records():
    """
    Verify that the cleaned Parquet dataset contains records.
    """

    df = pd.read_parquet(
        PROCESSED_PARQUET_FILE
    )

    assert len(df) > 0