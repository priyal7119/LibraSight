from pathlib import Path

import pandas as pd
import psycopg2


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "spark" / "output"

DB_CONFIG = {
    "host": "host.docker.internal",
    "port": 5432,
    "database": "librasight",
    "user": "postgres",
    "password": "Password123",
}

DATASETS = [
    "book_analytics",
    "branch_analytics",
    "collection_analytics",
    "genre_analytics",
    "monthly_trends",
    "reader_analytics",
    "status_analytics",
    "yearly_trends",
]


def connect_database():
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("Connected successfully.")
    return conn


def get_column_sql_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    if pd.api.types.is_float_dtype(series):
        return "DOUBLE PRECISION"
    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    return "TEXT"


def read_output_dataset(dataset_name: str):
    parquet_path = OUTPUT_DIR / dataset_name / "part-00000.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing parquet output: {parquet_path}")

    df = pd.read_parquet(parquet_path)
    df = df.copy()
    for column in df.columns:
        if pd.api.types.is_float_dtype(df[column]) and df[column].isna().any():
            df[column] = df[column].where(df[column].notna(), None)
    return df


def create_table_if_missing(conn, table_name, df):
    columns = []
    for column_name in df.columns:
        series = df[column_name]
        sql_type = get_column_sql_type(series)
        safe_name = column_name.lower()
        columns.append(f'"{safe_name}" {sql_type}')

    create_sql = (
        f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n'
        + ",\n".join(columns)
        + "\n);"
    )

    with conn.cursor() as cursor:
        cursor.execute(create_sql)
    conn.commit()


def load_dataset(conn, dataset_name):
    df = read_output_dataset(dataset_name)
    columns = list(df.columns)
    safe_columns = [str(column).lower() for column in columns]

    print(f"\nLoading {dataset_name}...")
    print(f"Columns: {columns}")

    create_table_if_missing(conn, dataset_name, df)

    rows = []
    for _, row in df.iterrows():
        values = []
        for value in row.tolist():
            if pd.isna(value):
                values.append(None)
            else:
                values.append(value)
        rows.append(tuple(values))

    if not rows:
        print(f"Loaded: 0 rows")
        return 0

    placeholders = ", ".join(["%s"] * len(safe_columns))
    quoted_columns = ", ".join(f'"{column}"' for column in safe_columns)
    insert_sql = (
        f'INSERT INTO "{dataset_name}" ({quoted_columns}) VALUES ({placeholders})'
    )

    with conn.cursor() as cursor:
        cursor.executemany(insert_sql, rows)
    conn.commit()

    print(f"Loaded: {len(rows)} rows")
    return len(rows)


def main():
    conn = connect_database()
    try:
        total_loaded = 0
        for dataset_name in DATASETS:
            total_loaded += load_dataset(conn, dataset_name)

        print(f"\nDatabase loading completed successfully.")
        print(f"Total rows loaded: {total_loaded}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()