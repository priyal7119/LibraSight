# Airflow Pipeline

The Airflow DAG orchestrating the end-to-end pipeline is `airflow/dags/library_etl_dag.py`.

Task sequence (as implemented in the DAG):

```
start
   ↓
ingest_data (ingestion/ingest.py)
   ↓
validate_data (validation/validate.py)
   ↓
clean_transform (transformation/clean_transform.py)
   ↓
save_parquet (parquet verification)
   ↓
spark_processing (spark/jobs/library_spark_job.py)
   ↓
load_postgresql (database/load_data.py)
   ↓
quality_check (final data quality validation)
   ↓
end
```

Key points

- The DAG runs tasks as PythonOperator tasks calling the project functions directly (not external scripts) when possible. For Spark and the PostgreSQL loader, the DAG executes the Python scripts using `subprocess` to preserve behavior in the project environment.
- Parquet verification ensures the cleaned Parquet exists and is non-empty before running Spark.
- The final `quality_check` task verifies that `data/quality/data_quality_report.csv` and `data/quality/rejected_records.csv` exist and reports completion.

File: `airflow/dags/library_etl_dag.py`

Do not modify the DAG unless you must; it is part of the working, tested pipeline.
