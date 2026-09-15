import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PARQUET_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "library_clean.parquet"
)

# Backwards-compatible names expected by tests and external callers
PROCESSED_PARQUET = PARQUET_FILE



# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "librasight")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

# When running directly on Windows, localhost is used to connect
# to PostgreSQL running on the Windows host.
#
# When running inside Docker/Airflow, host.docker.internal is used.
if os.name == "nt" and DATABASE_HOST == "host.docker.internal":
    DATABASE_HOST = "localhost"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a PostgreSQL database connection.
    """

    return psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )


# Compatibility alias expected by tests
def connect_database():
    return get_connection()


# ============================================================
# LOAD CLEAN PARQUET
# ============================================================

def load_parquet():
    """
    Load the cleaned library dataset.
    """

    print("=" * 70)
    print("LIBRASIGHT DATA WAREHOUSE LOADER")
    print("=" * 70)

    print("\nReading cleaned Parquet:")
    print(PARQUET_FILE)

    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Clean Parquet file not found: {PARQUET_FILE}"
        )

    df = pd.read_parquet(PARQUET_FILE)

    print(f"Parquet loaded successfully.")
    print(f"Total records: {len(df)}")

    return df


# Compatibility alias expected by tests
def load_library_data():
    """
    Backwards-compatible wrapper that returns the cleaned library dataframe.
    """
    return load_parquet()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Convert pandas NaN/NaT values to Python None.
    PostgreSQL understands None as SQL NULL.
    """

    if pd.isna(value):
        return None

    return value


def convert_date_column(df, column):
    """
    Convert a column into pandas datetime.
    """

    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    return df


# ============================================================
# DIM_DATE
# ============================================================

def load_dim_date(cursor, df):
    """
    Create and load dim_date using unique checkout dates.
    """

    print("\n[1/5] Loading dim_date...")

    date_df = df[["checkout_date"]].copy()

    date_df["checkout_date"] = pd.to_datetime(
        date_df["checkout_date"],
        errors="coerce"
    )

    date_df = date_df.dropna(
        subset=["checkout_date"]
    )

    date_df["full_date"] = (
        date_df["checkout_date"]
        .dt.date
    )

    date_df = date_df.drop_duplicates(
        subset=["full_date"]
    )

    date_df["date_key"] = date_df["checkout_date"].dt.strftime(
        "%Y%m%d"
    ).astype(int)

    date_df["day"] = (
        date_df["checkout_date"].dt.day
    )

    date_df["month"] = (
        date_df["checkout_date"].dt.month
    )

    date_df["month_name"] = (
        date_df["checkout_date"].dt.month_name()
    )

    date_df["quarter"] = (
        date_df["checkout_date"].dt.quarter
    )

    date_df["year"] = (
        date_df["checkout_date"].dt.year
    )

    # Clear existing dimension data
    cursor.execute(
        "TRUNCATE TABLE dim_date CASCADE;"
    )

    query = """
        INSERT INTO dim_date (
            date_key,
            full_date,
            day,
            month,
            month_name,
            quarter,
            year
        )
        VALUES %s
    """

    values = [
        (
            int(row.date_key),
            row.full_date,
            int(row.day),
            int(row.month),
            row.month_name,
            int(row.quarter),
            int(row.year)
        )
        for row in date_df.itertuples()
    ]

    if values:
        execute_values(
            cursor,
            query,
            values
        )

    print(
        f"dim_date loaded: {len(values)} records"
    )


# ============================================================
# DIM_READER
# ============================================================

def load_dim_reader(cursor, df):
    """
    Create and load dim_reader.
    One dimension record per reader_id.
    """

    print("\n[2/5] Loading dim_reader...")

    reader_columns = [
        "reader_id",
        "reader_name",
        "age",
        "gender",
        "reader_type",
        "membership_date",
        "home_branch_id"
    ]

    reader_df = df[reader_columns].copy()

    reader_df = reader_df.drop_duplicates(
        subset=["reader_id"]
    )

    reader_df = reader_df.sort_values(
        by="reader_id"
    )

    cursor.execute(
        "TRUNCATE TABLE dim_reader CASCADE;"
    )

    query = """
        INSERT INTO dim_reader (
            reader_id,
            reader_name,
            age,
            gender,
            reader_type,
            membership_date,
            home_branch_id
        )
        VALUES %s
        RETURNING reader_key, reader_id
    """

    values = []

    for row in reader_df.itertuples(index=False):

        values.append(
            (
                clean_value(row.reader_id),
                clean_value(row.reader_name),
                clean_value(row.age),
                clean_value(row.gender),
                clean_value(row.reader_type),
                clean_value(row.membership_date),
                clean_value(row.home_branch_id)
            )
        )

    if values:
        execute_values(
            cursor,
            query,
            values
        )

    print(
        f"dim_reader loaded: {len(values)} records"
    )


