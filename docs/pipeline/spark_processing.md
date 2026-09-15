# PySpark Processing

PySpark processing is implemented in `spark/jobs/library_spark_job.py` and reads the cleaned Parquet at `data/processed/library_clean.parquet`.

Purpose

- Compute analytical aggregates used for reporting and offline analysis (book popularity, genre aggregates, reader aggregates, branch performance, collection health, yearly/monthly trends, transaction status analytics).

Inputs

- `data/processed/library_clean.parquet` (cleaned dataset)

Outputs (existing directories)

- `spark/output/book_analytics`
- `spark/output/genre_analytics`
- `spark/output/reader_analytics`
- `spark/output/branch_analytics`
- `spark/output/collection_analytics`
- `spark/output/yearly_trends`
- `spark/output/monthly_trends`
- `spark/output/status_analytics`

Processing notes

- Spark is run locally (`master("local[*]")`) in the job and uses `toPandas()` when saving analytical outputs as Parquet part files. The outputs are saved under `spark/output/`.
- The job prints schema, sample records, counts and aggregation previews to stdout for operational visibility.

Do not modify the output directories unless you have verified they are not used by other components.
