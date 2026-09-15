from pathlib import Path

import pandas as pd
import pytest

from ingestion.readers import read_input_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEST_INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "test_inputs"
)

CSV_FILE = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"

JSON_FILE = TEST_INPUT_DIR / "library_raw_data.json"

XLSX_FILE = TEST_INPUT_DIR / "library_raw_data.xlsx"


EXPECTED_COLUMN_COUNT = 35


def test_csv_reader():
    df = read_input_file(CSV_FILE)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df.columns) == EXPECTED_COLUMN_COUNT


def test_json_reader():
    df = read_input_file(JSON_FILE)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df.columns) == EXPECTED_COLUMN_COUNT


def test_xlsx_reader():
    df = read_input_file(XLSX_FILE)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df.columns) == EXPECTED_COLUMN_COUNT


def test_unsupported_format():
    test_file = TEST_INPUT_DIR / "test.txt"

    test_file.write_text(
        "This is an unsupported file.",
        encoding="utf-8"
    )

    try:
        with pytest.raises(ValueError, match="Unsupported file format"):
            read_input_file(test_file)
    finally:
        test_file.unlink(missing_ok=True)