# ============================================================
# DIM_BOOK
# ============================================================

def load_dim_book(cursor, df):
    """
    Create and load dim_book.
    One dimension record per book_id.
    """

    print("\n[3/5] Loading dim_book...")

    book_columns = [
        "book_id",
        "isbn",
        "book_title",
        "author",
        "genre",
        "publication_year",
        "language",
        "format",
        "publisher"
    ]

    book_df = df[book_columns].copy()

    book_df = book_df.drop_duplicates(
        subset=["book_id"]
    )

    book_df = book_df.sort_values(
        by="book_id"
    )

    cursor.execute(
        "TRUNCATE TABLE dim_book CASCADE;"
    )

    query = """
        INSERT INTO dim_book (
            book_id,
            isbn,
            book_title,
            author,
            genre,
            publication_year,
            language,
            format,
            publisher
        )
        VALUES %s
    """

    values = []

    for row in book_df.itertuples(index=False):

        values.append(
            (
                clean_value(row.book_id),
                clean_value(row.isbn),
                clean_value(row.book_title),
                clean_value(row.author),
                clean_value(row.genre),
                clean_value(row.publication_year),
                clean_value(row.language),
                clean_value(row.format),
                clean_value(row.publisher)
            )
        )

    if values:
        execute_values(
            cursor,
            query,
            values
        )

    print(
        f"dim_book loaded: {len(values)} records"
    )


# ============================================================
# DIM_BRANCH
# ============================================================

def load_dim_branch(cursor, df):
    """
    Create and load dim_branch.
    One dimension record per branch_id.
    """

    print("\n[4/5] Loading dim_branch...")

    branch_columns = [
        "branch_id",
        "branch_name",
        "city",
        "area",
        "library_type",
        "branch_capacity"
    ]

    branch_df = df[branch_columns].copy()

    branch_df = branch_df.drop_duplicates(
        subset=["branch_id"]
    )

    branch_df = branch_df.sort_values(
        by="branch_id"
    )

    cursor.execute(
        "TRUNCATE TABLE dim_branch CASCADE;"
    )

    query = """
        INSERT INTO dim_branch (
            branch_id,
            branch_name,
            city,
            area,
            library_type,
            branch_capacity
        )
        VALUES %s
    """

    values = []

    for row in branch_df.itertuples(index=False):

        values.append(
            (
                clean_value(row.branch_id),
                clean_value(row.branch_name),
                clean_value(row.city),
                clean_value(row.area),
                clean_value(row.library_type),
                clean_value(row.branch_capacity)
            )
        )

    if values:
        execute_values(
            cursor,
            query,
            values
        )

    print(
        f"dim_branch loaded: {len(values)} records"
    )


# ============================================================
# LOAD FACT TABLE
# ============================================================

