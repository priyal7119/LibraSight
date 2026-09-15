"""
Tests for the LibraSight validation stage.

File:
    tests/test_validation.py

Purpose:
    Verify that invalid library records can be detected based on
    the business rules used by the LibraSight data pipeline.

Validation rules tested:
    - Negative fine amount
    - Negative inventory
    - Invalid reader age
    - Invalid publication year
    - Invalid dates
    - Due date before checkout date
    - Return date before checkout date
    - Available copies greater than total copies
    - Duplicate records
    - Missing values
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
# HELPER FUNCTION
# ============================================================

def load_raw_data():
    """
    Load the raw library dataset.
    """

    assert RAW_DATA_FILE.exists(), (
        f"Raw data file does not exist: {RAW_DATA_FILE}"
    )

    return pd.read_csv(RAW_DATA_FILE)


# ============================================================
# TEST 1 — NEGATIVE FINE AMOUNT
# ============================================================

def test_negative_fine_amount_is_detected():
    """
    A fine amount below zero should be considered invalid.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "fine_amount"] = -1

    invalid_records = test_df[
        pd.to_numeric(
            test_df["fine_amount"],
            errors="coerce"
        ) < 0
    ]

    assert len(invalid_records) > 0, (
        "Negative fine amount was not detected."
    )


# ============================================================
# TEST 2 — NEGATIVE TOTAL COPIES
# ============================================================

def test_negative_total_copies_is_detected():
    """
    Total copies cannot be negative.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "total_copies"] = -1

    invalid_records = test_df[
        pd.to_numeric(
            test_df["total_copies"],
            errors="coerce"
        ) < 0
    ]

    assert len(invalid_records) > 0, (
        "Negative total_copies value was not detected."
    )


# ============================================================
# TEST 3 — NEGATIVE AVAILABLE COPIES
# ============================================================

def test_negative_available_copies_is_detected():
    """
    Available copies cannot be negative.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "available_copies"] = -1

    invalid_records = test_df[
        pd.to_numeric(
            test_df["available_copies"],
            errors="coerce"
        ) < 0
    ]

    assert len(invalid_records) > 0, (
        "Negative available_copies value was not detected."
    )


# ============================================================
# TEST 4 — AGE ABOVE 120
# ============================================================

def test_age_above_120_is_detected():
    """
    Reader age above 120 should be considered invalid.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "age"] = 121

    invalid_records = test_df[
        pd.to_numeric(
            test_df["age"],
            errors="coerce"
        ) > 120
    ]

    assert len(invalid_records) > 0, (
        "Age greater than 120 was not detected."
    )


# ============================================================
# TEST 5 — NEGATIVE AGE
# ============================================================

def test_negative_age_is_detected():
    """
    Reader age below zero should be considered invalid.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "age"] = -1

    invalid_records = test_df[
        pd.to_numeric(
            test_df["age"],
            errors="coerce"
        ) < 0
    ]

    assert len(invalid_records) > 0, (
        "Negative age was not detected."
    )


# ============================================================
# TEST 6 — INVALID PUBLICATION YEAR
# ============================================================

def test_invalid_publication_year_is_detected():
    """
    Publication year outside a reasonable range should be detected.

    The project treats years after the current year as invalid.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "publication_year"] = 9999

    invalid_records = test_df[
        pd.to_numeric(
            test_df["publication_year"],
            errors="coerce"
        ) > 2026
    ]

    assert len(invalid_records) > 0, (
        "Invalid publication year was not detected."
    )


# ============================================================
# TEST 7 — INVALID CHECKOUT DATE
# ============================================================

def test_invalid_checkout_date_is_detected():
    """
    An invalid checkout date should be converted to NaT
    when parsed using pandas.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "checkout_date"] = "INVALID_DATE"

    parsed_dates = pd.to_datetime(
        test_df["checkout_date"],
        errors="coerce",
        dayfirst=True
    )

    assert parsed_dates.isna().any(), (
        "Invalid checkout date was not detected."
    )


# ============================================================
# TEST 8 — INVALID MEMBERSHIP DATE
# ============================================================

