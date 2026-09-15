"""
Database warehouse tests for LibraSight.

These tests verify that the PostgreSQL star-schema warehouse
has been loaded correctly.

IMPORTANT:
These tests DO NOT run database/load_data.py because the
loader truncates and reloads the warehouse.
"""


import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(
    PROJECT_ROOT / ".env"
)


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "librasight")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a PostgreSQL connection using the same
    environment variables used by the project.
    """

    assert DB_HOST, (
        "DATABASE_HOST is not configured."
    )

    assert DB_NAME, (
        "DATABASE_NAME is not configured."
    )

    assert DB_USER, (
        "DATABASE_USER is not configured."
    )

    assert DB_PASSWORD, (
        "DATABASE_PASSWORD is not configured."
    )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

def test_database_connection():
    """
    Verify that PostgreSQL is reachable.
    """

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT 1;"
        )

        result = cursor.fetchone()

        assert result == (1,)

        cursor.close()

    finally:

        if connection:
            connection.close()


# ============================================================
# HELPER — TABLE ROW COUNT
# ============================================================

def get_table_count(cursor, table_name):
    """
    Return the number of records in a warehouse table.
    """

    cursor.execute(
        f"SELECT COUNT(*) FROM {table_name};"
    )

    return cursor.fetchone()[0]


# ============================================================
# TEST DIM_DATE
# ============================================================

def test_dim_date_populated():
    """
    Verify that dim_date contains records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        count = get_table_count(
            cursor,
            "dim_date"
        )

        assert count > 0, (
            "dim_date is empty."
        )

    finally:

        connection.close()


# ============================================================
# TEST DIM_READER
# ============================================================

def test_dim_reader_populated():
    """
    Verify that dim_reader contains records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        count = get_table_count(
            cursor,
            "dim_reader"
        )

        assert count > 0, (
            "dim_reader is empty."
        )

    finally:

        connection.close()


# ============================================================
# TEST DIM_BOOK
# ============================================================

def test_dim_book_populated():
    """
    Verify that dim_book contains records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        count = get_table_count(
            cursor,
            "dim_book"
        )

        assert count > 0, (
            "dim_book is empty."
        )

    finally:

        connection.close()


# ============================================================
# TEST DIM_BRANCH
# ============================================================

def test_dim_branch_populated():
    """
    Verify that dim_branch contains records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        count = get_table_count(
            cursor,
            "dim_branch"
        )

        assert count > 0, (
            "dim_branch is empty."
        )

    finally:

        connection.close()


# ============================================================
# TEST FACT TABLE
# ============================================================

def test_fact_library_transaction_populated():
    """
    Verify that the central fact table contains records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        count = get_table_count(
            cursor,
            "fact_library_transaction"
        )

        assert count > 0, (
            "fact_library_transaction is empty."
        )

    finally:

        connection.close()


# ============================================================
# TEST EXPECTED TABLES
# ============================================================

def test_star_schema_tables_exist():
    """
    Verify that all five star-schema tables exist.
    """

    expected_tables = [
        "dim_date",
        "dim_reader",
        "dim_book",
        "dim_branch",
        "fact_library_transaction"
    ]

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = ANY(%s);
        """, (expected_tables,))

        existing_tables = {
            row[0]
            for row in cursor.fetchall()
        }

        missing_tables = [
            table
            for table in expected_tables
            if table not in existing_tables
        ]

        assert not missing_tables, (
            "Missing warehouse tables: "
            + ", ".join(missing_tables)
        )

    finally:

        connection.close()


# ============================================================
# TEST FACT TRANSACTION UNIQUENESS
# ============================================================

def test_fact_transaction_ids_are_unique():
    """
    Verify that transaction_id is unique in the fact table.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction;
        """)

        total_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT transaction_id)
            FROM fact_library_transaction;
        """)

        unique_count = cursor.fetchone()[0]

        assert total_count == unique_count, (
            "Duplicate transaction_id values found "
            "in fact_library_transaction."
        )

    finally:

        connection.close()


# ============================================================
# TEST FOREIGN KEY — READER
# ============================================================

def test_fact_reader_foreign_keys_are_valid():
    """
    Verify that every fact reader_key exists in dim_reader.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction f
            LEFT JOIN dim_reader r
                ON f.reader_key = r.reader_key
            WHERE r.reader_key IS NULL;
        """)

        invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0, (
            f"{invalid_count} fact records have invalid "
            "reader_key references."
        )

    finally:

        connection.close()


# ============================================================
# TEST FOREIGN KEY — BOOK
# ============================================================

def test_fact_book_foreign_keys_are_valid():
    """
    Verify that every fact book_key exists in dim_book.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction f
            LEFT JOIN dim_book b
                ON f.book_key = b.book_key
            WHERE b.book_key IS NULL;
        """)

        invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0, (
            f"{invalid_count} fact records have invalid "
            "book_key references."
        )

    finally:

        connection.close()


# ============================================================
# TEST FOREIGN KEY — BRANCH
# ============================================================

def test_fact_branch_foreign_keys_are_valid():
    """
    Verify that every fact branch_key exists in dim_branch.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction f
            LEFT JOIN dim_branch b
                ON f.branch_key = b.branch_key
            WHERE b.branch_key IS NULL;
        """)

        invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0, (
            f"{invalid_count} fact records have invalid "
            "branch_key references."
        )

    finally:

        connection.close()


# ============================================================
# TEST FOREIGN KEY — DATE
# ============================================================

def test_fact_date_foreign_keys_are_valid():
    """
    Verify that every fact date_key exists in dim_date.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction f
            LEFT JOIN dim_date d
                ON f.date_key = d.date_key
            WHERE d.date_key IS NULL;
        """)

        invalid_count = cursor.fetchone()[0]

        assert invalid_count == 0, (
            f"{invalid_count} fact records have invalid "
            "date_key references."
        )

    finally:

        connection.close()


# ============================================================
# TEST FACT TABLE RECORD COUNT
# ============================================================

def test_fact_table_has_expected_scale():
    """
    Verify that the fact table contains a substantial
    number of library transactions.

    The project currently uses a 500-record raw dataset,
    while the cleaned/loaded warehouse may contain fewer
    records after validation and transformation.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_library_transaction;
        """)

        count = cursor.fetchone()[0]

        assert count > 0

        assert count <= 500, (
            "Fact table contains more records than the "
            "500-record raw dataset."
        )

    finally:

        connection.close()