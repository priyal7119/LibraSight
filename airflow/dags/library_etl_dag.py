import sys
import subprocess
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


# --------------------------------------------------
# Add LibraSight project to Python path
# --------------------------------------------------

sys.path.insert(0, "/opt/librasight")


# --------------------------------------------------
# Import existing LibraSight functions
# --------------------------------------------------

from ingestion.ingest import ingest_data
from validation.validate import validate_data
from transformation.clean_transform import clean_transform


# --------------------------------------------------
# Project paths
# --------------------------------------------------

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


# --------------------------------------------------
# Parquet verification
# --------------------------------------------------

def save_parquet():

    print("=" * 60)
    print("LIBRASIGHT - PARQUET VERIFICATION")
    print("=" * 60)

    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {PARQUET_FILE}"
        )

    file_size = PARQUET_FILE.stat().st_size

    print(
        f"\nParquet file found:\n{PARQUET_FILE}"
    )

    print(
        f"\nFile size: {file_size} bytes"
    )

    if file_size == 0:
        raise ValueError(
            "Parquet file is empty."
        )

    print("\nParquet verification: PASS")


# --------------------------------------------------
# Run PySpark
# --------------------------------------------------

def spark_processing():

    print("=" * 60)
    print("LIBRASIGHT - AIRFLOW PYSPARK TASK")
    print("=" * 60)

    if not SPARK_JOB.exists():
        raise FileNotFoundError(
            f"Spark job not found: {SPARK_JOB}"
        )

    print(
        f"\nRunning Spark job:\n{SPARK_JOB}"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SPARK_JOB)
        ],
        capture_output=True,
        text=True
    )

    print("\n--- Spark Output ---")
    print(result.stdout)

    if result.stderr:
        print("\n--- Spark Errors/Warnings ---")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            "PySpark job failed."
        )

    print("\nPySpark task completed successfully.")


# --------------------------------------------------
# PostgreSQL placeholder
# --------------------------------------------------

def load_postgresql():
    print("=" * 60)
    print("LIBRASIGHT - POSTGRESQL LOAD")
    print("=" * 60)

    load_script = PROJECT_ROOT / "database" / "load_data.py"

    if not load_script.exists():
        raise FileNotFoundError(
            f"PostgreSQL load script not found: {load_script}"
        )

    print(f"\nRunning PostgreSQL loader:")
    print(load_script)

    result = subprocess.run(
        [sys.executable, str(load_script)],
        capture_output=True,
        text=True
    )

    print("\n--- PostgreSQL Loader Output ---")
    print(result.stdout)

    if result.stderr:
        print("\n--- PostgreSQL Errors/Warnings ---")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError("PostgreSQL loading failed.")

    print("\nPostgreSQL loading completed successfully.")


# --------------------------------------------------
# Final quality check
# --------------------------------------------------

def quality_check():

    print("=" * 60)
    print("LIBRASIGHT - FINAL DATA QUALITY CHECK")
    print("=" * 60)

    quality_file = (
        PROJECT_ROOT
        / "data"
        / "quality"
        / "data_quality_report.csv"
    )

    rejected_file = (
        PROJECT_ROOT
        / "data"
        / "quality"
        / "rejected_records.csv"
    )

    if not quality_file.exists():
        raise FileNotFoundError(
            f"Quality report not found: {quality_file}"
        )

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

    print("\nFinal quality check: PASS")

    print("\n" + "=" * 60)
    print("LIBRASIGHT PIPELINE COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# Define DAG
# --------------------------------------------------

with DAG(
    dag_id="library_etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    description="LibraSight Library ETL Pipeline",
) as dag:

    task_ingest = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_data,
    )

    task_validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    task_clean = PythonOperator(
        task_id="clean_transform",
        python_callable=clean_transform,
    )

    task_parquet = PythonOperator(
        task_id="save_parquet",
        python_callable=save_parquet,
    )

    task_spark = PythonOperator(
        task_id="spark_processing",
        python_callable=spark_processing,
    )

    task_postgresql = PythonOperator(
        task_id="load_postgresql",
        python_callable=load_postgresql,
    )

    task_quality = PythonOperator(
        task_id="quality_check",
        python_callable=quality_check,
    )

    (
        task_ingest
        >> task_validate
        >> task_clean
        >> task_parquet
        >> task_spark
        >> task_postgresql
        >> task_quality
    )