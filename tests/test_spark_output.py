"""
Tests for PySpark analytical output.

Verifies that all expected Spark-generated Parquet
outputs exist, are readable, and contain records.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SPARK_OUTPUT_DIR = (
    PROJECT_ROOT
    / "spark"
    / "output"
)


# ---------------------------------------------------------
# EXPECTED SPARK OUTPUTS
# ---------------------------------------------------------

EXPECTED_OUTPUTS = [
    "book_analytics",
    "genre_analytics",
    "reader_analytics",
    "branch_analytics",
    "collection_analytics",
    "yearly_trends",
    "monthly_trends",
    "status_analytics",
]


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def get_output_path(output_name):
    """
    Return the path of a Spark analytical output directory.
    """

    return SPARK_OUTPUT_DIR / output_name


# ---------------------------------------------------------
# TEST 1 — SPARK OUTPUT DIRECTORY
# ---------------------------------------------------------

def test_spark_output_directory_exists():
    """
    Verify that the main Spark output directory exists.
    """

    assert SPARK_OUTPUT_DIR.exists(), (
        f"Spark output directory was not found at:\n"
        f"{SPARK_OUTPUT_DIR}"
    )

    assert SPARK_OUTPUT_DIR.is_dir(), (
        f"Spark output path is not a directory:\n"
        f"{SPARK_OUTPUT_DIR}"
    )


# ---------------------------------------------------------
# TEST 2 — ALL EXPECTED OUTPUT DIRECTORIES
# ---------------------------------------------------------

def test_all_expected_spark_outputs_exist():
    """
    Verify that all eight expected Spark analytical
    output directories exist.
    """

    missing_outputs = []

    for output_name in EXPECTED_OUTPUTS:

        output_path = get_output_path(output_name)

        if not output_path.exists():
            missing_outputs.append(
                f"{output_name}: {output_path}"
            )

        elif not output_path.is_dir():
            missing_outputs.append(
                f"{output_name}: path is not a directory"
            )

    assert not missing_outputs, (
        "The following Spark outputs are missing:\n"
        + "\n".join(missing_outputs)
    )


# ---------------------------------------------------------
# TEST 3 — PARQUET FILE EXISTS
# ---------------------------------------------------------

def test_each_spark_output_contains_parquet_file():
    """
    Verify that every Spark output directory contains
    at least one Parquet file.
    """

    missing_parquet = []

    for output_name in EXPECTED_OUTPUTS:

        output_path = get_output_path(output_name)

        if not output_path.exists():
            missing_parquet.append(
                f"{output_name}: output directory missing"
            )
            continue

        parquet_files = list(
            output_path.glob("*.parquet")
        )

        if not parquet_files:
            missing_parquet.append(
                f"{output_name}: no .parquet file found"
            )

    assert not missing_parquet, (
        "The following Spark outputs do not contain "
        "Parquet files:\n"
        + "\n".join(missing_parquet)
    )


# ---------------------------------------------------------
# TEST 4 — PARQUET FILES ARE READABLE
# ---------------------------------------------------------

def test_spark_outputs_are_readable():
    """
    Verify that each Spark-generated Parquet output
    can be read successfully using pandas.
    """

    unreadable_outputs = []

    for output_name in EXPECTED_OUTPUTS:

        output_path = get_output_path(output_name)

        if not output_path.exists():
            unreadable_outputs.append(
                f"{output_name}: output directory missing"
            )
            continue

        parquet_files = list(
            output_path.glob("*.parquet")
        )

        if not parquet_files:
            unreadable_outputs.append(
                f"{output_name}: no Parquet file found"
            )
            continue

        parquet_file = parquet_files[0]

        try:
            df = pd.read_parquet(parquet_file)

            # Verify that the result is actually a DataFrame.
            assert isinstance(df, pd.DataFrame)

        except Exception as exc:
            unreadable_outputs.append(
                f"{output_name}: {exc}"
            )

    assert not unreadable_outputs, (
        "The following Spark outputs could not be read:\n"
        + "\n".join(unreadable_outputs)
    )


# ---------------------------------------------------------
# TEST 5 — SPARK OUTPUTS ARE NOT EMPTY
# ---------------------------------------------------------

def test_spark_outputs_are_not_empty():
    """
    Verify that every Spark analytical output contains
    at least one record.
    """

    empty_outputs = []

    for output_name in EXPECTED_OUTPUTS:

        output_path = get_output_path(output_name)

        if not output_path.exists():
            empty_outputs.append(
                f"{output_name}: output directory missing"
            )
            continue

        parquet_files = list(
            output_path.glob("*.parquet")
        )

        if not parquet_files:
            empty_outputs.append(
                f"{output_name}: no Parquet file found"
            )
            continue

        try:
            df = pd.read_parquet(parquet_files[0])

            if df.empty:
                empty_outputs.append(
                    f"{output_name}: Parquet file is empty"
                )

        except Exception as exc:
            empty_outputs.append(
                f"{output_name}: {exc}"
            )

    assert not empty_outputs, (
        "The following Spark outputs are empty:\n"
        + "\n".join(empty_outputs)
    )


# ---------------------------------------------------------
# TEST 6 — EXPECTED OUTPUT COUNT
# ---------------------------------------------------------

def test_expected_spark_output_count():
    """
    Verify that all eight analytical output directories
    are present.
    """

    existing_outputs = []

    for output_name in EXPECTED_OUTPUTS:

        output_path = get_output_path(output_name)

        if output_path.exists() and output_path.is_dir():
            existing_outputs.append(output_name)

    assert len(existing_outputs) == 8, (
        f"Expected 8 Spark outputs, "
        f"but found {len(existing_outputs)}."
    )