from pathlib import Path
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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


def get_json_source_file():
    """
    Return the bundled JSON digital-events source file.
    This is additive to the default CSV input and does not replace it.
    """
    return PROJECT_ROOT / "data" / "raw" / "library_digital_events.json"


def limit_chart_years(df, max_year=2026):
    """
    Restrict dashboard-facing time series to the active reporting window.
    This keeps the UI focused on current analytics and prevents future-year
    artifacts like 2028 or 2035 from appearing in charts and KPIs.
    """
    if df is None or df.empty:
        return df

    filtered = df.copy()

    for column in ["year", "checkout_year", "publication_year"]:
        if column in filtered.columns:
            numeric_years = pd.to_numeric(filtered[column], errors="coerce")
            valid_year_mask = numeric_years.isna() | numeric_years.le(max_year)
            filtered = filtered[valid_year_mask]

    if "checkout_date" in filtered.columns:
        date_years = pd.to_datetime(filtered["checkout_date"], errors="coerce", utc=True).dt.year
        valid_date_mask = date_years.isna() | date_years.le(max_year)
        filtered = filtered[valid_date_mask]

    return filtered.reset_index(drop=True)


def normalize_json_payload(payload):
    """
    Normalize a JSON payload into a pandas DataFrame.

    Supports common API response wrappers such as:
        {"data": [...]}
        {"results": [...]}
        {"records": [...]}
        {"items": [...]}
        [...]  # direct list of records
        {...}  # single-record object
    """
    if payload is None:
        raise ValueError("JSON payload is empty or null.")

    if isinstance(payload, pd.DataFrame):
        return payload.copy()

    if isinstance(payload, dict):
        for key in ("data", "results", "records", "items"):
            if key in payload:
                return normalize_json_payload(payload[key])

        if payload:
            return pd.json_normalize([payload])

        return pd.DataFrame()

    if isinstance(payload, list):
        if not payload:
            return pd.DataFrame()

        if isinstance(payload[0], dict):
            return pd.json_normalize(payload)

        return pd.DataFrame(payload)

    if isinstance(payload, (str, int, float, bool)):
        return pd.DataFrame([payload])

    raise ValueError(
        "Unsupported JSON payload type. Expected a dict, list, or scalar."
    )


