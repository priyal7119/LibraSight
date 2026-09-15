Application Architecture

This file describes the high-level application architecture and how the frontend, backend, database, BI, and reporting components interact.

Frontend

- React application located under `frontend/` (Vite-powered). The frontend fetches analytics and summary endpoints from the FastAPI backend. It runs separately (development: `localhost:5173`) and communicates with FastAPI at `http://127.0.0.1:8000`.

Backend / API

- FastAPI application located at `backend/app/` with entrypoint `backend/app/main.py`.
- Routers under `backend/app/routers/` expose endpoints such as `/dashboard/summary`, `/reports/*`, and other resource routes used by the frontend.

Database

- PostgreSQL star-schema (tables: `dim_date`, `dim_reader`, `dim_book`, `dim_branch`, `fact_library_transaction`).
- Loader script: `database/load_data.py` which reads `data/processed/library_clean.parquet` and populates dimension and fact tables.

BI & Reports

- Power BI: `powerbi/LibraSight.pbix` connects to the PostgreSQL warehouse for visualization and reporting; it is not embedded in the React app.
- PDF reports: generated via backend report endpoints and output under `reports/`.

Integration

- Airflow (`airflow/dags/library_etl_dag.py`) orchestrates ingestion → validation → transformation → parquet verification → spark processing → warehouse loading → quality check.
- The React UI and Power BI dashboards both derive analytic data from the PostgreSQL star schema; the backend provides filtered endpoints and aggregated results.