def load_fact_library_transaction(cursor, df):
    """
    Load the central fact table.

    Natural/business identifiers from the cleaned dataset
    are converted into surrogate dimension keys.
    """

    print(
        "\n[5/5] Loading fact_library_transaction..."
    )

    # --------------------------------------------------------
    # Read surrogate keys from dimensions
    # --------------------------------------------------------

    cursor.execute("""
        SELECT reader_key, reader_id
        FROM dim_reader
    """)

    reader_lookup = {
        row[1]: row[0]
        for row in cursor.fetchall()
    }

    cursor.execute("""
        SELECT book_key, book_id
        FROM dim_book
    """)

    book_lookup = {
        row[1]: row[0]
        for row in cursor.fetchall()
    }

    cursor.execute("""
        SELECT branch_key, branch_id
        FROM dim_branch
    """)

    branch_lookup = {
        row[1]: row[0]
        for row in cursor.fetchall()
    }

    cursor.execute("""
        SELECT date_key, full_date
        FROM dim_date
    """)

    date_lookup = {
        row[1]: row[0]
        for row in cursor.fetchall()
    }

    # --------------------------------------------------------
    # Clear fact table
    # --------------------------------------------------------

    cursor.execute(
        "TRUNCATE TABLE fact_library_transaction;"
    )

    # --------------------------------------------------------
    # Prepare fact records
    # --------------------------------------------------------

    values = []

    for row in df.itertuples(index=False):

        reader_key = reader_lookup.get(
            row.reader_id
        )

        book_key = book_lookup.get(
            row.book_id
        )

        branch_key = branch_lookup.get(
            row.branch_id
        )

        checkout_timestamp = pd.to_datetime(
            row.checkout_date,
            errors="coerce"
        )

        checkout_date = (
            checkout_timestamp.date()
            if not pd.isna(checkout_timestamp)
            else None
        )

        date_key = date_lookup.get(
            checkout_date
        )

        if reader_key is None:
            raise ValueError(
                f"Reader ID not found in dim_reader: "
                f"{row.reader_id}"
            )

        if book_key is None:
            raise ValueError(
                f"Book ID not found in dim_book: "
                f"{row.book_id}"
            )

        if branch_key is None:
            raise ValueError(
                f"Branch ID not found in dim_branch: "
                f"{row.branch_id}"
            )

        if date_key is None:
            raise ValueError(
                f"Checkout date not found in dim_date: "
                f"{checkout_date}"
            )

        due_timestamp = pd.to_datetime(
            row.due_date,
            errors="coerce"
        )

        return_timestamp = pd.to_datetime(
            row.return_date,
            errors="coerce"
        )

        due_date = (
            due_timestamp.date()
            if not pd.isna(due_timestamp)
            else None
        )

        return_date = (
            return_timestamp.date()
            if not pd.isna(return_timestamp)
            else None
        )

        values.append(
            (
                clean_value(row.transaction_id),
                reader_key,
                book_key,
                branch_key,
                date_key,
                checkout_date,
                due_date,
                return_date,
                clean_value(row.transaction_status),
                clean_value(row.renewal_count),
                clean_value(row.reservation_flag),
                clean_value(row.reservation_count),
                clean_value(row.checkout_method),
                clean_value(row.fine_amount),
                clean_value(row.total_copies),
                clean_value(row.available_copies)
            )
        )

    # --------------------------------------------------------
    # Insert facts
    # --------------------------------------------------------

    query = """
        INSERT INTO fact_library_transaction (
            transaction_id,
            reader_key,
            book_key,
            branch_key,
            date_key,
            checkout_date,
            due_date,
            return_date,
            transaction_status,
            renewal_count,
            reservation_flag,
            reservation_count,
            checkout_method,
            fine_amount,
            total_copies,
            available_copies
        )
        VALUES %s
    """

    if values:
        execute_values(
            cursor,
            query,
            values
        )

    print(
        "fact_library_transaction loaded: "
        f"{len(values)} records"
    )


# ============================================================
# VERIFY WAREHOUSE
# ============================================================

def verify_warehouse(cursor):
    """
    Verify final warehouse row counts.
    """

    print("\n" + "=" * 70)
    print("WAREHOUSE VERIFICATION")
    print("=" * 70)

    tables = [
        "dim_date",
        "dim_reader",
        "dim_book",
        "dim_branch",
        "fact_library_transaction"
    ]

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(
            f"{table:<35} {count:>6}"
        )

    # --------------------------------------------------------
    # Verify fact uniqueness
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_library_transaction
    """)

    total_fact = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT transaction_id)
        FROM fact_library_transaction
    """)

    unique_transactions = cursor.fetchone()[0]

    print("\nFact table checks:")
    print(
        f"Total fact rows:          {total_fact}"
    )
    print(
        f"Unique transactions:      {unique_transactions}"
    )

    if total_fact != unique_transactions:
        raise ValueError(
            "Duplicate transaction IDs detected "
            "in fact_library_transaction."
        )

    # --------------------------------------------------------
    # Verify duplicate transaction IDs
    # --------------------------------------------------------

    cursor.execute("""
        SELECT transaction_id, COUNT(*)
        FROM fact_library_transaction
        GROUP BY transaction_id
        HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    if duplicates:
        raise ValueError(
            f"Duplicate transactions found: {duplicates}"
        )

    print(
        "Duplicate transaction check: PASS"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_parquet()

    connection = None
    cursor = None

    try:

        print("\nConnecting to PostgreSQL...")

        connection = get_connection()
        cursor = connection.cursor()

        print("PostgreSQL connection successful.")

        # ----------------------------------------------------
        # Load dimensions in dependency order
        # ----------------------------------------------------

        load_dim_date(
            cursor,
            df
        )

        load_dim_reader(
            cursor,
            df
        )

        load_dim_book(
            cursor,
            df
        )

        load_dim_branch(
            cursor,
            df
        )

        # ----------------------------------------------------
        # Load fact table last
        # ----------------------------------------------------

        load_fact_library_transaction(
            cursor,
            df
        )

        # ----------------------------------------------------
        # Verify
        # ----------------------------------------------------

        verify_warehouse(
            cursor
        )

        # ----------------------------------------------------
        # Commit everything
        # ----------------------------------------------------

        connection.commit()

        print("\n" + "=" * 70)
        print(
            "DATA WAREHOUSE LOADING COMPLETED SUCCESSFULLY"
        )
        print("=" * 70)

    except Exception as error:

        if connection:
            connection.rollback()

        print("\n" + "=" * 70)
        print("DATA WAREHOUSE LOADING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

        print("\nPostgreSQL connection closed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()