def read_json_file(file_path):
    """
    Read a JSON or NDJSON file and return a pandas DataFrame.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() in {".jsonl", ".ndjson"}:
        df = pd.read_json(file_path, lines=True)
    else:
        with open(file_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        df = normalize_json_payload(payload)

    if df.empty:
        raise ValueError(f"Input file contains no records: {file_path}")

    return df


def fetch_json_from_api(url, params=None, headers=None, timeout=30):
    """
    Fetch a JSON payload from an API and normalize it to a DataFrame.

    This keeps the project compatible with external REST APIs without
    changing the existing CSV-based ETL flow.
    """
    if not url:
        raise ValueError("API URL is required.")

    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    request_params = params or {}
    query_string = urlencode(request_params)
    request_url = f"{url}?{query_string}" if query_string else url

    request = Request(request_url, headers=request_headers, method="GET")

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
    except Exception as exc:
        raise RuntimeError(f"Unable to fetch JSON from API: {url}") from exc

    if not body:
        return pd.DataFrame()

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"API response is not valid JSON: {url}") from exc

    return normalize_json_payload(payload)


def _flatten_json_event_dataframe(json_df):
    """
    Flatten the digital-events JSON structure into a dashboard-friendly table
    while preserving the existing CSV-based ETL path untouched.
    """
    if json_df is None or json_df.empty:
        return pd.DataFrame()

    event_df = json_df.copy()

    device_columns = ["device_type", "device_os", "device_app_version", "device_browser"]
    for col in device_columns:
        event_df[col] = pd.NA

    for idx, row in event_df.iterrows():
        device = row.get("device") if isinstance(row.get("device"), dict) else {}
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

        event_df.at[idx, "device_type"] = device.get("type")
        event_df.at[idx, "device_os"] = device.get("os")
        event_df.at[idx, "device_app_version"] = device.get("app_version")
        event_df.at[idx, "device_browser"] = device.get("browser")

        for key, value in payload.items():
            event_df.at[idx, key] = value

    event_df["source"] = "json"
    event_df["event_type"] = (
        event_df["event_type"].astype(str).str.strip().str.lower()
    )
    event_df["source_system"] = (
        event_df["source_system"].astype(str).str.strip().str.lower()
    )
    event_df["environment"] = (
        event_df["environment"].astype(str).str.strip().str.lower()
    )
    event_df["event_timestamp"] = pd.to_datetime(
        event_df["event_timestamp"], errors="coerce"
    )

    event_df["reader_id"] = event_df.get("reader_id", pd.Series([pd.NA] * len(event_df), index=event_df.index))
    event_df["book_id"] = event_df.get("book_id", pd.Series([pd.NA] * len(event_df), index=event_df.index))
    event_df["branch_id"] = event_df.get("branch_id", pd.Series([pd.NA] * len(event_df), index=event_df.index))

    return event_df


def merge_csv_json_sources(csv_df, json_df):
    """
    Safely combine CSV and JSON sources into one dashboard dataset without
    forcing the JSON event objects through the legacy CSV schema validation.
    """
    if csv_df is None or csv_df.empty:
        csv_df = pd.DataFrame()
    else:
        csv_df = csv_df.copy()
        csv_df["source"] = "csv"

    if json_df is None or json_df.empty:
        json_df = pd.DataFrame()
    else:
        json_df = _flatten_json_event_dataframe(json_df)
        json_df["source"] = "json"

    if csv_df.empty and json_df.empty:
        return pd.DataFrame()

    combined_columns = list(dict.fromkeys(list(csv_df.columns) + list(json_df.columns)))

    csv_aligned = csv_df.reindex(columns=combined_columns) if not csv_df.empty else pd.DataFrame(columns=combined_columns)
    json_aligned = json_df.reindex(columns=combined_columns) if not json_df.empty else pd.DataFrame(columns=combined_columns)

    return pd.concat([csv_aligned, json_aligned], ignore_index=True, sort=False)


def load_combined_sources(csv_source=None, json_source=None):
    """
    Load both the original CSV dataset and the digital-events JSON source,
    normalize them, and return a safe summary dictionary for dashboard use.
    """
    csv_path = Path(csv_source) if csv_source else get_raw_file()
    json_path = Path(json_source) if json_source else get_json_source_file()

    csv_df = read_input_file(csv_path) if Path(csv_path).exists() else pd.DataFrame()

    if json_path.exists():
        json_df = read_input_file(json_path)
    else:
        json_df = pd.DataFrame()

    combined_df = merge_csv_json_sources(csv_df, json_df)

    event_types = []
    if not json_df.empty and "event_type" in json_df.columns:
        event_types = sorted(json_df["event_type"].dropna().astype(str).unique().tolist())

    summary = {
        "data_sources": ["csv", "json"],
        "csv_records": int(len(csv_df)) if not csv_df.empty else 0,
        "json_records": int(len(json_df)) if not json_df.empty else 0,
        "total_records": int(len(combined_df)) if not combined_df.empty else 0,
        "event_types": event_types,
        "source_systems": sorted(
            json_df["source_system"].dropna().astype(str).unique().tolist()
        ) if not json_df.empty and "source_system" in json_df.columns else [],
        "csv_columns": list(csv_df.columns) if not csv_df.empty else [],
        "json_columns": list(json_df.columns) if not json_df.empty else [],
        "combined_columns": list(combined_df.columns) if not combined_df.empty else [],
    }

    return summary


def build_combined_dashboard_payload(
    year=None,
    branch_id=None,
    genre=None,
    start_date=None,
    end_date=None,
):
    """
    Build a dashboard-ready payload that blends the original CSV dataset with the
    digital-events JSON stream after running the combined-source ETL flow.

    The structure matches the existing frontend expectation so the dashboard can
    keep its KPI/filter/chart layout while consuming both sources together.
    """
    from transformation.clean_transform import clean_combined_source_dataframe

    combined_df = clean_combined_source_dataframe()
    combined_df = limit_chart_years(combined_df, max_year=2026)

    if year is not None:
        combined_df = combined_df[combined_df["checkout_date"].dt.year == int(year)] if "checkout_date" in combined_df.columns else combined_df
    if branch_id:
        combined_df = combined_df[combined_df["branch_id"].astype(str).str.strip().str.lower() == str(branch_id).strip().lower()] if "branch_id" in combined_df.columns else combined_df
    if genre:
        combined_df = combined_df[combined_df["genre"].astype(str).str.strip().str.lower() == str(genre).strip().lower()] if "genre" in combined_df.columns else combined_df
    if start_date:
        start_dt = pd.to_datetime(start_date, errors="coerce")
        if not pd.isna(start_dt):
            combined_df = combined_df[combined_df["checkout_date"].notna() & (pd.to_datetime(combined_df["checkout_date"], errors="coerce") >= start_dt)] if "checkout_date" in combined_df.columns else combined_df
    if end_date:
        end_dt = pd.to_datetime(end_date, errors="coerce")
        if not pd.isna(end_dt):
            combined_df = combined_df[combined_df["checkout_date"].notna() & (pd.to_datetime(combined_df["checkout_date"], errors="coerce") <= end_dt)] if "checkout_date" in combined_df.columns else combined_df

    if combined_df.empty:
        return {
            "summary": {
                "total_transactions": 0,
                "total_books": 0,
                "total_readers": 0,
                "total_branches": 0,
            },
            "data_sources": {"csv": 0, "json": 0, "combined": 0},
            "trends": [],
            "status": [],
            "genres": [],
            "branches": [],
            "reader_types": [],
            "top_books": [],
            "checkout_methods": [],
            "fine_trend": [],
            "collection_health": {},
            "reservation_summary": {},
            "event_type_counts": {},
            "source_system_counts": {},
        }

    csv_df = combined_df[combined_df["source"] == "csv"].copy()
    json_df = combined_df[combined_df["source"] == "json"].copy()

    def to_int(series):
        return int(series.fillna(0).sum()) if hasattr(series, "sum") else int(series or 0)

    csv_summary = {
        "total_transactions": int(len(csv_df)),
        "total_books": int(csv_df["book_id"].nunique(dropna=True)),
        "total_readers": int(csv_df["reader_id"].nunique(dropna=True)),
        "total_branches": int(csv_df["branch_id"].nunique(dropna=True)),
    }

    summary = {
        "total_transactions": int(len(combined_df)),
        "total_books": int(combined_df["book_id"].nunique(dropna=True)),
        "total_readers": int(combined_df["reader_id"].nunique(dropna=True)),
        "total_branches": int(combined_df["branch_id"].nunique(dropna=True)),
    }

    trends_df = combined_df.dropna(subset=["checkout_date"]).copy()
    trends_df["year"] = trends_df["checkout_date"].dt.year
    trends_df["month"] = trends_df["checkout_date"].dt.month
    trends_df["month_name"] = trends_df["checkout_date"].dt.strftime("%B")
    trends = (
        trends_df.groupby(["year", "month", "month_name"], as_index=False)
        .size()
        .rename(columns={"size": "transaction_count"})
        .sort_values(["year", "month"])
        .to_dict(orient="records")
    )

    status = (
        combined_df["transaction_status"]
        .dropna()
        .astype(str)
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
        .to_dict(orient="records")
    )

    genres = (
        combined_df[combined_df["genre"].notna()]
        .groupby("genre", dropna=False)
        .size()
        .reset_index(name="transaction_count")
        .rename(columns={"genre": "genre"})
        .sort_values("transaction_count", ascending=False)
        .to_dict(orient="records")
    )

    branches = (
        combined_df[combined_df["branch_name"].notna()]
        .groupby(["branch_id", "branch_name"], dropna=False)
        .size()
        .reset_index(name="transaction_count")
        .sort_values("transaction_count", ascending=False)
        .to_dict(orient="records")
    )

    reader_types = (
        combined_df[combined_df["reader_type"].notna()]
        .groupby("reader_type", dropna=False)
        .size()
        .reset_index(name="transaction_count")
        .sort_values("transaction_count", ascending=False)
        .to_dict(orient="records")
    )

    top_books = (
        combined_df[combined_df["book_title"].notna()]
        .groupby(["book_title", "author", "genre"], dropna=False)
        .size()
        .reset_index(name="transaction_count")
        .sort_values("transaction_count", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )

    checkout_methods = (
        combined_df["checkout_method"]
        .dropna()
        .astype(str)
        .value_counts()
        .rename_axis("checkout_method")
        .reset_index(name="transaction_count")
        .to_dict(orient="records")
    )

    fine_trend_df = combined_df.dropna(subset=["checkout_date"]).copy()
    fine_trend_df["year"] = fine_trend_df["checkout_date"].dt.year
    fine_trend_df["month"] = fine_trend_df["checkout_date"].dt.month
    fine_trend_df["month_name"] = fine_trend_df["checkout_date"].dt.strftime("%b")
    fine_trend = (
        fine_trend_df.groupby(["year", "month", "month_name"], as_index=False)["fine_amount"]
        .sum()
        .rename(columns={"fine_amount": "total_fine"})
        .sort_values(["year", "month"])
        .to_dict(orient="records")
    )

    if "total_copies" in combined_df.columns and "available_copies" in combined_df.columns:
        valid_inventory = combined_df[combined_df["total_copies"].notna() & combined_df["available_copies"].notna()].copy()
        total_copies = pd.to_numeric(valid_inventory["total_copies"], errors="coerce").fillna(0)
        available_copies = pd.to_numeric(valid_inventory["available_copies"], errors="coerce").fillna(0)
        total_copies_sum = int(total_copies.sum())
        available_copies_sum = int(available_copies.sum())
        collection_health = {
            "total_copies": total_copies_sum,
            "available_copies": available_copies_sum,
            "unavailable_copies": max(0, total_copies_sum - available_copies_sum),
            "avg_available_copies": float(available_copies.mean()) if not available_copies.empty else 0.0,
            "zero_available_count": int(((available_copies == 0) & (total_copies > 0)).sum()) if not available_copies.empty else 0,
        }
    else:
        collection_health = {
            "total_copies": 0,
            "available_copies": 0,
            "unavailable_copies": 0,
            "avg_available_copies": 0.0,
            "zero_available_count": 0,
        }

    reservation_summary = {
        "total_reservations": to_int(combined_df["reservation_count"]),
        "transactions_with_reservations": int(combined_df["reservation_flag"].fillna(False).astype(bool).sum()) if "reservation_flag" in combined_df.columns else 0,
    }

    res_trend_df = combined_df.dropna(subset=["checkout_date"]).copy()
    res_trend_df["year"] = res_trend_df["checkout_date"].dt.year
    res_trend_df["month"] = res_trend_df["checkout_date"].dt.month
    res_trend_df["month_name"] = res_trend_df["checkout_date"].dt.strftime("%b")
    res_trend_df["has_res"] = res_trend_df["reservation_flag"].fillna(False).astype(bool).astype(int) if "reservation_flag" in res_trend_df.columns else 0
    res_trend_df["res_cnt"] = pd.to_numeric(res_trend_df["reservation_count"], errors="coerce").fillna(0) if "reservation_count" in res_trend_df.columns else 0

    res_trend_grouped = (
        res_trend_df.groupby(["year", "month", "month_name"], as_index=False)
        .agg(
            total_reservations=("res_cnt", "sum"),
            transactions_with_reservations=("has_res", "sum"),
            total_transactions=("res_cnt", "count"),
        )
        .sort_values(["year", "month"])
    )
    res_trend_grouped["hold_rate"] = (
        (res_trend_grouped["transactions_with_reservations"] / res_trend_grouped["total_transactions"].replace(0, 1)) * 100
    ).round(1)
    reservation_trend = res_trend_grouped.to_dict(orient="records")

    event_type_counts = (
        json_df["transaction_status"].dropna().astype(str).value_counts().sort_values(ascending=False)
    )
    source_counts = (
        json_df["checkout_method"].dropna().astype(str).value_counts().sort_values(ascending=False)
    )

    return {
        "summary": summary,
        "csv_summary": csv_summary,
        "data_sources": {
            "csv": int(len(csv_df)),
            "json": int(len(json_df)),
            "combined": int(len(combined_df)),
        },
        "trends": trends,
        "status": status,
        "genres": genres,
        "branches": branches,
        "reader_types": reader_types,
        "top_books": top_books,
        "checkout_methods": checkout_methods,
        "fine_trend": fine_trend,
        "collection_health": collection_health,
        "reservation_summary": reservation_summary,
        "reservation_trend": reservation_trend,
        "event_type_counts": event_type_counts.to_dict(),
        "source_system_counts": source_counts.to_dict(),
        "event_types": event_type_counts.index.astype(str).tolist(),
        "source_systems": source_counts.index.astype(str).tolist(),
    }


def read_input_file(file_path):
    """
    Read a supported LibraSight input file.

    Supported formats:
        CSV
        JSON
        JSONL
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

    elif extension in {".json", ".jsonl", ".ndjson"}:
        if extension in {".jsonl", ".ndjson"}:
            df = pd.read_json(file_path, lines=True)
        else:
            with open(file_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            df = normalize_json_payload(payload)

    elif extension == ".xlsx":
        df = pd.read_excel(
            file_path,
            engine="openpyxl"
        )

    else:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            "Supported formats are: .csv, .json, .jsonl, .xlsx"
        )

    if df.empty:
        raise ValueError(
            f"Input file contains no records: {file_path}"
        )

    return df