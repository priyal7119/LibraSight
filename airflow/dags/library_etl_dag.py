import sys
import subprocess
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


# ============================================================
# ADD LIBRASIGHT PROJECT TO PYTHON PATH
# ============================================================

sys.path.insert(0, "/opt/librasight")


# ============================================================
# IMPORT EXISTING LIBRASIGHT FUNCTIONS
# ============================================================

from ingestion.ingest import ingest_data
from validation.validate import validate_data
from transformation.clean_transform import main as clean_transform
# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path("/opt/librasight")

PARQUET_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "library_clean.parquet"
)

SPARK_JOB = (
    PROJECT_ROOT
    / "spark"
    / "jobs"
    / "library_spark_job.py"
)

POSTGRESQL_LOADER = (
    PROJECT_ROOT
    / "database"
    / "load_data.py"
)


# ============================================================
# PARQUET VERIFICATION
# ============================================================

def save_parquet():

    print("=" * 60)
    print("LIBRASIGHT - PARQUET VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check whether Parquet file exists
    # --------------------------------------------------------

    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {PARQUET_FILE}"
        )

    # --------------------------------------------------------
    # Check file size
    # --------------------------------------------------------

    file_size = PARQUET_FILE.stat().st_size

    print(
        f"\nParquet file found:\n{PARQUET_FILE}"
    )

    print(
        f"\nFile size: {file_size} bytes"
    )

    # --------------------------------------------------------
    # Check whether file is empty
    # --------------------------------------------------------

    if file_size == 0:
        raise ValueError(
            "Parquet file is empty."
        )

    print("\nParquet verification: PASS")


# ============================================================
# RUN PYSPARK
# ============================================================

