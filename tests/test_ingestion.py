"""
Tests for the LibraSight data ingestion stage.

File:
    tests/test_ingestion.py

Purpose:
    Verify that the raw library CSV file:
    1. Exists
    2. Can be loaded
    3. Contains the expected columns
    4. Does not have missing required columns
    5. Does not contain unexpected columns
"""

from pathlib import Path

import pandas as pd
import pytest


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"


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
# HELPER FUNCTION
# ============================================================

def load_raw_data():
    """
    Load the raw CSV file and return it as a pandas DataFrame.
    """
    return pd.read_csv(RAW_DATA_FILE)


# ============================================================
# TEST 1 — RAW CSV EXISTS
# ============================================================

def test_raw_csv_exists():
    """
    Verify that the raw library CSV file exists.
    """

    assert RAW_DATA_FILE.exists(), (
        f"Raw CSV file was not found at: {RAW_DATA_FILE}"
    )

    assert RAW_DATA_FILE.is_file(), (
        f"Expected a file but found something else: {RAW_DATA_FILE}"
    )


# ============================================================
# TEST 2 — CSV CAN BE LOADED
# ============================================================

def test_raw_csv_can_be_loaded():
    """
    Verify that the CSV can be successfully loaded using pandas.
    """

    df = load_raw_data()

    assert df is not None

    assert isinstance(df, pd.DataFrame)

    assert not df.empty, "Raw CSV loaded successfully but contains no rows."


# ============================================================
# TEST 3 — EXPECTED NUMBER OF COLUMNS
# ============================================================

def test_raw_csv_has_expected_column_count():
    """
    Verify that the raw dataset contains 35 columns.
    """

    df = load_raw_data()

    assert len(df.columns) == 35, (
        f"Expected 35 columns, but found {len(df.columns)} columns."
    )


# ============================================================
# TEST 4 — REQUIRED COLUMNS EXIST
# ============================================================

def test_required_columns_exist():
    """
    Verify that every required column exists in the raw dataset.
    """

    df = load_raw_data()

    actual_columns = set(df.columns)

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    assert not missing_columns, (
        "The following required columns are missing: "
        f"{missing_columns}"
    )


# ============================================================
# TEST 5 — NO UNEXPECTED COLUMNS
# ============================================================

def test_no_unexpected_columns():
    """
    Verify that the raw dataset does not contain columns
    outside the defined LibraSight schema.
    """

    df = load_raw_data()

    expected_columns = set(EXPECTED_COLUMNS)
    actual_columns = set(df.columns)

    unexpected_columns = actual_columns - expected_columns

    assert not unexpected_columns, (
        "Unexpected columns found in raw dataset: "
        f"{sorted(unexpected_columns)}"
    )


# ============================================================
# TEST 6 — COLUMN ORDER
# ============================================================

def test_column_order():
    """
    Verify that the columns appear in the expected order.

    This helps detect accidental changes to the raw schema.
    """

    df = load_raw_data()

    actual_columns = list(df.columns)

    assert actual_columns == EXPECTED_COLUMNS, (
        "Column order does not match the expected raw-data schema.\n"
        f"Expected: {EXPECTED_COLUMNS}\n"
        f"Actual:   {actual_columns}"
    )


# ============================================================
# TEST 7 — DATASET CONTAINS ROWS
# ============================================================

def test_raw_dataset_contains_rows():
    """
    Verify that the raw dataset contains at least one record.
    """

    df = load_raw_data()

    assert len(df) > 0, "Raw dataset contains zero records."


# ============================================================
# TEST 8 — TRANSACTION ID COLUMN EXISTS AND HAS DATA
# ============================================================

def test_transaction_id_has_data():
    """
    Verify that transaction_id exists and contains values.
    """

    df = load_raw_data()

    assert "transaction_id" in df.columns

    assert df["transaction_id"].notna().any(), (
        "transaction_id column does not contain any values."
    )


# ============================================================
# TEST 9 — BOOK ID COLUMN EXISTS AND HAS DATA
# ============================================================

def test_book_id_has_data():
    """
    Verify that book_id exists and contains values.
    """

    df = load_raw_data()

    assert "book_id" in df.columns

    assert df["book_id"].notna().any(), (
        "book_id column does not contain any values."
    )


# ============================================================
# TEST 10 — READER ID COLUMN EXISTS AND HAS DATA
# ============================================================

def test_reader_id_has_data():
    """
    Verify that reader_id exists and contains values.
    """

    df = load_raw_data()

    assert "reader_id" in df.columns

    assert df["reader_id"].notna().any(), (
        "reader_id column does not contain any values."
    )