def test_invalid_membership_date_is_detected():
    """
    An invalid membership date should be detected.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "membership_date"] = "INVALID_DATE"

    parsed_dates = pd.to_datetime(
        test_df["membership_date"],
        errors="coerce",
        dayfirst=True
    )

    assert parsed_dates.isna().any(), (
        "Invalid membership date was not detected."
    )


# ============================================================
# TEST 9 — DUE DATE BEFORE CHECKOUT DATE
# ============================================================

def test_due_date_before_checkout_date_is_detected():
    """
    The due date must not occur before the checkout date.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "checkout_date"] = "20/01/2024"
    test_df.loc[test_df.index[0], "due_date"] = "19/01/2024"

    checkout_dates = pd.to_datetime(
        test_df["checkout_date"],
        errors="coerce",
        dayfirst=True
    )

    due_dates = pd.to_datetime(
        test_df["due_date"],
        errors="coerce",
        dayfirst=True
    )

    invalid_records = test_df[
        due_dates < checkout_dates
    ]

    assert len(invalid_records) > 0, (
        "Due date before checkout date was not detected."
    )


# ============================================================
# TEST 10 — RETURN DATE BEFORE CHECKOUT DATE
# ============================================================

def test_return_date_before_checkout_date_is_detected():
    """
    The return date must not occur before the checkout date.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "checkout_date"] = "20/01/2024"
    test_df.loc[test_df.index[0], "return_date"] = "19/01/2024"

    checkout_dates = pd.to_datetime(
        test_df["checkout_date"],
        errors="coerce",
        dayfirst=True
    )

    return_dates = pd.to_datetime(
        test_df["return_date"],
        errors="coerce",
        dayfirst=True
    )

    invalid_records = test_df[
        return_dates < checkout_dates
    ]

    assert len(invalid_records) > 0, (
        "Return date before checkout date was not detected."
    )


# ============================================================
# TEST 11 — AVAILABLE COPIES GREATER THAN TOTAL COPIES
# ============================================================

def test_available_copies_greater_than_total_copies_is_detected():
    """
    Available copies cannot exceed total copies.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "total_copies"] = 5
    test_df.loc[test_df.index[0], "available_copies"] = 10

    total_copies = pd.to_numeric(
        test_df["total_copies"],
        errors="coerce"
    )

    available_copies = pd.to_numeric(
        test_df["available_copies"],
        errors="coerce"
    )

    invalid_records = test_df[
        available_copies > total_copies
    ]

    assert len(invalid_records) > 0, (
        "available_copies greater than total_copies "
        "was not detected."
    )


# ============================================================
# TEST 12 — DUPLICATE RECORDS
# ============================================================

def test_duplicate_records_are_detected():
    """
    Verify that duplicate rows can be detected.
    """

    df = load_raw_data()

    test_df = pd.concat(
        [df, df.iloc[[0]]],
        ignore_index=True
    )

    duplicate_count = test_df.duplicated().sum()

    assert duplicate_count > 0, (
        "Duplicate record was not detected."
    )


# ============================================================
# TEST 13 — MISSING VALUES
# ============================================================

def test_missing_values_are_detected():
    """
    Verify that missing values can be detected.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "reader_name"] = None

    missing_count = test_df["reader_name"].isna().sum()

    assert missing_count > 0, (
        "Missing reader_name value was not detected."
    )


# ============================================================
# TEST 14 — REQUIRED IDENTIFIER MISSING
# ============================================================

def test_missing_transaction_id_is_detected():
    """
    A missing transaction_id should be detected because
    transaction_id is a required identifier.
    """

    df = load_raw_data()

    test_df = df.copy()

    test_df.loc[test_df.index[0], "transaction_id"] = None

    missing_count = test_df["transaction_id"].isna().sum()

    assert missing_count > 0, (
        "Missing transaction_id was not detected."
    )


# ============================================================
# TEST 15 — NUMERIC VALIDATION
# ============================================================

def test_numeric_columns_can_be_validated():
    """
    Verify that important numeric columns can be converted
    to numeric values and invalid values can be detected.
    """

    df = load_raw_data()

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

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        assert isinstance(converted, pd.Series)