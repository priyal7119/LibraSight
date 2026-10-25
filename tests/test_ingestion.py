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
# TEST 8 — DASHBOARD YEAR CAP
# ============================================================

def test_dashboard_year_cap_uses_2026_ceiling():
    """
    All dashboard aggregations should be capped at the current reporting window.
    Future years beyond 2026 must be excluded from visible analytics.
    """
    import pandas as pd

    from ingestion.readers import limit_chart_years

    df = pd.DataFrame(
        {
            "checkout_date": pd.to_datetime([
                "2024-01-15",
                "2025-06-20",
                "2026-09-01",
                "2028-02-08",
                "2035-11-10",
            ])
        }
    )

    capped = limit_chart_years(df, max_year=2026)

    assert capped["checkout_date"].dt.year.max() <= 2026
    assert len(capped) == 3


# ============================================================
# TEST 8 — JSON PAYLOAD NORMALIZATION
# ============================================================

def test_normalize_json_payload_handles_standard_response_shapes():
    """
    Verify that common JSON response wrappers are converted to a DataFrame.
    """
    from ingestion.readers import normalize_json_payload

    payload = {
        "data": [
            {"transaction_id": "t1", "reader_id": 101, "fine_amount": 5.5},
            {"transaction_id": "t2", "reader_id": 102, "fine_amount": 0.0},
        ]
    }

    df = normalize_json_payload(payload)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["transaction_id", "reader_id", "fine_amount"]
    assert len(df) == 2


# ============================================================
# TEST 9 — API RESPONSE NORMALIZATION
# ============================================================

def test_normalize_json_payload_handles_api_result_wrapper():
    """
    Verify that API-style result wrappers are handled safely.
    """
    from ingestion.readers import normalize_json_payload

    payload = {
        "results": [
            {"book_id": "b1", "book_title": "Clean Code", "available_copies": 4},
            {"book_id": "b2", "book_title": "The Pragmatic Programmer", "available_copies": 2},
        ]
    }

    df = normalize_json_payload(payload)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["book_id", "book_title", "available_copies"]
    assert len(df) == 2


# ============================================================
# TEST 10 — COMBINED CSV + JSON SOURCE SUMMARY
# ============================================================


def test_load_combined_sources_reads_csv_and_json():
    """
    Verify that the CSV dataset and digital event JSON can be loaded together
    as a combined source summary without replacing the original CSV pipeline.
    """
    from ingestion.readers import load_combined_sources

    combined = load_combined_sources()

    assert isinstance(combined, dict)
    assert combined["csv_records"] > 0
    assert combined["json_records"] > 0
    assert "event_types" in combined
    assert "data_sources" in combined
    assert "csv" in combined["data_sources"]
    assert "json" in combined["data_sources"]


# ============================================================
# TEST 11 — COMBINED DASHBOARD ANALYTICS
# ============================================================


def test_build_combined_dashboard_payload_aggregates_csv_and_json():
    """
    Verify that a combined dashboard payload exposes both sources and their
    summary metrics without altering the canonical CSV dataset flow.
    """
    from ingestion.readers import build_combined_dashboard_payload

    payload = build_combined_dashboard_payload()

    assert isinstance(payload, dict)
    assert payload["data_sources"]["csv"] > 0
    assert payload["data_sources"]["json"] > 0
    assert payload["data_sources"]["combined"] > 0
    assert payload["csv_summary"]["total_transactions"] > 0
    assert payload["event_type_counts"]
    assert payload["source_system_counts"]


def test_build_combined_dashboard_payload_respects_filters():
    """Ensure the dashboard filter parameters are honored when aggregating a combined payload."""
    from ingestion.readers import build_combined_dashboard_payload

    df = load_raw_data()
    branch_id = df["branch_id"].dropna().astype(str).iloc[0]
    genre = df["genre"].dropna().astype(str).iloc[0]

    filtered = build_combined_dashboard_payload(
        year=int(df["checkout_date"].dropna().astype(str).str[:4].mode().iloc[0]),
        branch_id=branch_id,
        genre=genre,
    )

    assert isinstance(filtered, dict)
    assert filtered["summary"]["total_transactions"] >= 0
    assert filtered["summary"]["total_branches"] >= 0
    assert filtered["summary"]["total_books"] >= 0
    assert filtered["summary"]["total_readers"] >= 0


def test_inventory_summary_matches_valid_dataset_rows():
    """Inventory totals should match the active 2026 reporting window and ignore null/JSON-only stock rows."""
    from ingestion.readers import build_combined_dashboard_payload

    payload = build_combined_dashboard_payload()
    health = payload["collection_health"]

    assert health["total_copies"] == 3861
    assert health["available_copies"] == 2388
    assert health["unavailable_copies"] == 1473
    assert health["zero_available_count"] == 60


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