def spark_processing():

    print("=" * 60)
    print("LIBRASIGHT - AIRFLOW PYSPARK TASK")
    print("=" * 60)

    # --------------------------------------------------------
    # Check whether Spark job exists
    # --------------------------------------------------------

    if not SPARK_JOB.exists():
        raise FileNotFoundError(
            f"Spark job not found: {SPARK_JOB}"
        )

    print(
        f"\nRunning Spark job:\n{SPARK_JOB}"
    )

    # --------------------------------------------------------
    # Execute Spark job
    # --------------------------------------------------------

    result = subprocess.run(
        [
            sys.executable,
            str(SPARK_JOB)
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )

    # --------------------------------------------------------
    # Display Spark output
    # --------------------------------------------------------

    print("\n--- Spark Output ---")
    print(result.stdout)

    # --------------------------------------------------------
    # Display Spark warnings/errors
    # --------------------------------------------------------

    if result.stderr:
        print(
            "\n--- Spark Errors/Warnings ---"
        )
        print(result.stderr)

    # --------------------------------------------------------
    # Check Spark exit status
    # --------------------------------------------------------

    if result.returncode != 0:
        raise RuntimeError(
            "PySpark job failed.\n"
            f"Spark stderr:\n{result.stderr}"
        )

    print(
        "\nPySpark task completed successfully."
    )


# ============================================================
# POSTGRESQL STAR-SCHEMA WAREHOUSE LOADER
# ============================================================

def load_postgresql():

    print("=" * 60)
    print("LIBRASIGHT - POSTGRESQL STAR SCHEMA LOAD")
    print("=" * 60)

    # --------------------------------------------------------
    # Verify PostgreSQL loader exists
    # --------------------------------------------------------

    if not POSTGRESQL_LOADER.exists():
        raise FileNotFoundError(
            "PostgreSQL warehouse loader not found:\n"
            f"{POSTGRESQL_LOADER}"
        )

    print(
        "\nRunning PostgreSQL warehouse loader:"
    )

    print(
        POSTGRESQL_LOADER
    )

    # --------------------------------------------------------
    # Execute database/load_data.py
    #
    # This loader is responsible for:
    #
    # dim_date
    # dim_reader
    # dim_book
    # dim_branch
    # fact_library_transaction
    #
    # --------------------------------------------------------

    result = subprocess.run(
        [
            sys.executable,
            str(POSTGRESQL_LOADER)
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )

    # --------------------------------------------------------
    # Display loader output
    # --------------------------------------------------------

    print(
        "\n--- PostgreSQL Loader Output ---"
    )

    print(
        result.stdout
    )

    # --------------------------------------------------------
    # Display loader errors/warnings
    # --------------------------------------------------------

    if result.stderr:

        print(
            "\n--- PostgreSQL Errors/Warnings ---"
        )

        print(
            result.stderr
        )

    # --------------------------------------------------------
    # Check loader exit status
    # --------------------------------------------------------

    if result.returncode != 0:

        raise RuntimeError(
            "PostgreSQL warehouse loading failed.\n"
            f"Loader stderr:\n{result.stderr}"
        )

    print(
        "\nPostgreSQL star-schema warehouse "
        "loading completed successfully."
    )


# ============================================================
# FINAL DATA QUALITY CHECK
# ============================================================

def quality_check():

    print("=" * 60)
    print("LIBRASIGHT - FINAL DATA QUALITY CHECK")
    print("=" * 60)

    # --------------------------------------------------------
    # Quality report path
    # --------------------------------------------------------

    quality_file = (
        PROJECT_ROOT
        / "data"
        / "quality"
        / "data_quality_report.csv"
    )

    # --------------------------------------------------------
    # Rejected records path
    # --------------------------------------------------------

    rejected_file = (
        PROJECT_ROOT
        / "data"
        / "quality"
        / "rejected_records.csv"
    )

    # --------------------------------------------------------
    # Verify quality report
    # --------------------------------------------------------

    if not quality_file.exists():
        raise FileNotFoundError(
            f"Quality report not found: {quality_file}"
        )

    # --------------------------------------------------------
    # Verify rejected records file
    # --------------------------------------------------------

    if not rejected_file.exists():
        raise FileNotFoundError(
            f"Rejected records file not found: {rejected_file}"
        )

    print(
        f"\nQuality report found:\n{quality_file}"
    )

    print(
        f"\nRejected records file found:\n{rejected_file}"
    )

    print(
        "\nFinal quality check: PASS"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "LIBRASIGHT PIPELINE COMPLETED"
    )

    print(
        "=" * 60
    )


# ============================================================
# DEFINE AIRFLOW DAG
# ============================================================

with DAG(
    dag_id="library_etl_pipeline",

    start_date=datetime(
        2026,
        1,
        1
    ),

    schedule=None,

    catchup=False,

    description=(
        "LibraSight Library ETL Pipeline"
    ),

) as dag:

    # --------------------------------------------------------
    # STEP 1 — INGESTION
    # --------------------------------------------------------

    task_ingest = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_data,
    )

    # --------------------------------------------------------
    # STEP 2 — VALIDATION
    # --------------------------------------------------------

    task_validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    # --------------------------------------------------------
    # STEP 3 — CLEANING AND TRANSFORMATION
    # --------------------------------------------------------

    task_clean = PythonOperator(
        task_id="clean_transform",
        python_callable=clean_transform,
    )

    # --------------------------------------------------------
    # STEP 4 — PARQUET VERIFICATION
    # --------------------------------------------------------

    task_parquet = PythonOperator(
        task_id="save_parquet",
        python_callable=save_parquet,
    )

    # --------------------------------------------------------
    # STEP 5 — PYSPARK PROCESSING
    # --------------------------------------------------------

    task_spark = PythonOperator(
        task_id="spark_processing",
        python_callable=spark_processing,
    )

    # --------------------------------------------------------
    # STEP 6 — STAR SCHEMA POSTGRESQL LOADING
    # --------------------------------------------------------

    task_postgresql = PythonOperator(
        task_id="load_postgresql",
        python_callable=load_postgresql,
    )

    # --------------------------------------------------------
    # STEP 7 — FINAL QUALITY CHECK
    # --------------------------------------------------------

    task_quality = PythonOperator(
        task_id="quality_check",
        python_callable=quality_check,
    )

    # ========================================================
    # TASK DEPENDENCIES
    # ========================================================

    (
        task_ingest
        >> task_validate
        >> task_clean
        >> task_parquet
        >> task_spark
        >> task_postgresql
        >> task_quality
    )

