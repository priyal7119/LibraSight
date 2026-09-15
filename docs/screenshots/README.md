# Screenshots Checklist

This file lists the recommended screenshots to capture for documentation and verification. The repository does not include image files; the checklist specifies filenames and what each should show.

01_airflow_dag.png
- Application: Airflow
- Show: Complete `library_etl_dag` task sequence as visible in the Airflow UI (task graph view)
- Purpose: Demonstrates pipeline orchestration and task ordering

02_airflow_successful_run.png
- Application: Airflow
- Show: DAG run details and a successful run with green task statuses and run logs
- Purpose: Evidence the pipeline completed successfully

03_postgresql_tables.png
- Application: PostgreSQL (pgAdmin / DBeaver screenshot)
- Show: `dim_date`, `dim_reader`, `dim_book`, `dim_branch`, `fact_library_transaction` with row counts
- Purpose: Demonstrates warehouse population and counts

04_swagger_api.png
- Application: FastAPI / Swagger UI
- Show: API root and the `/dashboard/summary` endpoint documentation with example response
- Purpose: API contract and interactive docs

05_react_dashboard.png
- Application: React frontend
- Show: Main dashboard page with summary metrics and charts
- Purpose: Demonstrate frontend consuming the API

06_reading_trends.png
- Application: React frontend or Power BI
- Show: Reading trends (yearly/monthly) chart
- Purpose: Visual evidence of trends analysis

07_collection.png
- Application: React frontend or backend report
- Show: Collection health / availability chart or table
- Purpose: Demonstrate collection analytics

08_data_quality.png
- Application: CSV or UI
- Show: `data/quality/data_quality_report.csv` contents or a UI view summarizing checks
- Purpose: Demonstrates validation outputs and rejected records count

09_reports.png
- Application: PDF report or backend reports page
- Show: Example generated PDF or report endpoint output
- Purpose: Evidence of reporting functionality

10_powerbi.png
- Application: Power BI Desktop
- Show: the main LibraSight PBIX dashboard (high-level visuals, filters)
- Purpose: Demonstrates BI dashboard that consumes the PostgreSQL star schema

Notes

- Do NOT fabricate screenshots. Capture real outputs from your environment when possible and place PNG files under `docs/screenshots/` using the filenames above.
