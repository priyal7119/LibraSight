from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

def get_raw_file():
    """
    Return the active LibraSight input file.

    If RAW_DATA_FILE is not configured,
    the existing CSV file is used by default.
    """

    default_file = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "library_raw_data.csv"
    )

    configured_file = os.getenv("RAW_DATA_FILE")

    if not configured_file:
        return default_file

    file_path = Path(configured_file)

    if not file_path.is_absolute():
        file_path = PROJECT_ROOT / file_path

    return file_path

def read_input_file(file_path):
    """
    Read a supported LibraSight input file.

    Supported formats:
        CSV
        JSON
        XLSX

    Returns:
        pandas.DataFrame
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Input path is not a file: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension == ".json":
        df = pd.read_json(file_path)

    elif extension == ".xlsx":
        df = pd.read_excel(
            file_path,
            engine="openpyxl"
        )

    else:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            "Supported formats are: .csv, .json, .xlsx"
        )

    if df.empty:
        raise ValueError(
            f"Input file contains no records: {file_path}"
        )

    return df